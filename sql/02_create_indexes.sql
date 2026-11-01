CREATE INDEX idx_orders_customer_id on orders (customer_id);
CREATE INDEX idx_orders_store_id ON orders (store_id);
CREATE INDEX idx_orders_created_at ON orders (created_at);
CREATE INDEX idx_order_items_order_id ON order_items (order_id);
CREATE INDEX idx_order_items_product_id ON order_items (product_id);