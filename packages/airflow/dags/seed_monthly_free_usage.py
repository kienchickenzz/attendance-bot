import asyncio
from datetime import datetime

from etl.db import DbConnPool

async def main():
    connection_url = "postgresql://postgres:Pa55w.rd@localhost:5432/attendance"
    db_pool = DbConnPool()

    employee_id = 'ndkien.ts@cmc.com.vn'
    
    # Dữ liệu seed cho tháng 7, 8, 9 năm 2024
    monthly_data = [
        ('2024-07-01', 0),  # Tháng 7
        ('2024-08-01', 0),  # Tháng 8
        ('2024-09-01', 0),  # Tháng 9
    ]

    seed_data_sql = """
INSERT INTO monthly_free_usage (employee_id, year_month, used_count)
VALUES (%s, %s, %s)
ON CONFLICT (employee_id, year_month) DO NOTHING;
"""
    
    try:
        await db_pool.connect( connection_url )
        print( "✅ Kết nối thành công!" )

        for year_month, used_count in monthly_data:
            await db_pool.execute_query(
                seed_data_sql, 
                (employee_id, year_month, used_count), 
                readonly=False
            )
            print( f"✅ Seed dữ liệu cho {employee_id} tháng {year_month} thành công!" )
        
    except Exception as e:
        print( f"❌ Error: { e }" )
        
    finally:
        await db_pool.close()

if __name__ == "__main__":
    asyncio.run( main() )
