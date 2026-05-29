from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.sql.expression import text

from .database import Base


class Branch(Base):
    __tablename__ = "branches"

    branchID = Column(Integer, primary_key=True, nullable=False)
    code = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    phoneNumber = Column(String, nullable=True)
    address = Column(String, nullable=True)
    active = Column(Boolean, nullable=False, server_default=text("true"))
    createdAt = Column(DateTime, nullable=False, server_default=text("now()"))


class User(Base):
    __tablename__ = "users"

    userID = Column(Integer, primary_key=True, nullable=False)
    branchID = Column(Integer, ForeignKey("branches.branchID", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    fullName = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, server_default=text("'EMPLOYEE'"))
    active = Column(Boolean, nullable=False, server_default=text("true"))
    createdAt = Column(DateTime, nullable=False, server_default=text("now()"))


class Customer(Base):
    __tablename__ = "customers"

    customerID = Column(Integer, primary_key=True, nullable=False)
    branchID = Column(Integer, ForeignKey("branches.branchID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    fullName = Column(String, nullable=False)
    phoneNumber = Column(String, nullable=True)
    identityNumber = Column(String, nullable=True)
    address = Column(String, nullable=True)
    createdAt = Column(DateTime, nullable=False, server_default=text("now()"))


class GoldProduct(Base):
    __tablename__ = "gold_products"

    productID = Column(Integer, primary_key=True, nullable=False)
    branchID = Column(Integer, ForeignKey("branches.branchID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    sku = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    goldType = Column(String, nullable=False)
    purity = Column(String, nullable=True)
    weightGram = Column(Numeric(12, 3), nullable=False, server_default=text("0"))
    quantity = Column(Integer, nullable=False, server_default=text("1"))
    makingFee = Column(Numeric(15, 2), nullable=False, server_default=text("0"))
    stoneFee = Column(Numeric(15, 2), nullable=False, server_default=text("0"))
    costPrice = Column(Numeric(15, 2), nullable=False, server_default=text("0"))
    status = Column(String, nullable=False, server_default=text("'IN_STOCK'"))
    note = Column(Text, nullable=True)
    createdAt = Column(DateTime, nullable=False, server_default=text("now()"))


class GoldPriceHistory(Base):
    __tablename__ = "gold_price_histories"

    priceID = Column(Integer, primary_key=True, nullable=False)
    branchID = Column(Integer, ForeignKey("branches.branchID", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    goldType = Column(String, nullable=False)
    buyPricePerChi = Column(Numeric(15, 2), nullable=False)
    sellPricePerChi = Column(Numeric(15, 2), nullable=False)
    createdBy = Column(Integer, ForeignKey("users.userID", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    effectiveFrom = Column(DateTime, nullable=False, server_default=text("now()"))


class SaleOrder(Base):
    __tablename__ = "sale_orders"

    saleID = Column(Integer, primary_key=True, nullable=False)
    code = Column(String, nullable=False, unique=True)
    branchID = Column(Integer, ForeignKey("branches.branchID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    customerID = Column(Integer, ForeignKey("customers.customerID", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    productID = Column(Integer, ForeignKey("gold_products.productID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    quantity = Column(Integer, nullable=False, server_default=text("1"))
    weightGram = Column(Numeric(12, 3), nullable=False)
    goldType = Column(String, nullable=False)
    sellPricePerChi = Column(Numeric(15, 2), nullable=False)
    makingFee = Column(Numeric(15, 2), nullable=False, server_default=text("0"))
    stoneFee = Column(Numeric(15, 2), nullable=False, server_default=text("0"))
    discount = Column(Numeric(15, 2), nullable=False, server_default=text("0"))
    totalAmount = Column(Numeric(15, 2), nullable=False)
    paymentMethod = Column(String, nullable=False, server_default=text("'CASH'"))
    createdBy = Column(Integer, ForeignKey("users.userID", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    createdAt = Column(DateTime, nullable=False, server_default=text("now()"))


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    purchaseID = Column(Integer, primary_key=True, nullable=False)
    code = Column(String, nullable=False, unique=True)
    branchID = Column(Integer, ForeignKey("branches.branchID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    customerID = Column(Integer, ForeignKey("customers.customerID", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)

    goldType = Column(String, nullable=False)
    weightGram = Column(Numeric(12, 3), nullable=False)
    buyPricePerChi = Column(Numeric(15, 2), nullable=False)
    totalAmount = Column(Numeric(15, 2), nullable=False)
    description = Column(Text, nullable=True)
    paymentMethod = Column(String, nullable=False, server_default=text("'CASH'"))
    createdBy = Column(Integer, ForeignKey("users.userID", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    createdAt = Column(DateTime, nullable=False, server_default=text("now()"))


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    movementID = Column(Integer, primary_key=True, nullable=False)
    branchID = Column(Integer, ForeignKey("branches.branchID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    productID = Column(Integer, ForeignKey("gold_products.productID", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)

    movementType = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, server_default=text("0"))
    weightGram = Column(Numeric(12, 3), nullable=False, server_default=text("0"))
    referenceType = Column(String, nullable=True)
    referenceID = Column(Integer, nullable=True)
    note = Column(Text, nullable=True)
    createdBy = Column(Integer, ForeignKey("users.userID", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    createdAt = Column(DateTime, nullable=False, server_default=text("now()"))



class OnlineOrder(Base):
    __tablename__ = "online_orders"

    onlineOrderID = Column(Integer, primary_key=True, nullable=False)
    branchID = Column(Integer, ForeignKey("branches.branchID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    customerName = Column(String, nullable=False)
    phoneNumber = Column(String, nullable=False)
    address = Column(String, nullable=True)
    note = Column(Text, nullable=True)
    status = Column(String, nullable=False, server_default=text("'PENDING'"))
    totalAmount = Column(Numeric(15, 2), nullable=False, server_default=text("0"))
    createdAt = Column(DateTime, nullable=False, server_default=text("now()"))
    updatedAt = Column(DateTime, nullable=False, server_default=text("now()"))


class OnlineOrderItem(Base):
    __tablename__ = "online_order_items"

    onlineOrderItemID = Column(Integer, primary_key=True, nullable=False)
    onlineOrderID = Column(Integer, ForeignKey("online_orders.onlineOrderID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    productID = Column(Integer, ForeignKey("gold_products.productID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    quantity = Column(Integer, nullable=False, server_default=text("1"))
    unitPrice = Column(Numeric(15, 2), nullable=False)
    makingFee = Column(Numeric(15, 2), nullable=False, server_default=text("0"))
    stoneFee = Column(Numeric(15, 2), nullable=False, server_default=text("0"))
    totalAmount = Column(Numeric(15, 2), nullable=False)
