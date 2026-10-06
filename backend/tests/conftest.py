import pytest
from datetime import datetime, time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.config import settings
from app.models.user import User, UserRole
from app.models.category import Category
from app.models.menu_item import MenuItem
from app.models.pickup_slot import PickupSlot, SlotStatus
from app.services.auth_service import hash_password, create_access_token

# In-memory test database with StaticPool so all connections share the memory DB
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    
    # Populate essential seed data
    student = User(
        campus_id="STU-TEST-001",
        full_name="Test Student",
        email="student@test.com",
        hashed_password=hash_password("password123"),
        role=UserRole.STUDENT
    )
    staff = User(
        campus_id="STF-TEST-001",
        full_name="Test Staff Chef",
        email="staff@test.com",
        hashed_password=hash_password("password123"),
        role=UserRole.STAFF
    )
    admin = User(
        campus_id="ADM-TEST-001",
        full_name="Test Admin",
        email="admin@test.com",
        hashed_password=hash_password("password123"),
        role=UserRole.ADMIN
    )
    db.add_all([student, staff, admin])
    db.commit()

    cat = Category(name="Quick Bites", description="Test Category", icon="Utensils")
    db.add(cat)
    db.commit()

    item1 = MenuItem(
        category_id=cat.id,
        name="Crispy Samosa",
        description="Fresh hot samosa",
        price=30.0,
        stock_quantity=5, # Small stock to test limits & race conditions
        prep_time_minutes=3,
        complexity_score=0.8,
        is_available=True,
        is_veg=True
    )
    item2 = MenuItem(
        category_id=cat.id,
        name="Masala Dosa",
        description="Golden crepe",
        price=60.0,
        stock_quantity=20,
        prep_time_minutes=6,
        complexity_score=1.2,
        is_available=True,
        is_veg=True
    )
    db.add_all([item1, item2])
    db.commit()

    slot1 = PickupSlot(
        slot_label="12:30 PM - 12:45 PM",
        start_time=time(12, 30),
        end_time=time(12, 45),
        capacity=2, # Small capacity to test slot exhaustion
        booked_count=0,
        status=SlotStatus.AVAILABLE,
        is_active=True
    )
    db.add(slot1)
    db.commit()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def student_auth_headers(db_session):
    student = db_session.query(User).filter(User.email == "student@test.com").first()
    token = create_access_token(data={"sub": str(student.id), "role": student.role.value})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def staff_auth_headers(db_session):
    staff = db_session.query(User).filter(User.email == "staff@test.com").first()
    token = create_access_token(data={"sub": str(staff.id), "role": staff.role.value})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_auth_headers(db_session):
    admin = db_session.query(User).filter(User.email == "admin@test.com").first()
    token = create_access_token(data={"sub": str(admin.id), "role": admin.role.value})
    return {"Authorization": f"Bearer {token}"}
