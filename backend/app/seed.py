from decimal import Decimal

from . import models
from .database import SessionLocal, engine
from .utils import hashPassword


def create_user_if_missing(db, branchID, fullName, email, password, role):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        user = models.User(
            branchID=branchID,
            fullName=fullName,
            email=email,
            password=hashPassword(password),
            role=role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def seed():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        hn = db.query(models.Branch).filter(models.Branch.code == "HN001").first()
        if hn is None:
            hn = models.Branch(
                code="HN001",
                name="Chi nhánh Hà Nội",
                phoneNumber="0900000001",
                address="Cầu Giấy, Hà Nội",
            )
            db.add(hn)
            db.commit()
            db.refresh(hn)

        hcm = db.query(models.Branch).filter(models.Branch.code == "HCM001").first()
        if hcm is None:
            hcm = models.Branch(
                code="HCM001",
                name="Chi nhánh Hồ Chí Minh",
                phoneNumber="0900000002",
                address="Quận 1, TP. Hồ Chí Minh",
            )
            db.add(hcm)
            db.commit()
            db.refresh(hcm)

        admin_user = create_user_if_missing(db, None, "Quản trị tổng chuỗi", "admin@gold.local", "123456", "ADMIN")
        create_user_if_missing(db, hn.branchID, "Quản lý chi nhánh Hà Nội", "manager.hn@gold.local", "123456", "BRANCH_MANAGER")
        create_user_if_missing(db, hn.branchID, "Nhân viên bán hàng Hà Nội", "employee.hn@gold.local", "123456", "EMPLOYEE")
        create_user_if_missing(db, hcm.branchID, "Quản lý chi nhánh Hồ Chí Minh", "manager.hcm@gold.local", "123456", "BRANCH_MANAGER")

        if db.query(models.GoldPriceHistory).count() == 0:
            db.add_all(
                [
                    models.GoldPriceHistory(branchID=None, goldType="9999", buyPricePerChi=Decimal("8500000"), sellPricePerChi=Decimal("8650000"), createdBy=admin_user.userID),
                    models.GoldPriceHistory(branchID=None, goldType="24K", buyPricePerChi=Decimal("8400000"), sellPricePerChi=Decimal("8600000"), createdBy=admin_user.userID),
                    models.GoldPriceHistory(branchID=None, goldType="18K", buyPricePerChi=Decimal("5800000"), sellPricePerChi=Decimal("6100000"), createdBy=admin_user.userID),
                    models.GoldPriceHistory(branchID=None, goldType="14K", buyPricePerChi=Decimal("4300000"), sellPricePerChi=Decimal("4700000"), createdBy=admin_user.userID),
                ]
            )
            db.commit()

        if db.query(models.Customer).count() == 0:
            db.add_all(
                [
                    models.Customer(branchID=hn.branchID, fullName="Nguyễn Văn An", phoneNumber="0912345678", identityNumber="001200000001", address="Hà Nội"),
                    models.Customer(branchID=hn.branchID, fullName="Trần Thị Bình", phoneNumber="0987654321", identityNumber="001200000002", address="Hà Nội"),
                    models.Customer(branchID=hcm.branchID, fullName="Lê Văn Cường", phoneNumber="0909123456", identityNumber="079200000001", address="TP. Hồ Chí Minh"),
                ]
            )
            db.commit()

        if db.query(models.GoldProduct).count() == 0:
            products = [
                models.GoldProduct(
                    branchID=hn.branchID,
                    sku="HN-NV9999-001",
                    name="Nhẫn vàng 9999 trơn",
                    category="Nhẫn",
                    goldType="9999",
                    purity="99.99%",
                    weightGram=Decimal("3.750"),
                    quantity=4,
                    makingFee=Decimal("300000"),
                    stoneFee=Decimal("0"),
                    costPrice=Decimal("8400000"),
                    status="IN_STOCK",
                ),
                models.GoldProduct(
                    branchID=hn.branchID,
                    sku="HN-DC18K-001",
                    name="Dây chuyền vàng 18K",
                    category="Dây chuyền",
                    goldType="18K",
                    purity="75%",
                    weightGram=Decimal("7.500"),
                    quantity=2,
                    makingFee=Decimal("700000"),
                    stoneFee=Decimal("0"),
                    costPrice=Decimal("11000000"),
                    status="IN_STOCK",
                ),
                models.GoldProduct(
                    branchID=hcm.branchID,
                    sku="HCM-LT24K-001",
                    name="Lắc tay vàng 24K",
                    category="Lắc tay",
                    goldType="24K",
                    purity="99.9%",
                    weightGram=Decimal("11.250"),
                    quantity=2,
                    makingFee=Decimal("900000"),
                    stoneFee=Decimal("0"),
                    costPrice=Decimal("25000000"),
                    status="IN_STOCK",
                ),
            ]
            db.add_all(products)
            db.flush()

            for product in products:
                db.add(
                    models.InventoryMovement(
                        branchID=product.branchID,
                        productID=product.productID,
                        movementType="IMPORT",
                        quantity=product.quantity,
                        weightGram=product.weightGram * product.quantity,
                        referenceType="SEED",
                        referenceID=product.productID,
                        note="Dữ liệu mẫu ban đầu",
                        createdBy=admin_user.userID,
                    )
                )
            db.commit()

        print("Seed dữ liệu mẫu thành công.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
