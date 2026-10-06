from datetime import datetime, time, timedelta
from sqlalchemy.orm import Session

from app.database import engine, Base, SessionLocal
from app.models.user import User, UserRole
from app.models.category import Category
from app.models.menu_item import MenuItem
from app.models.pickup_slot import PickupSlot, SlotStatus
from app.models.order import Order, OrderItem, OrderStatus
from app.models.queue import QueueEntry
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.inventory import InventoryLog, StockChangeReason
from app.models.analytics import BottleneckEvent
from app.services.auth_service import hash_password
from app.services.qr_service import QRVerificationService

def seed_database(db: Session):
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    # Check if already seeded
    if db.query(User).first():
        print("Database already seeded. Skipping initial population.")
        return

    print("Seeding Smart Canteen Database with Campus Demo Data...")

    # 1. Users
    student = User(
        campus_id="STU-2024-001",
        full_name="Aarav Sharma",
        email="student@campus.edu",
        hashed_password=hash_password("campus123"),
        role=UserRole.STUDENT,
        phone="+91 98765 43210"
    )
    student2 = User(
        campus_id="STU-2024-042",
        full_name="Priya Patel",
        email="priya@campus.edu",
        hashed_password=hash_password("campus123"),
        role=UserRole.STUDENT,
        phone="+91 98765 43211"
    )
    staff = User(
        campus_id="STF-KITCHEN-01",
        full_name="Chef Ramesh Kumar",
        email="staff@campus.edu",
        hashed_password=hash_password("staff123"),
        role=UserRole.STAFF,
        phone="+91 98765 43220"
    )
    admin = User(
        campus_id="ADM-DIR-001",
        full_name="Dr. Sunita Rao",
        email="admin@campus.edu",
        hashed_password=hash_password("admin123"),
        role=UserRole.ADMIN,
        phone="+91 98765 43230"
    )
    db.add_all([student, student2, staff, admin])
    db.commit()

    # 2. Categories
    cat_breakfast = Category(name="Breakfast & South Indian", description="Fresh hot morning snacks and tiffins", icon="Utensils")
    cat_lunch = Category(name="Lunch & Thalis", description="Nutritious meals, thalis, and bowls", icon="Soup")
    cat_snacks = Category(name="Snacks & Quick Bites", description="Crispy samosas, sandwiches, rolls and puffs", icon="Sandwich")
    cat_beverages = Category(name="Beverages & Juices", description="Hot filter coffee, chai, cold drinks and juices", icon="Coffee")
    db.add_all([cat_breakfast, cat_lunch, cat_snacks, cat_beverages])
    db.commit()

    # 3. Menu Items
    menu_items = [
        # Breakfast
        MenuItem(
            category_id=cat_breakfast.id,
            name="Masala Dosa with Sambar",
            description="Crispy golden rice crepe filled with spiced potato masala, served with fresh coconut chutney & piping hot sambar.",
            price=60.0,
            prep_time_minutes=6,
            complexity_score=1.2,
            stock_quantity=45,
            is_veg=True,
            calories=320
        ),
        MenuItem(
            category_id=cat_breakfast.id,
            name="Idli Vada Combo (2 Idli + 1 Vada)",
            description="Steamed fluffy rice cakes paired with crispy medu vada and spicy lentil sambar.",
            price=50.0,
            prep_time_minutes=4,
            complexity_score=0.8,
            stock_quantity=60,
            is_veg=True,
            calories=280
        ),
        MenuItem(
            category_id=cat_breakfast.id,
            name="Poha with Roasted Peanuts & Sev",
            description="Flattened rice tempered with mustard seeds, curry leaves, turmeric and crunchy peanuts.",
            price=35.0,
            prep_time_minutes=3,
            complexity_score=0.6,
            stock_quantity=40,
            is_veg=True,
            calories=220
        ),
        MenuItem(
            category_id=cat_breakfast.id,
            name="Chole Bhature (2 pcs)",
            description="Fluffy deep-fried bhature served with rich, aromatic Punjabi chickpea curry and pickled onions.",
            price=80.0,
            prep_time_minutes=8,
            complexity_score=1.5,
            stock_quantity=30,
            is_veg=True,
            calories=550
        ),
        # Lunch
        MenuItem(
            category_id=cat_lunch.id,
            name="Special Executive Veg Thali",
            description="Paneer butter masala, dal tadka, 2 butter rotis, jeera rice, gulab jamun, salad and papad.",
            price=120.0,
            prep_time_minutes=7,
            complexity_score=1.4,
            stock_quantity=50,
            is_veg=True,
            calories=680
        ),
        MenuItem(
            category_id=cat_lunch.id,
            name="Hyderabadi Veg Dum Biryani",
            description="Fragrant basmati rice layered with marinated vegetables, saffron and herbs, served with raita & salan.",
            price=110.0,
            prep_time_minutes=5,
            complexity_score=1.1,
            stock_quantity=35,
            is_veg=True,
            calories=520
        ),
        MenuItem(
            category_id=cat_lunch.id,
            name="Paneer Butter Masala with 3 Rotis",
            description="Cottage cheese cubes in rich cashew-tomato gravy served with warm whole wheat rotis.",
            price=100.0,
            prep_time_minutes=6,
            complexity_score=1.3,
            stock_quantity=25,
            is_veg=True,
            calories=480
        ),
        MenuItem(
            category_id=cat_lunch.id,
            name="Rajma Chawal Bowl",
            description="Slow-cooked kidney beans in Punjabi spiced gravy over fragrant steamed basmati rice.",
            price=70.0,
            prep_time_minutes=4,
            complexity_score=0.8,
            stock_quantity=40,
            is_veg=True,
            calories=420
        ),
        # Snacks
        MenuItem(
            category_id=cat_snacks.id,
            name="Special Samosa (2 pcs) with Mint Chutney",
            description="Crispy golden pastry pockets stuffed with spiced potato and green peas.",
            price=30.0,
            prep_time_minutes=2,
            complexity_score=0.5,
            stock_quantity=80,
            is_veg=True,
            calories=260
        ),
        MenuItem(
            category_id=cat_snacks.id,
            name="Paneer Tikka Grilled Sandwich",
            description="Grilled multigrain bread loaded with marinated paneer tikka, onions, capsicum and mint mayo.",
            price=75.0,
            prep_time_minutes=5,
            complexity_score=1.0,
            stock_quantity=20,
            is_veg=True,
            calories=380
        ),
        MenuItem(
            category_id=cat_snacks.id,
            name="Veg Cheese Burger with French Fries",
            description="Crispy vegetable patty with melted cheese, lettuce, tomato and spiced mayonnaise.",
            price=85.0,
            prep_time_minutes=7,
            complexity_score=1.2,
            stock_quantity=25,
            is_veg=True,
            calories=490
        ),
        MenuItem(
            category_id=cat_snacks.id,
            name="Veg Hakka Noodles",
            description="Wok-tossed noodles with shredded cabbage, carrots, bell peppers, spring onions and soy sauce.",
            price=70.0,
            prep_time_minutes=6,
            complexity_score=1.1,
            stock_quantity=30,
            is_veg=True,
            calories=390
        ),
        # Beverages
        MenuItem(
            category_id=cat_beverages.id,
            name="South Indian Filter Coffee",
            description="Traditional strong decoction brewed with milk and served frothy.",
            price=20.0,
            prep_time_minutes=2,
            complexity_score=0.4,
            stock_quantity=100,
            is_veg=True,
            calories=95
        ),
        MenuItem(
            category_id=cat_beverages.id,
            name="Masala Chai (Ginger & Cardamom)",
            description="Piping hot milk tea infused with crushed ginger, cardamom and aromatic spices.",
            price=15.0,
            prep_time_minutes=2,
            complexity_score=0.4,
            stock_quantity=120,
            is_veg=True,
            calories=80
        ),
        MenuItem(
            category_id=cat_beverages.id,
            name="Fresh Cold Cold Coffee with Ice Cream",
            description="Thick creamy blended coffee topped with a rich scoop of vanilla ice cream.",
            price=50.0,
            prep_time_minutes=3,
            complexity_score=0.7,
            stock_quantity=40,
            is_veg=True,
            calories=240
        ),
        MenuItem(
            category_id=cat_beverages.id,
            name="Fresh Mint Lemonade (Nimbu Pani)",
            description="Refreshing chilled sweet-salted limeade with muddled mint leaves.",
            price=25.0,
            prep_time_minutes=2,
            complexity_score=0.4,
            stock_quantity=50,
            is_veg=True,
            calories=60
        ),
    ]
    db.add_all(menu_items)
    db.commit()

    # 4. Pickup Slots
    slot_times = [
        ("12:00 PM - 12:15 PM", time(12, 0), time(12, 15), 25, 6, SlotStatus.AVAILABLE),
        ("12:15 PM - 12:30 PM", time(12, 15), time(12, 30), 25, 14, SlotStatus.AVAILABLE),
        ("12:30 PM - 12:45 PM", time(12, 30), time(12, 45), 25, 24, SlotStatus.BUSY),
        ("12:45 PM - 01:00 PM", time(12, 45), time(13, 0), 25, 25, SlotStatus.FULL),
        ("01:00 PM - 01:15 PM", time(13, 0), time(13, 15), 25, 18, SlotStatus.BUSY),
        ("01:15 PM - 01:30 PM", time(13, 15), time(13, 30), 25, 8, SlotStatus.AVAILABLE),
        ("01:30 PM - 01:45 PM", time(13, 30), time(13, 45), 25, 4, SlotStatus.AVAILABLE),
        ("01:45 PM - 02:00 PM", time(13, 45), time(14, 0), 25, 0, SlotStatus.AVAILABLE),
    ]
    slots = [
        PickupSlot(
            slot_label=label,
            start_time=st,
            end_time=et,
            capacity=cap,
            booked_count=booked,
            status=status,
            is_active=True
        )
        for label, st, et, cap, booked, status in slot_times
    ]
    db.add_all(slots)
    db.commit()

    # 5. Demo Order (Ready for pickup with QR token)
    dosa = db.query(MenuItem).filter(MenuItem.name.ilike("%Masala Dosa%")).first()
    coffee = db.query(MenuItem).filter(MenuItem.name.ilike("%Filter Coffee%")).first()
    
    order1 = Order(
        order_number="ORD-20261005-0001",
        token_number="#T-001",
        user_id=student.id,
        pickup_slot_id=slots[1].id,
        status=OrderStatus.READY,
        total_amount=80.0,
        estimated_prep_time_minutes=8,
        estimated_ready_time=datetime.utcnow() - timedelta(minutes=2),
        actual_ready_time=datetime.utcnow() - timedelta(minutes=1),
        special_instructions="Extra sambar and crispy please"
    )
    db.add(order1)
    db.flush()

    item1 = OrderItem(
        order_id=order1.id,
        menu_item_id=dosa.id,
        quantity=1,
        unit_price=dosa.price,
        total_price=dosa.price,
        prep_time_snapshot=dosa.prep_time_minutes,
        complexity_snapshot=dosa.complexity_score
    )
    item2 = OrderItem(
        order_id=order1.id,
        menu_item_id=coffee.id,
        quantity=1,
        unit_price=coffee.price,
        total_price=coffee.price,
        prep_time_snapshot=coffee.prep_time_minutes,
        complexity_snapshot=coffee.complexity_score
    )
    db.add_all([item1, item2])
    db.flush()

    qr_tok, qr_sig = QRVerificationService.generate_qr_token(order1)
    order1.pickup_qr_token = qr_tok
    order1.pickup_qr_signature = qr_sig

    payment1 = Payment(
        order_id=order1.id,
        transaction_id="TXN_DEMO_20261005_001",
        idempotency_key="IDEMP_DEMO_001",
        amount=80.0,
        payment_method=PaymentMethod.CAMPUS_WALLET,
        status=PaymentStatus.SUCCESS,
        completed_at=datetime.utcnow() - timedelta(minutes=10)
    )
    db.add(payment1)

    q_entry = QueueEntry(
        order_id=order1.id,
        queue_position=1,
        priority_score=142.5,
        waiting_time_minutes=9.5,
        aging_bonus=11.8,
        urgency_score=1.5,
        complexity_penalty=1.0,
        assigned_station="Station-1",
        entered_queue_at=datetime.utcnow() - timedelta(minutes=10),
        started_prep_at=datetime.utcnow() - timedelta(minutes=8),
        completed_prep_at=datetime.utcnow() - timedelta(minutes=1)
    )
    db.add(q_entry)
    db.commit()

    print("Smart Canteen Database successfully populated with realistic campus records!")

if __name__ == "__main__":
    db = SessionLocal()
    seed_database(db)
    db.close()
