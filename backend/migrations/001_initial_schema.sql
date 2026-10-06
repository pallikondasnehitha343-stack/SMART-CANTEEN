-- ====================================================================
-- SMART CANTEEN ORCHESTRATION PLATFORM - DATABASE DDL (SUPABASE / POSTGRESQL)
-- MIGRATION: 001_initial_schema.sql
-- ====================================================================

-- 1. Create Enums
CREATE TYPE user_role AS ENUM ('STUDENT', 'STAFF', 'ADMIN');
CREATE TYPE order_status AS ENUM (
    'CREATED', 'PAYMENT_PENDING', 'CONFIRMED', 'QUEUED', 
    'ACCEPTED', 'PREPARING', 'READY', 'PICKED_UP', 'CANCELLED', 'REFUNDED'
);
CREATE TYPE payment_status AS ENUM (
    'INITIATED', 'PROCESSING', 'SUCCESS', 'FAILED', 'PENDING', 'TIMEOUT', 'CANCELLED', 'REFUNDED'
);
CREATE TYPE payment_method AS ENUM (
    'CAMPUS_WALLET', 'UPI', 'CREDIT_DEBIT_CARD', 'NET_BANKING'
);
CREATE TYPE slot_status AS ENUM ('AVAILABLE', 'BUSY', 'FULL', 'CLOSED');
CREATE TYPE stock_change_reason AS ENUM (
    'ORDER_RESERVATION', 'ORDER_CANCELLATION', 'MANUAL_RESTOCK', 'WASTAGE_ADJUSTMENT'
);

-- 2. Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    campus_id VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'STUDENT' NOT NULL,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 3. Categories Table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255),
    icon VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 4. Menu Items Table
CREATE TABLE menu_items (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    is_available BOOLEAN DEFAULT TRUE NOT NULL,
    stock_quantity INTEGER DEFAULT 50 NOT NULL CHECK (stock_quantity >= 0),
    prep_time_minutes INTEGER DEFAULT 5 NOT NULL CHECK (prep_time_minutes > 0),
    complexity_score NUMERIC(3, 2) DEFAULT 1.0 NOT NULL CHECK (complexity_score > 0),
    image_url VARCHAR(255),
    is_veg BOOLEAN DEFAULT TRUE NOT NULL,
    calories INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 5. Pickup Slots Table
CREATE TABLE pickup_slots (
    id SERIAL PRIMARY KEY,
    slot_label VARCHAR(50) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    capacity INTEGER DEFAULT 25 NOT NULL CHECK (capacity > 0),
    booked_count INTEGER DEFAULT 0 NOT NULL CHECK (booked_count >= 0 AND booked_count <= capacity),
    status slot_status DEFAULT 'AVAILABLE' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 6. Orders Table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    token_number VARCHAR(20) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    pickup_slot_id INTEGER REFERENCES pickup_slots(id) ON DELETE SET NULL,
    status order_status DEFAULT 'CREATED' NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL CHECK (total_amount >= 0),
    estimated_prep_time_minutes INTEGER DEFAULT 10 NOT NULL,
    estimated_ready_time TIMESTAMP WITH TIME ZONE,
    actual_ready_time TIMESTAMP WITH TIME ZONE,
    picked_up_at TIMESTAMP WITH TIME ZONE,
    pickup_qr_token TEXT,
    pickup_qr_signature VARCHAR(255),
    is_qr_used INTEGER DEFAULT 0 NOT NULL CHECK (is_qr_used IN (0, 1)),
    special_instructions TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 7. Order Items Table
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE NOT NULL,
    menu_item_id INTEGER REFERENCES menu_items(id) ON DELETE RESTRICT NOT NULL,
    quantity INTEGER DEFAULT 1 NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    total_price NUMERIC(10, 2) NOT NULL CHECK (total_price >= 0),
    prep_time_snapshot INTEGER DEFAULT 5 NOT NULL,
    complexity_snapshot NUMERIC(3, 2) DEFAULT 1.0 NOT NULL
);

-- 8. Queue Entries Table
CREATE TABLE queue_entries (
    id SERIAL PRIMARY KEY,
    order_id INTEGER UNIQUE REFERENCES orders(id) ON DELETE CASCADE NOT NULL,
    queue_position INTEGER DEFAULT 1 NOT NULL CHECK (queue_position > 0),
    priority_score NUMERIC(8, 2) DEFAULT 100.0 NOT NULL,
    waiting_time_minutes NUMERIC(6, 2) DEFAULT 0.0 NOT NULL,
    aging_bonus NUMERIC(6, 2) DEFAULT 0.0 NOT NULL,
    urgency_score NUMERIC(4, 2) DEFAULT 1.0 NOT NULL,
    complexity_penalty NUMERIC(4, 2) DEFAULT 1.0 NOT NULL,
    assigned_station VARCHAR(50) DEFAULT 'Station-1' NOT NULL,
    entered_queue_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    started_prep_at TIMESTAMP WITH TIME ZONE,
    completed_prep_at TIMESTAMP WITH TIME ZONE
);

-- 9. Payments Table
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER UNIQUE REFERENCES orders(id) ON DELETE CASCADE NOT NULL,
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    idempotency_key VARCHAR(100) UNIQUE,
    amount NUMERIC(10, 2) NOT NULL CHECK (amount >= 0),
    currency VARCHAR(10) DEFAULT 'INR' NOT NULL,
    payment_method payment_method DEFAULT 'CAMPUS_WALLET' NOT NULL,
    status payment_status DEFAULT 'INITIATED' NOT NULL,
    gateway_response TEXT,
    error_message VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- 10. Inventory Logs Table
CREATE TABLE inventory_logs (
    id SERIAL PRIMARY KEY,
    menu_item_id INTEGER REFERENCES menu_items(id) ON DELETE CASCADE NOT NULL,
    change_amount INTEGER NOT NULL,
    previous_stock INTEGER NOT NULL,
    new_stock INTEGER NOT NULL,
    reason stock_change_reason NOT NULL,
    reference_id VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 11. Notifications Table
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) DEFAULT 'ORDER_STATUS' NOT NULL,
    is_read BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 12. Hourly KPIs Table
CREATE TABLE hourly_kpis (
    id SERIAL PRIMARY KEY,
    recorded_hour TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    total_orders INTEGER DEFAULT 0 NOT NULL,
    completed_orders INTEGER DEFAULT 0 NOT NULL,
    cancelled_orders INTEGER DEFAULT 0 NOT NULL,
    total_revenue NUMERIC(12, 2) DEFAULT 0.0 NOT NULL,
    avg_waiting_time_minutes NUMERIC(6, 2) DEFAULT 0.0 NOT NULL,
    avg_prep_time_minutes NUMERIC(6, 2) DEFAULT 0.0 NOT NULL,
    avg_pickup_delay_minutes NUMERIC(6, 2) DEFAULT 0.0 NOT NULL,
    peak_level VARCHAR(20) DEFAULT 'NORMAL' NOT NULL,
    kitchen_utilization_pct NUMERIC(5, 2) DEFAULT 0.0 NOT NULL
);

-- 13. Bottleneck Events Table
CREATE TABLE bottleneck_events (
    id SERIAL PRIMARY KEY,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP WITH TIME ZONE,
    bottleneck_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'WARNING' NOT NULL,
    active_orders_count INTEGER DEFAULT 0 NOT NULL,
    avg_eta_minutes NUMERIC(6, 2) DEFAULT 0.0 NOT NULL,
    description TEXT NOT NULL,
    recommended_action TEXT
);
