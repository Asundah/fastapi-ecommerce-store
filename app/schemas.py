from pydantic import BaseModel
from typing import List

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    image_url: str
    stock: int
    class Config: 
        from_attributes = True

class CartItemAdd(BaseModel):
    product_id: int

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    name: str
    price: float
    image_url: str
    total: float

class CartResponse(BaseModel):
    items: List[CartItemResponse]
    cart_total: float

class CheckoutRequest(BaseModel):
    phone_number: str