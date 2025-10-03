"""
Data models for the e-commerce domain using Pydantic for validation.
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, validator


class User(BaseModel):
    """User model representing customer data."""
    
    user_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: Optional[date] = None
    registration_date: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True)
    address: Optional[str] = None
    phone: Optional[str] = None
    
    class Config:
        json_encoders = {
            uuid.UUID: str,
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


class Product(BaseModel):
    """Product model representing catalog items."""
    
    product_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0, decimal_places=2)
    category: str = Field(..., min_length=1, max_length=100)
    brand: str = Field(..., min_length=1, max_length=100)
    sku: str = Field(..., min_length=1, max_length=50)
    stock_quantity: int = Field(default=0, ge=0)
    created_date: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True)
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return round(v, 2)
    
    class Config:
        json_encoders = {
            uuid.UUID: str,
            datetime: lambda v: v.isoformat(),
            Decimal: float
        }


class Order(BaseModel):
    """Order model representing customer purchases."""
    
    order_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID
    order_date: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="PENDING", pattern="^(PENDING|PROCESSING|SHIPPED|DELIVERED|CANCELLED)$")
    total_amount: Decimal = Field(..., gt=0, decimal_places=2)
    shipping_address: Optional[str] = None
    payment_method: Optional[str] = None
    
    @validator('total_amount')
    def validate_total_amount(cls, v):
        if v <= 0:
            raise ValueError('Total amount must be positive')
        return round(v, 2)
    
    class Config:
        json_encoders = {
            uuid.UUID: str,
            datetime: lambda v: v.isoformat(),
            Decimal: float
        }


class OrderItem(BaseModel):
    """Order item model representing individual products in an order."""
    
    order_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0, decimal_places=2)
    
    @property
    def total_price(self) -> Decimal:
        """Calculate total price for this item."""
        return self.unit_price * self.quantity
    
    class Config:
        json_encoders = {
            uuid.UUID: str,
            Decimal: float
        }


class Review(BaseModel):
    """Review model representing customer product reviews."""
    
    review_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    product_id: uuid.UUID
    user_id: uuid.UUID
    rating: int = Field(..., ge=1, le=5)
    title: str = Field(..., min_length=1, max_length=200)
    comment: Optional[str] = None
    review_date: datetime = Field(default_factory=datetime.now)
    is_verified_purchase: bool = Field(default=False)
    
    class Config:
        json_encoders = {
            uuid.UUID: str,
            datetime: lambda v: v.isoformat()
        }


class Category(BaseModel):
    """Category model for product categorization."""
    
    category_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_category_id: Optional[uuid.UUID] = None
    
    class Config:
        json_encoders = {
            uuid.UUID: str
        }


class ShoppingCartItem(BaseModel):
    """Shopping cart item model."""
    
    user_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int = Field(..., gt=0)
    added_date: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            uuid.UUID: str,
            datetime: lambda v: v.isoformat()
        }


class WishlistItem(BaseModel):
    """Wishlist item model."""
    
    user_id: uuid.UUID
    product_id: uuid.UUID
    added_date: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            uuid.UUID: str,
            datetime: lambda v: v.isoformat()
        }


# Convenience type aliases for lists
Users = List[User]
Products = List[Product]
Orders = List[Order]
OrderItems = List[OrderItem]
Reviews = List[Review]
Categories = List[Category]