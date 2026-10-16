import asyncio
import asyncpg
import json
import random
from datetime import datetime
from zoneinfo import ZoneInfo

DATABASE_URL = "postgresql://postgres:  @localhost:5432/postgres"


async def seed_millions_of_rows():
    conn = await asyncpg.connect(DATABASE_URL)
    print("Connected to DB. Preparing 1 Million records...")

    bd_tz = ZoneInfo("Asia/Dhaka")

    def data_generator():
        for _ in range(1000000):
            user_id = random.randint(1, 50000)
            status = random.randint(1, 3)
            
            order_details = json.dumps({
                "item_id": random.randint(100, 999),
                "qty": random.randint(1, 5),
                "platform": random.choice(["web", "ios", "android"])
            })
            
            created_at = datetime.now(bd_tz)
            
            yield (user_id, status, order_details, created_at)

    print("Executing high-speed COPY command...")
    
    await conn.copy_records_to_table(
        'orders',
        columns=['user_id', 'status', 'order_details', 'created_at'],
        records=data_generator()
    )

    await conn.close()
    print("Successfully inserted 1 Million rows!")

if __name__ == "__main__":
    asyncio.run(seed_millions_of_rows())