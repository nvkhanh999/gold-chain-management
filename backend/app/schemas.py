from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    branchID: Optional[int] = None
    fullName: str
    email: str
    password: str
    role: str = "EMPLOYEE"


class UserResponse(BaseModel):
    userID: int
    branchID: Optional[int] = None
    fullName: str
    email: str
    role: str
    active: bool
    createdAt: datetime

    class Config:
        orm_mode = True


class BranchBase(BaseModel):
    code: str
    name: str
    phoneNumber: Optional[str] = None
    address: Optional[str] = None


class BranchCreate(BranchBase):
    pass


class BranchResponse(BranchBase):
    branchID: int
    active: bool
    createdAt: datetime

    class Config:
        orm_mode = True


class CustomerCreate(BaseModel):
    fullName: str
    phoneNumber: Optional[str] = None
    identityNumber: Optional[str] = None
    address: Optional[str] = None


class CustomerResponse(CustomerCreate):
    customerID: int
    branchID: int
    createdAt: datetime

    class Config:
        orm_mode = True


class GoldPriceCreate(BaseModel):
    branchID: Optional[int] = None
    goldType: str
    buyPricePerChi: Decimal
    sellPricePerChi: Decimal


class GoldPriceResponse(GoldPriceCreate):
    priceID: int
    effectiveFrom: datetime

    class Config:
        orm_mode = True


class ProductCreate(BaseModel):
    sku: str
    name: str
    category: Optional[str] = None
    goldType: str
    purity: Optional[str] = None
    weightGram: Decimal
    quantity: int = 1
    makingFee: Decimal = 0
    stoneFee: Decimal = 0
    costPrice: Decimal = 0
    note: Optional[str] = None


class ProductResponse(ProductCreate):
    productID: int
    branchID: int
    status: str
    createdAt: datetime

    class Config:
        orm_mode = True


class SaleCreate(BaseModel):
    customerID: Optional[int] = None
    productID: int
    quantity: int = 1
    discount: Decimal = 0
    paymentMethod: str = "CASH"


class SaleResponse(BaseModel):
    saleID: int
    code: str
    branchID: int
    customerID: Optional[int] = None
    productID: int
    quantity: int
    goldType: str
    weightGram: Decimal
    totalAmount: Decimal
    paymentMethod: str
    createdAt: datetime

    class Config:
        orm_mode = True


class PurchaseCreate(BaseModel):
    customerID: Optional[int] = None
    goldType: str
    weightGram: Decimal
    description: Optional[str] = None
    paymentMethod: str = "CASH"


class PurchaseResponse(BaseModel):
    purchaseID: int
    code: str
    branchID: int
    customerID: Optional[int] = None
    goldType: str
    weightGram: Decimal
    totalAmount: Decimal
    paymentMethod: str
    createdAt: datetime

    class Config:
        orm_mode = True



class OnlineOrderItemCreate(BaseModel):
    productID: int
    quantity: int = 1


class OnlineOrderCreate(BaseModel):
    branchID: int
    customerName: str
    phoneNumber: str
    address: Optional[str] = None
    note: Optional[str] = None
    items: list[OnlineOrderItemCreate]


class OnlineOrderStatusUpdate(BaseModel):
    status: str


class OnlineOrderItemResponse(BaseModel):
    onlineOrderItemID: int
    onlineOrderID: int
    productID: int
    quantity: int
    unitPrice: Decimal
    makingFee: Decimal
    stoneFee: Decimal
    totalAmount: Decimal

    class Config:
        orm_mode = True


class OnlineOrderResponse(BaseModel):
    onlineOrderID: int
    branchID: int
    customerName: str
    phoneNumber: str
    address: Optional[str] = None
    note: Optional[str] = None
    status: str
    totalAmount: Decimal
    createdAt: datetime
    updatedAt: datetime

    class Config:
        orm_mode = True
