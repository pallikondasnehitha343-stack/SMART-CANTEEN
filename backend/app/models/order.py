import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class OrderStatus(str, enum.Enum):
    CREATED = "CREATED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    CONFIRMED = "CONFIRMED"
    QUEUED = "QUEUED"
    ACCEPTED = "ACCEPTED"
    PREPARING = "PREPARING"
    READY = "READY"
    PICKED_UP = "PICKED_UP"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False) # e.g. ORD-20261005-001
    token_number = Column(String(20), unique=True, index=True, nullable=False) # e.g. #T-101
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pickup_slot_id = Column(Integer, ForeignKey("pickup_slots.id"), nullable=True)
    
    status = Column(Enum(OrderStatus), default=OrderStatus.CREATED, nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    
    # Live Dynamic Estimation & Pickup Fields
    estimated_prep_time_minutes = Column(Integer, default=10, nullable=False)
    estimated_ready_time = Column(DateTime, nullable=True)
    actual_ready_time = Column(DateTime, nullable=True)
    picked_up_at = Column(DateTime, nullable=True)
    
    # Cryptographic QR Pickup Token
    pickup_qr_token = Column(Text, nullable=True)
    pickup_qr_signature = Column(String(255), nullable=True)
    is_qr_used = Column(Integer, default=0, nullable=False) # 0 = unused, 1 = verified and consumed
    
    special_instructions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="orders")
    pickup_slot = relationship("PickupSlot", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False, cascade="all, delete-orphan")
    queue_entry = relationship("QueueEntry", back_populates="order", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    prep_time_snapshot = Column(Integer, default=5, nullable=False)
    complexity_snapshot = Column(Float, default=1.0, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")
