CREATE OR REPLACE FUNCTION process_bulk_orders_safely()
RETURNS void AS $$
DECLARE
    -- 1. Cursor declaration (Fast execution plan er jonno)
    order_cur CURSOR FOR SELECT id, order_details FROM orders WHERE status = 2;
    -- 2. Matro 1 ta row RAM e hold korar temporary variable
    record_row RECORD;
BEGIN
    -- Cursor ta memory te open kora holo
    OPEN order_cur;

    LOOP
        -- 3. Disk theke matro 1 ta row record_row te pull korchi
        FETCH order_cur INTO record_row;

        -- 4. Kono data na thakle loop break korbe
        EXIT WHEN NOT FOUND;

        -- 5. Ekhane tumi JSONB data update, audit logging, ba onno table e insert er logic likhte parbe.
        -- Amra jeno fast runtime maintain kori tai test korar jonno just output print korchi:
        RAISE NOTICE 'Processing Order ID: %, Platform: %', record_row.id, record_row.order_details->>'platform';
    END LOOP;

    -- 6. Resource free kora r memory leak thekanor jonno cursor close kora oboshshok
    CLOSE order_cur;
END;
$$ LANGUAGE plpgsql;




SELECT process_bulk_orders_safely();

