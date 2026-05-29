from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models


ADMIN_ROLES = {"ADMIN", "CHAIN_MANAGER"}
CENTER_ROLES = {"BRANCH_MANAGER", "EMPLOYEE", "WAREHOUSE_STAFF"}


def isAdmin(user: models.User) -> bool:
    return user.role in ADMIN_ROLES


def requireAdmin(user: models.User):
    if not isAdmin(user):
        raise HTTPException(status_code=403, detail="Bạn không có quyền truy cập giao diện quản trị tổng chuỗi")


def requireCenter(user: models.User):
    if user.role not in ADMIN_ROLES and user.role not in CENTER_ROLES:
        raise HTTPException(status_code=403, detail="Bạn không có quyền truy cập giao diện cửa hàng")


def getUserBranchID(user: models.User) -> int:
    if user.branchID is None:
        raise HTTPException(status_code=400, detail="Tài khoản này chưa được gán chi nhánh")
    return user.branchID


def generateCode(prefix: str):
    return f"{prefix}{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"


def gramToChi(weightGram):
    return Decimal(weightGram) / Decimal("3.75")


def getLatestPrice(db: Session, goldType: str, branchID: int | None = None):
    query = db.query(models.GoldPriceHistory).filter(models.GoldPriceHistory.goldType == goldType)

    if branchID:
        price = (
            query.filter(models.GoldPriceHistory.branchID == branchID)
            .order_by(models.GoldPriceHistory.effectiveFrom.desc())
            .first()
        )
        if price:
            return price

    price = (
        query.filter(models.GoldPriceHistory.branchID.is_(None))
        .order_by(models.GoldPriceHistory.effectiveFrom.desc())
        .first()
    )

    if price is None:
        raise HTTPException(status_code=400, detail=f"Chưa có giá vàng cho loại {goldType}")

    return price


def createSaleOrder(db: Session, user: models.User, branchID: int, saleData):
    product = (
        db.query(models.GoldProduct)
        .filter(
            models.GoldProduct.productID == saleData.productID,
            models.GoldProduct.branchID == branchID,
        )
        .first()
    )

    if product is None or product.status != "IN_STOCK":
        raise HTTPException(status_code=400, detail="Sản phẩm không tồn tại hoặc không còn hàng tại chi nhánh")

    if product.quantity < saleData.quantity:
        raise HTTPException(status_code=400, detail="Số lượng tồn kho không đủ")

    price = getLatestPrice(db, product.goldType, branchID)
    weightTotal = product.weightGram * saleData.quantity
    goldMoney = gramToChi(weightTotal) * price.sellPricePerChi
    totalAmount = goldMoney + (product.makingFee * saleData.quantity) + (product.stoneFee * saleData.quantity) - saleData.discount

    order = models.SaleOrder(
        code=generateCode("BH"),
        branchID=branchID,
        customerID=saleData.customerID,
        productID=product.productID,
        quantity=saleData.quantity,
        weightGram=weightTotal,
        goldType=product.goldType,
        sellPricePerChi=price.sellPricePerChi,
        makingFee=product.makingFee,
        stoneFee=product.stoneFee,
        discount=saleData.discount,
        totalAmount=totalAmount,
        paymentMethod=saleData.paymentMethod,
        createdBy=user.userID,
    )
    db.add(order)
    db.flush()

    product.quantity -= saleData.quantity
    if product.quantity <= 0:
        product.status = "SOLD"

    movement = models.InventoryMovement(
        branchID=branchID,
        productID=product.productID,
        movementType="SALE",
        quantity=-saleData.quantity,
        weightGram=-weightTotal,
        referenceType="SALE_ORDER",
        referenceID=order.saleID,
        note=f"Bán vàng {order.code}",
        createdBy=user.userID,
    )
    db.add(movement)
    db.commit()
    db.refresh(order)
    return order


def createPurchaseOrder(db: Session, user: models.User, branchID: int, purchaseData):
    price = getLatestPrice(db, purchaseData.goldType, branchID)
    totalAmount = gramToChi(purchaseData.weightGram) * price.buyPricePerChi

    order = models.PurchaseOrder(
        code=generateCode("MV"),
        branchID=branchID,
        customerID=purchaseData.customerID,
        goldType=purchaseData.goldType,
        weightGram=purchaseData.weightGram,
        buyPricePerChi=price.buyPricePerChi,
        totalAmount=totalAmount,
        description=purchaseData.description,
        paymentMethod=purchaseData.paymentMethod,
        createdBy=user.userID,
    )
    db.add(order)
    db.flush()

    movement = models.InventoryMovement(
        branchID=branchID,
        productID=None,
        movementType="BUY_FROM_CUSTOMER",
        quantity=1,
        weightGram=purchaseData.weightGram,
        referenceType="PURCHASE_ORDER",
        referenceID=order.purchaseID,
        note=f"Mua vàng từ khách {order.code}",
        createdBy=user.userID,
    )
    db.add(movement)
    db.commit()
    db.refresh(order)
    return order
