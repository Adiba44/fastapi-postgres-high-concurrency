from fastapi import FastAPI
import asyncpg
from contextlib import asynccontextmanager
from fastapi import BackgroundTasks


DATABASE_URL = "postgresql://postgres:  @localhost:5432/postgres"


@asynccontextmanager
async def lifespan(app:FastAPI):
    print("Database connection pool is getting ready...")
    app.state.pool = await asyncpg.create_pool(
        DATABASE_URL, min_size= 5, max_size= 20
    )
    
    
    yield
    print("Database connection pool is getting close")
    await app.state.pool.close()


app = FastAPI(lifespan= lifespan)


@app.get("/")
async def check_health():
    async with app.state.pool.acquire() as connection:
        version = await connection.fetchval("SELECT version();")
    return {"status": "success", "db_version": version}


@app.post("/process-order/{order_id}")
async def process_order(order_id: int):
    async with app.state.pool.acquire() as connection:
        # Starting a strict ACID transaction block
        async with connection.transaction():
            
            # Locking the specific row so no other request can read or modify it concurrently
            select_query = "SELECT status FROM orders WHERE id = $1 FOR UPDATE"
            current_status = await connection.fetchval(select_query, order_id)
            
            if current_status is None:
                return {"error": "Order not found"}
                
            if current_status != 1:
                return {"error": "Order already processed or cancelled"}
            
            # Processing the payment logic here (simulated)
            
            update_query = "UPDATE orders SET status = 2 WHERE id = $1"
            await connection.execute(update_query, order_id)
            
            return {"status": "success", "message": f"Order {order_id} successfully marked as Paid"}
        
    
    

@app.get("/export-paid-orders")
async def export_paid_orders():
    async with app.state.pool.acquire() as connection:
        # Cursors in PostgreSQL require a transaction block
        async with connection.transaction():
            query = "SELECT id, user_id, order_details FROM orders WHERE status = 2"
            
            processed_count = 0
            
            # Using asyncpg's server-side cursor to fetch data chunk by chunk
            async for record in connection.cursor(query):
                # We are processing one row at a time. RAM usage remains minimal!
                processed_count += 1
                
                # We will break at 100 for testing, so it doesn't run forever
                if processed_count >= 100:
                    break
                    
            return {
                "status": "success", 
                "message": f"Processed {processed_count} rows using database cursor safely."
            }
            
            
            
            
@app.post("/trigger-db-processing")
async def trigger_db_processing():
    # Acquire an optimized connection from the pool
    async with app.state.pool.acquire() as connection:
        
        # Execute the PL/pgSQL function directly in the database engine
        # await connection.execute() sends the command and waits for completion
        await connection.execute("SELECT process_bulk_orders_safely();")
        
        return {
            "status": "success", 
            "message": "Heavy processing completed entirely inside the database engine."
        }