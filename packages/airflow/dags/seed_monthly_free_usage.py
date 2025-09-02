import asyncio

from psycopg import AsyncConnection

async def main():
    connection_url = "postgresql://postgres:Pa55w.rd@localhost:5432/attendance"
    conn = None
    cursor = None

    employee_ids = [
        'ndkien.ts@cmc.com.vn',
        'dmdat@cmc.com.vn',
        'ndgiang1@cmc.com.vn',
        'pthieu5@cmc.com.vn',
        'ntntuyet1@cmc.com.vn',
    ]
    
    # Dữ liệu seed cho tháng 7, 8, 9 năm 2025
    months_data = [
        ('2025-07-01', 0 ),  # Tháng 7
        ('2025-08-01', 0 ),  # Tháng 8
        ('2025-09-01', 0 ),  # Tháng 9
    ]

    all_records = []
    for employee_id in employee_ids:
        for year_month, used_count in months_data:
            all_records.append( ( employee_id, year_month, used_count ) )

    seed_data_sql = """
INSERT INTO monthly_free_usage (employee_id, year_month, used_count)
VALUES (%s, %s, %s)
ON CONFLICT (employee_id, year_month) DO NOTHING;
"""
    
    try:
        conn = await AsyncConnection.connect( connection_url )
        print( "✅ Kết nối thành công!" )

        cursor = conn.cursor()

        await cursor.executemany( seed_data_sql, all_records )
        await conn.commit()
        
    except Exception as e:
        print( f"❌ Error: { e }" )

        # Rollback nếu có lỗi
        if conn:
            await conn.rollback()
        
    finally:
        # Đóng cursor và connection
        if cursor:
            await cursor.close()
        if conn:
            await conn.close()
            print( "🔒 Đã đóng kết nối database" )

if __name__ == "__main__":
    asyncio.run( main() )
