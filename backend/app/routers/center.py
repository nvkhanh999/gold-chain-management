from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import database, models, oauth2, schemas, services


router = APIRouter(prefix="/api/center", tags=["Center"])


@router.get("/dashboard")
def getDashboard(db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireCenter(currentUser)
    branchID = services.getUserBranchID(currentUser)

    branch = db.query(models.Branch).filter(models.Branch.branchID == branchID).first()
    totalCustomers = db.query(func.count(models.Customer.customerID)).filter(models.Customer.branchID == branchID).scalar() or 0
    totalProducts = db.query(func.count(models.GoldProduct.productID)).filter(models.GoldProduct.branchID == branchID).scalar() or 0
    inStockProducts = (
        db.query(func.count(models.GoldProduct.productID))
        .filter(models.GoldProduct.branchID == branchID, models.GoldProduct.status == "IN_STOCK")
        .scalar()
        or 0
    )
    totalSaleAmount = db.query(func.coalesce(func.sum(models.SaleOrder.totalAmount), 0)).filter(models.SaleOrder.branchID == branchID).scalar() or 0
    totalPurchaseAmount = db.query(func.coalesce(func.sum(models.PurchaseOrder.totalAmount), 0)).filter(models.PurchaseOrder.branchID == branchID).scalar() or 0
    stockWeightGram = (
        db.query(func.coalesce(func.sum(models.GoldProduct.weightGram * models.GoldProduct.quantity), 0))
        .filter(models.GoldProduct.branchID == branchID, models.GoldProduct.status == "IN_STOCK")
        .scalar()
        or 0
    )

    return {
        "branchID": branchID,
        "branchName": branch.name if branch else "",
        "totalCustomers": int(totalCustomers),
        "totalProducts": int(totalProducts),
        "inStockProducts": int(inStockProducts),
        "totalSaleAmount": float(totalSaleAmount),
        "totalPurchaseAmount": float(totalPurchaseAmount),
        "stockWeightGram": float(stockWeightGram),
    }


@router.get("/customers", response_model=list[schemas.CustomerResponse])
def getCustomers(db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireCenter(currentUser)
    branchID = services.getUserBranchID(currentUser)
    return db.query(models.Customer).filter(models.Customer.branchID == branchID).order_by(models.Customer.customerID.desc()).all()


@router.post("/customers", response_model=schemas.CustomerResponse)
def createCustomer(customer: schemas.CustomerCreate, db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireCenter(currentUser)
    branchID = services.getUserBranchID(currentUser)
    newCustomer = models.Customer(branchID=branchID, **customer.dict())
    db.add(newCustomer)
    db.commit()
    db.refresh(newCustomer)
    return newCustomer


@router.get("/products", response_model=list[schemas.ProductResponse])
def getProducts(db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireCenter(currentUser)
    branchID = services.getUserBranchID(currentUser)
    return db.query(models.GoldProduct).filter(models.GoldProduct.branchID == branchID).order_by(models.GoldProduct.productID.desc()).all()


@router.post("/products", response_model=schemas.ProductResponse)
def createProduct(product: schemas.ProductCreate, db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireCenter(currentUser)
    branchID = services.getUserBranchID(currentUser)

    newProduct = models.GoldProduct(branchID=branchID, **product.dict())
    db.add(newProduct)
    db.flush()

    movement = models.InventoryMovement(
        branchID=branchID,
        productID=newProduct.productID,
        movementType="IMPORT",
        quantity=newProduct.quantity,
        weightGram=newProduct.weightGram * newProduct.quantity,
        referenceType="PRODUCT",
        referenceID=newProduct.productID,
        note="Tạo sản phẩm tại cửa hàng",
        createdBy=currentUser.userID,
    )
    db.add(movement)
    db.commit()
    db.refresh(newProduct)
    return newProduct


@router.get("/gold-prices", response_model=list[schemas.GoldPriceResponse])
def getGoldPrices(db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireCenter(currentUser)
    branchID = services.getUserBranchID(currentUser)
    return (
        db.query(models.GoldPriceHistory)
        .filter((models.GoldPriceHistory.branchID == branchID) | (models.GoldPriceHistory.branchID.is_(None)))
        .order_by(models.GoldPriceHistory.effectiveFrom.desc())
        .limit(100)
        .all()
    )


@router.get("/sales", response_model=list[schemas.SaleResponse])
def getSales(db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireCenter(currentUser)
    branchID = services.getUserBranchID(currentUser)
    return db.query(models.SaleOrder).filter(models.SaleOrder.branchID == branchID).order_by(models.SaleOrder.saleID.desc()).limit(200).all()


@router.post("/sales", response_model=schemas.SaleResponse)
def createSale(sale: schemas.SaleCreate, db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireCenter(currentUser)
    branchID = services.getUserBranchID(currentUser)
    return services.createSaleOrder(db, currentUser, branchID, sale)


@router.get("/purchases", response_model=list[schemas.PurchaseResponse])
def getPurchases(db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireCenter(currentUser)
    branchID = services.getUserBranchID(currentUser)
    return db.query(models.PurchaseOrder).filter(models.PurchaseOrder.branchID == branchID).order_by(models.PurchaseOrder.purchaseID.desc()).limit(200).all()


@router.post("/purchases", response_model=schemas.PurchaseResponse)
def createPurchase(purchase: schemas.PurchaseCreate, db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireCenter(currentUser)
    branchID = services.getUserBranchID(currentUser)
    return services.createPurchaseOrder(db, currentUser, branchID, purchase)


@router.get("/inventory")
def getInventory(db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireCenter(currentUser)
    branchID = services.getUserBranchID(currentUser)
    rows = (
        db.query(models.InventoryMovement)
        .filter(models.InventoryMovement.branchID == branchID)
        .order_by(models.InventoryMovement.movementID.desc())
        .limit(200)
        .all()
    )
    return [
        {
            "movementID": item.movementID,
            "branchID": item.branchID,
            "productID": item.productID,
            "movementType": item.movementType,
            "quantity": item.quantity,
            "weightGram": float(item.weightGram),
            "referenceType": item.referenceType,
            "referenceID": item.referenceID,
            "note": item.note,
            "createdAt": item.createdAt,
        }
        for item in rows
    ]



@router.get("/online-orders")
def getOnlineOrders(db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireCenter(currentUser)
    branchID = services.getUserBranchID(currentUser)

    orders = (
        db.query(models.OnlineOrder)
        .filter(models.OnlineOrder.branchID == branchID)
        .order_by(models.OnlineOrder.onlineOrderID.desc())
        .limit(200)
        .all()
    )

    result = []
    for order in orders:
        items = (
            db.query(models.OnlineOrderItem, models.GoldProduct)
            .join(models.GoldProduct, models.GoldProduct.productID == models.OnlineOrderItem.productID)
            .filter(models.OnlineOrderItem.onlineOrderID == order.onlineOrderID)
            .all()
        )

        result.append(
            {
                "onlineOrderID": order.onlineOrderID,
                "branchID": order.branchID,
                "customerName": order.customerName,
                "phoneNumber": order.phoneNumber,
                "address": order.address,
                "note": order.note,
                "status": order.status,
                "totalAmount": float(order.totalAmount),
                "createdAt": order.createdAt,
                "items": [
                    {
                        "onlineOrderItemID": item.OnlineOrderItem.onlineOrderItemID,
                        "productID": item.OnlineOrderItem.productID,
                        "sku": item.GoldProduct.sku,
                        "productName": item.GoldProduct.name,
                        "quantity": item.OnlineOrderItem.quantity,
                        "unitPrice": float(item.OnlineOrderItem.unitPrice),
                        "totalAmount": float(item.OnlineOrderItem.totalAmount),
                    }
                    for item in items
                ],
            }
        )

    return result


@router.put("/online-orders/{onlineOrderID}/status")
def updateOnlineOrderStatus(
    onlineOrderID: int,
    data: schemas.OnlineOrderStatusUpdate,
    db: Session = Depends(database.getDatabase),
    currentUser: models.User = Depends(oauth2.getCurrentUser),
):
    services.requireCenter(currentUser)
    branchID = services.getUserBranchID(currentUser)

    allowedStatuses = {"PENDING", "CONFIRMED", "COMPLETED", "CANCELLED"}
    if data.status not in allowedStatuses:
        raise HTTPException(status_code=400, detail="Trạng thái đơn hàng không hợp lệ")

    order = (
        db.query(models.OnlineOrder)
        .filter(models.OnlineOrder.onlineOrderID == onlineOrderID, models.OnlineOrder.branchID == branchID)
        .first()
    )

    if order is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng online")

    if order.status == "COMPLETED":
        raise HTTPException(status_code=400, detail="Đơn hàng đã hoàn tất, không thể đổi trạng thái")

    if data.status == "COMPLETED":
        items = db.query(models.OnlineOrderItem).filter(models.OnlineOrderItem.onlineOrderID == onlineOrderID).all()

        for item in items:
            product = (
                db.query(models.GoldProduct)
                .filter(models.GoldProduct.productID == item.productID, models.GoldProduct.branchID == branchID)
                .first()
            )
            if product is None or product.quantity < item.quantity:
                raise HTTPException(status_code=400, detail=f"Sản phẩm {item.productID} không đủ tồn kho để hoàn tất đơn")

        for item in items:
            product = db.query(models.GoldProduct).filter(models.GoldProduct.productID == item.productID).first()
            product.quantity -= item.quantity
            if product.quantity <= 0:
                product.status = "SOLD"

            db.add(
                models.InventoryMovement(
                    branchID=branchID,
                    productID=product.productID,
                    movementType="ONLINE_SALE",
                    quantity=-item.quantity,
                    weightGram=-(product.weightGram * item.quantity),
                    referenceType="ONLINE_ORDER",
                    referenceID=onlineOrderID,
                    note=f"Hoàn tất đơn online #{onlineOrderID}",
                    createdBy=currentUser.userID,
                )
            )

    order.status = data.status
    db.commit()

    return {"message": "Cập nhật trạng thái đơn hàng thành công", "onlineOrderID": order.onlineOrderID, "status": order.status}
