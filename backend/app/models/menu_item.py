from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    stock_quantity = Column(Integer, default=50, nullable=False)
    prep_time_minutes = Column(Integer, default=5, nullable=False) # Base prep time
    complexity_score = Column(Float, default=1.0, nullable=False) # 1.0 = standard, 2.0 = high labor
    image_url = Column(String(255), nullable=True)
    is_veg = Column(Boolean, default=True)
    calories = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("Category", back_populates="menu_items")
    order_items = relationship("OrderItem", back_populates="menu_item")
    inventory_logs = relationship("InventoryLog", back_populates="menu_item")
