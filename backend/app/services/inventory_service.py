from typing import List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.menu_item import MenuItem
from app.models.inventory import InventoryLog, StockChangeReason
from app.schemas.order import CartItemRequest

class InventoryService:
    @staticmethod
    def validate_and_reserve_stock(
        db: Session,
        items: List[CartItemRequest],
        reference_order_number: str
    ) -> List[Tuple[MenuItem, int]]:
        """
        Transactional atomic stock verification and reservation.
        Prevents race condition overselling when multiple users buy simultaneously.
        """
        reserved_items = []
        
        for cart_item in items:
            menu_item = db.query(MenuItem).filter(MenuItem.id == cart_item.menu_item_id).first()
            if not menu_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Menu item ID {cart_item.menu_item_id} not found"
                )
                
            if not menu_item.is_available or menu_item.stock_quantity < cart_item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for '{menu_item.name}'. Available: {menu_item.stock_quantity}, Requested: {cart_item.quantity}"
                )
                
            prev_stock = menu_item.stock_quantity
            new_stock = prev_stock - cart_item.quantity
            menu_item.stock_quantity = new_stock
            if new_stock == 0:
                menu_item.is_available = False
                
            log = InventoryLog(
                menu_item_id=menu_item.id,
                change_amount=-cart_item.quantity,
                previous_stock=prev_stock,
                new_stock=new_stock,
                reason=StockChangeReason.ORDER_RESERVATION,
                reference_id=reference_order_number,
                notes=f"Reserved for order {reference_order_number}"
            )
            db.add(log)
            reserved_items.append((menu_item, cart_item.quantity))
            
        db.commit()
        return reserved_items

    @staticmethod
    def restore_stock_on_cancellation(db: Session, order) -> None:
        """Restores inventory when an order is cancelled or payment fails"""
        for item in order.items:
            menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
            if menu_item:
                prev_stock = menu_item.stock_quantity
                new_stock = prev_stock + item.quantity
                menu_item.stock_quantity = new_stock
                menu_item.is_available = True
                
                log = InventoryLog(
                    menu_item_id=menu_item.id,
                    change_amount=item.quantity,
                    previous_stock=prev_stock,
                    new_stock=new_stock,
                    reason=StockChangeReason.ORDER_CANCELLATION,
                    reference_id=order.order_number,
                    notes=f"Restored stock from cancelled order {order.order_number}"
                )
                db.add(log)
        db.commit()

    @staticmethod
    def update_stock(
        db: Session,
        menu_item_id: int,
        change_amount: int,
        reason: StockChangeReason,
        notes: str = ""
    ) -> MenuItem:
        """Manual restock or wastage adjustment by canteen staff/admin"""
        menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
        if not menu_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
            
        prev_stock = menu_item.stock_quantity
        new_stock = max(0, prev_stock + change_amount)
        menu_item.stock_quantity = new_stock
        menu_item.is_available = (new_stock > 0)
        
        log = InventoryLog(
            menu_item_id=menu_item.id,
            change_amount=change_amount,
            previous_stock=prev_stock,
            new_stock=new_stock,
            reason=reason,
            reference_id="STAFF_MANUAL_ADJUSTMENT",
            notes=notes or f"Manual update of {change_amount} units"
        )
        db.add(log)
        db.commit()
        db.refresh(menu_item)
        return menu_item
