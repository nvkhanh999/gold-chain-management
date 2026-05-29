from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import database, models, oauth2, schemas, services, utils


router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/dashboard")
def getDashboard(db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireAdmin(currentUser)

    totalBranches = db.query(func.count(models.Branch.branchID)).scalar() or 0
    totalUsers = db.query(func.count(models.User.userID)).scalar() or 0
    totalProducts = db.query(func.count(models.GoldProduct.productID)).scalar() or 0
    inStockProducts = db.query(func.count(models.GoldProduct.productID)).filter(models.GoldProduct.status == "IN_STOCK").scalar() or 0
    totalSaleAmount = db.query(func.coalesce(func.sum(models.SaleOrder.totalAmount), 0)).scalar() or 0
    totalPurchaseAmount = db.query(func.coalesce(func.sum(models.PurchaseOrder.totalAmount), 0)).scalar() or 0
    stockWeightGram = (
        db.query(func.coalesce(func.sum(models.GoldProduct.weightGram * models.GoldProduct.quantity), 0))
        .filter(models.GoldProduct.status == "IN_STOCK")
        .scalar()
        or 0
    )

    branches = db.query(models.Branch).order_by(models.Branch.branchID).all()
    branchStats = []
    for branch in branches:
        saleAmount = db.query(func.coalesce(func.sum(models.SaleOrder.totalAmount), 0)).filter(models.SaleOrder.branchID == branch.branchID).scalar() or 0
        purchaseAmount = db.query(func.coalesce(func.sum(models.PurchaseOrder.totalAmount), 0)).filter(models.PurchaseOrder.branchID == branch.branchID).scalar() or 0
        stockWeight = (
            db.query(func.coalesce(func.sum(models.GoldProduct.weightGram * models.GoldProduct.quantity), 0))
            .filter(models.GoldProduct.branchID == branch.branchID, models.GoldProduct.status == "IN_STOCK")
            .scalar()
            or 0
        )
        branchStats.append(
            {
                "branchID": branch.branchID,
                "code": branch.code,
                "name": branch.name,
                "saleAmount": float(saleAmount),
                "purchaseAmount": float(purchaseAmount),
                "stockWeightGram": float(stockWeight),
            }
        )

    return {
        "totalBranches": int(totalBranches),
        "totalUsers": int(totalUsers),
        "totalProducts": int(totalProducts),
        "inStockProducts": int(inStockProducts),
        "totalSaleAmount": float(totalSaleAmount),
        "totalPurchaseAmount": float(totalPurchaseAmount),
        "stockWeightGram": float(stockWeightGram),
        "branchStats": branchStats,
    }


@router.get("/branches", response_model=list[schemas.BranchResponse])
def getBranches(db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireAdmin(currentUser)
    return db.query(models.Branch).order_by(models.Branch.branchID.desc()).all()


@router.post("/branches", response_model=schemas.BranchResponse)
def createBranch(branch: schemas.BranchCreate, db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireAdmin(currentUser)
    newBranch = models.Branch(**branch.dict())
    db.add(newBranch)
    db.commit()
    db.refresh(newBranch)
    return newBranch


@router.get("/users", response_model=list[schemas.UserResponse])
def getUsers(db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireAdmin(currentUser)
    return db.query(models.User).order_by(models.User.userID.desc()).all()


@router.post("/users", response_model=schemas.UserResponse)
def createUser(user: schemas.UserCreate, db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireAdmin(currentUser)
    newUser = models.User(
        branchID=user.branchID,
        fullName=user.fullName,
        email=user.email,
        password=utils.hashPassword(user.password),
        role=user.role,
    )
    db.add(newUser)
    db.commit()
    db.refresh(newUser)
    return newUser


@router.get("/gold-prices", response_model=list[schemas.GoldPriceResponse])
def getGoldPrices(db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireAdmin(currentUser)
    return db.query(models.GoldPriceHistory).order_by(models.GoldPriceHistory.effectiveFrom.desc()).limit(200).all()


@router.post("/gold-prices", response_model=schemas.GoldPriceResponse)
def createGoldPrice(price: schemas.GoldPriceCreate, db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireAdmin(currentUser)
    newPrice = models.GoldPriceHistory(**price.dict(), createdBy=currentUser.userID)
    db.add(newPrice)
    db.commit()
    db.refresh(newPrice)
    return newPrice


@router.get("/products", response_model=list[schemas.ProductResponse])
def getProducts(db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireAdmin(currentUser)
    return db.query(models.GoldProduct).order_by(models.GoldProduct.productID.desc()).all()


@router.get("/sales", response_model=list[schemas.SaleResponse])
def getSales(db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireAdmin(currentUser)
    return db.query(models.SaleOrder).order_by(models.SaleOrder.saleID.desc()).limit(300).all()


@router.get("/purchases", response_model=list[schemas.PurchaseResponse])
def getPurchases(db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireAdmin(currentUser)
    return db.query(models.PurchaseOrder).order_by(models.PurchaseOrder.purchaseID.desc()).limit(300).all()


@router.get("/inventory")
def getInventory(db: Session = Depends(database.getDatabase), currentUser: models.User = Depends(oauth2.getCurrentUser)):
    services.requireAdmin(currentUser)
    rows = db.query(models.InventoryMovement).order_by(models.InventoryMovement.movementID.desc()).limit(300).all()
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
    services.requireAdmin(currentUser)
    orders = db.query(models.OnlineOrder).order_by(models.OnlineOrder.onlineOrderID.desc()).limit(300).all()

    return [
        {
            "onlineOrderID": order.onlineOrderID,
            "branchID": order.branchID,
            "customerName": order.customerName,
            "phoneNumber": order.phoneNumber,
            "address": order.address,
            "status": order.status,
            "totalAmount": float(order.totalAmount),
            "createdAt": order.createdAt,
        }
        for order in orders
    ]
