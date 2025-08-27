import asyncio
from db import DbConnPool

async def main():
    connection_url = "postgresql://postgres:Pa55w.rd@localhost:5432/attendance_processed"
    db_pool = DbConnPool()
    
    try:
        await db_pool.connect( connection_url )
        print("✅ Kết nối thành công!")
        
        result = await db_pool.execute_query("SELECT version()", readonly=True)
        if result:
            print(f"PostgreSQL version: {result[0].cells['version']}")
        
    except Exception as e:
        print( f"❌ Error: { e }" )
        
    finally:
        await db_pool.close()

if __name__ == "__main__":
    asyncio.run( main() )
