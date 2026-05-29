from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import database, models, schemas, services


router = APIRouter(prefix="/api/shop", tags=["Shop"])


def productToPublicDict(db: Session, product: models.GoldProduct):
    price = services.getLatestPrice(db, product.goldType, product.branchID)
    goldMoney = services.gramToChi(product.weightGram) * price.sellPricePerChi
    unitPrice = goldMoney + product.makingFee + product.stoneFee

    return {
        "productID": product.productID,
        "branchID": product.branchID,
        "sku": product.sku,
        "name": product.name,
        "category": product.category,
        "goldType": product.goldType,
        "purity": product.purity,
        "weightGram": float(product.weightGram),
        "quantity": product.quantity,
        "makingFee": float(product.makingFee),
        "stoneFee": float(product.stoneFee),
        "sellPricePerChi": float(price.sellPricePerChi),
        "estimatedPrice": float(unitPrice),
        "status": product.status,
        "note": product.note,
    }


@router.get("/branches")
def getBranches(db: Session = Depends(database.getDatabase)):
    rows = db.query(models.Branch).filter(models.Branch.active == True).order_by(models.Branch.branchID).all()
    return [
        {
            "branchID": item.branchID,
            "code": item.code,
            "name": item.name,
            "phoneNumber": item.phoneNumber,
            "address": item.address,
        }
        for item in rows
    ]


@router.get("/products")
def getProducts(
    branchID: int | None = None,
    keyword: str | None = None,
    goldType: str | None = None,
    db: Session = Depends(database.getDatabase),
):
    query = db.query(models.GoldProduct).filter(models.GoldProduct.status == "IN_STOCK", models.GoldProduct.quantity > 0)

    if branchID:
        query = query.filter(models.GoldProduct.branchID == branchID)

    if keyword:
        query = query.filter(
            (models.GoldProduct.name.ilike(f"%{keyword}%"))
            | (models.GoldProduct.sku.ilike(f"%{keyword}%"))
            | (models.GoldProduct.category.ilike(f"%{keyword}%"))
        )

    if goldType:
        query = query.filter(models.GoldProduct.goldType == goldType)

    products = query.order_by(models.GoldProduct.productID.desc()).all()
    return [productToPublicDict(db, product) for product in products]


@router.get("/products/{productID}")
def getProduct(productID: int, db: Session = Depends(database.getDatabase)):
    product = db.query(models.GoldProduct).filter(models.GoldProduct.productID == productID).first()
    if product is None or product.status != "IN_STOCK":
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
    return productToPublicDict(db, product)


@router.post("/orders")
def createOnlineOrder(order: schemas.OnlineOrderCreate, db: Session = Depends(database.getDatabase)):
    if not order.items:
        raise HTTPException(status_code=400, detail="Giỏ hàng không có sản phẩm")

    branch = db.query(models.Branch).filter(models.Branch.branchID == order.branchID, models.Branch.active == True).first()
    if branch is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy chi nhánh")

    totalAmount = Decimal("0")
    itemRows = []

    for item in order.items:
        if item.quantity <= 0:
            raise HTTPException(status_code=400, detail="Số lượng sản phẩm phải lớn hơn 0")

        product = (
            db.query(models.GoldProduct)
            .filter(
                models.GoldProduct.productID == item.productID,
                models.GoldProduct.branchID == order.branchID,
                models.GoldProduct.status == "IN_STOCK",
            )
            .first()
        )

        if product is None:
            raise HTTPException(status_code=400, detail=f"Sản phẩm {item.productID} không tồn tại tại chi nhánh đã chọn")

        if product.quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Sản phẩm {product.sku} không đủ số lượng tồn kho")

        price = services.getLatestPrice(db, product.goldType, order.branchID)
        goldMoney = services.gramToChi(product.weightGram) * price.sellPricePerChi
        unitPrice = goldMoney + product.makingFee + product.stoneFee
        lineTotal = unitPrice * item.quantity

        itemRows.append(
            {
                "product": product,
                "quantity": item.quantity,
                "unitPrice": unitPrice,
                "makingFee": product.makingFee,
                "stoneFee": product.stoneFee,
                "totalAmount": lineTotal,
            }
        )
        totalAmount += lineTotal

    newOrder = models.OnlineOrder(
        branchID=order.branchID,
        customerName=order.customerName,
        phoneNumber=order.phoneNumber,
        address=order.address,
        note=order.note,
        status="PENDING",
        totalAmount=totalAmount,
    )
    db.add(newOrder)
    db.flush()

    for item in itemRows:
        db.add(
            models.OnlineOrderItem(
                onlineOrderID=newOrder.onlineOrderID,
                productID=item["product"].productID,
                quantity=item["quantity"],
                unitPrice=item["unitPrice"],
                makingFee=item["makingFee"],
                stoneFee=item["stoneFee"],
                totalAmount=item["totalAmount"],
            )
        )

    db.commit()
    db.refresh(newOrder)

    return {
        "message": "Đặt hàng thành công. Cửa hàng sẽ liên hệ xác nhận đơn.",
        "onlineOrderID": newOrder.onlineOrderID,
        "status": newOrder.status,
        "totalAmount": float(newOrder.totalAmount),
    }
