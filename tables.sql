CREATE TABLE IF NOT EXISTS orders (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, -- Standard BIGSERIAL er cheye better practice, B-Tree index er jonno perfect
    user_id INTEGER NOT NULL, -- Only 4 bytes
    status SMALLINT NOT NULL DEFAULT 1, -- 1: Pending, 2: Paid, 3: Cancelled. (Only 2 bytes space nibe, string er theke onek fast)
    order_details JSONB NOT NULL, -- Dynamic data r jonno JSONB. Binary format e save hoy tai parsing super fast.
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP -- Timezone shoho exact time, 8 bytes
);

select * from orders;

SELECT * FROM orders ORDER BY id DESC LIMIT 100;

EXPLAIN ANALYZE SELECT * FROM orders WHERE order_details->>'platform' = 'web';


CREATE INDEX idx_orders_platform ON orders ((order_details->>'platform'));

EXPLAIN ANALYZE SELECT * FROM orders WHERE order_details->>'platform' = 'web';

EXPLAIN ANALYZE SELECT * FROM orders WHERE order_details->>'platform' = 'web' LIMIT 50;