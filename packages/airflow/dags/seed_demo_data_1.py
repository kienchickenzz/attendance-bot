import asyncio
from datetime import date, timedelta

from packages.airflow.dags.etl.db import DbConnPool

async def main():
    connection_url = "postgresql://postgres:Pa55w.rd@localhost:5432/attendance_processed"
    db_pool = DbConnPool()

    demo_emails = [
        'ndkien.ts@cmc.com.vn', 'ndgiang1@cmc.com.vn', 'pthieu5@cmc.com.vn',
        'dmdat@cmc.com.vn', 'qthung@cmc.com.vn',
    ]

    # Tạo dữ liệu cho tất cả ngày trong tuần của tháng 8/2025
    weekdays = []
    start_date = date(2025, 8, 1)  # 1/8/2025
    end_date = date(2025, 8, 31)   # 31/8/2025
    
    current_date = start_date
    while current_date <= end_date:
        # Chỉ thêm thứ 2-6 (weekday 0-4)
        if current_date.weekday() < 5:
            weekdays.append(current_date)
        current_date += timedelta(days=1)

    # Tạo dữ liệu để insert
    insert_data = []
    for email in demo_emails:
        for day in weekdays:
            insert_data.append((email, day, False, False, 5))

    seed_data_sql = """
INSERT INTO attendance_calculation_input (user_email, date, leave_morning, leave_afternoon, free_allowance)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (user_email, date) DO NOTHING;
"""
    
    try:
        await db_pool.connect(connection_url)
        print("✅ Kết nối thành công!")

        for data in insert_data:
            await db_pool.execute_query(seed_data_sql, data, readonly=False)
        print( "✅ Seed dữ liệu demo thành công!" )
        print( f"📊 Đã thêm { len( demo_emails ) * len( weekdays ) } bản ghi cho { len( demo_emails ) } user trong tháng 8/2025" )
        
    except Exception as e:
        print( f"❌ Error: { e }" )
        
    finally:
        await db_pool.close()

if __name__ == "__main__":
    asyncio.run( main() )
