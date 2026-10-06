-- ====================================================================
-- SMART CANTEEN ORCHESTRATION PLATFORM - DATABASE INDEXES
-- MIGRATION: 002_indexes_and_constraints.sql
-- ====================================================================

-- Composite index for real-time queue queries and KDS ordering
CREATE INDEX idx_orders_status_created_at ON orders (status, created_at);

-- Index for student order history queries
CREATE INDEX idx_orders_user_id_status ON orders (user_id, status);

-- Index for fast slot capacity lookups
CREATE INDEX idx_orders_pickup_slot_id ON orders (pickup_slot_id);

-- Composite index on queue priority and dynamic ranking
CREATE INDEX idx_queue_priority_position ON queue_entries (priority_score DESC, entered_queue_at ASC);

-- Index for payment idempotency lookups
CREATE INDEX idx_payments_idempotency_key ON payments (idempotency_key);
CREATE INDEX idx_payments_transaction_id ON payments (transaction_id);

-- Index for menu item stock & category browsing
CREATE INDEX idx_menu_items_cat_avail ON menu_items (category_id, is_available, stock_quantity);

-- Index for stock audit history
CREATE INDEX idx_inventory_logs_menu_item ON inventory_logs (menu_item_id, created_at DESC);

-- Index for unread notifications
CREATE INDEX idx_notifications_user_unread ON notifications (user_id, is_read);
