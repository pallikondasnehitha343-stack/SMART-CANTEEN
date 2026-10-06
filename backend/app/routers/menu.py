from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.models.menu_item import MenuItem
from app.models.user import User, UserRole
from app.schemas.menu import (
    CategoryCreate, CategoryResponse, MenuItemCreate, MenuItemUpdate, MenuItemResponse
)
from app.services.auth_service import get_current_user, require_roles

router = APIRouter(prefix="/menu", tags=["Menu Management"])

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.STAFF]))
):
    existing = db.query(Category).filter(Category.name == category_in.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists")
    cat = Category(**category_in.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

@router.get("/items", response_model=List[MenuItemResponse])
def get_menu_items(
    category_id: Optional[int] = None,
    veg_only: Optional[bool] = None,
    available_only: Optional[bool] = True,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(MenuItem)
    if category_id:
        query = query.filter(MenuItem.category_id == category_id)
    if veg_only is not None:
        query = query.filter(MenuItem.is_veg == veg_only)
    if available_only:
        query = query.filter(MenuItem.is_available == True, MenuItem.stock_quantity > 0)
    if search:
        query = query.filter(MenuItem.name.ilike(f"%{search}%"))
        
    items = query.all()
    results = []
    for item in items:
        resp = MenuItemResponse.model_validate(item)
        resp.category_name = item.category.name if item.category else ""
        results.append(resp)
    return results

@router.get("/items/{item_id}", response_model=MenuItemResponse)
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    resp = MenuItemResponse.model_validate(item)
    resp.category_name = item.category.name if item.category else ""
    return resp

@router.post("/items", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_menu_item(
    item_in: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    cat = db.query(Category).filter(Category.id == item_in.category_id).first()
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    item = MenuItem(**item_in.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    resp = MenuItemResponse.model_validate(item)
    resp.category_name = cat.name
    return resp

@router.put("/items/{item_id}", response_model=MenuItemResponse)
def update_menu_item(
    item_id: int,
    item_in: MenuItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.STAFF]))
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
        
    update_data = item_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
        
    db.commit()
    db.refresh(item)
    resp = MenuItemResponse.model_validate(item)
    resp.category_name = item.category.name if item.category else ""
    return resp
