-- ====================================================================
-- SMART CANTEEN ORCHESTRATION PLATFORM - SUPABASE RLS & TRIGGERS
-- MIGRATION: 003_rls_and_triggers.sql
-- ====================================================================

-- Enable RLS on core tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- 1. Users policies: Users can view their own profile; Staff/Admin can view all
CREATE POLICY "Users can view own profile" 
ON users FOR SELECT 
USING (auth.uid() = id::text OR auth.jwt() ->> 'role' IN ('STAFF', 'ADMIN'));

-- 2. Orders policies: Students can view own orders; Staff/Admin can view all
CREATE POLICY "Students can view own orders" 
ON orders FOR SELECT 
USING (auth.uid() = user_id::text OR auth.jwt() ->> 'role' IN ('STAFF', 'ADMIN'));

-- 3. Notifications: Users can view and update own notifications
CREATE POLICY "Users can view own notifications" 
ON notifications FOR SELECT 
USING (auth.uid() = user_id::text);

CREATE POLICY "Users can update own notifications" 
ON notifications FOR UPDATE 
USING (auth.uid() = user_id::text);

-- Trigger function for preventing negative inventory at database level
CREATE OR REPLACE FUNCTION check_inventory_non_negative()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.stock_quantity < 0 THEN
        RAISE EXCEPTION 'Inventory constraint violation: stock_quantity cannot be negative for item %', NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_inventory_non_negative
BEFORE UPDATE ON menu_items
FOR EACH ROW
EXECUTE FUNCTION check_inventory_non_negative();
