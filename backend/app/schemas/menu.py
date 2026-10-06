from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class MenuItemBase(BaseModel):
    category_id: int
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool = True
    stock_quantity: int = 50
    prep_time_minutes: int = 5
    complexity_score: float = 1.0
    image_url: Optional[str] = None
    is_veg: bool = True
    calories: Optional[int] = None

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_available: Optional[bool] = None
    stock_quantity: Optional[int] = None
    prep_time_minutes: Optional[int] = None
    complexity_score: Optional[float] = None
    image_url: Optional[str] = None
    is_veg: Optional[bool] = None
    calories: Optional[int] = None

class MenuItemResponse(MenuItemBase):
    id: int
    category_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
