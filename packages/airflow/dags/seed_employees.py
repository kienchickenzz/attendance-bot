import asyncio
from datetime import datetime

from psycopg import AsyncConnection

async def main():
    connection_url = "postgresql://postgres:Pa55w.rd@localhost:5432/attendance"
    conn = None
    cursor = None

    employees_data = [ 
        {
            'employee_id': 'ndkien.ts@cmc.com.vn',
            'email': 'ndkien.ts@cmc.com.vn',
            'full_name': 'NGUYỄN ĐỨC KIÊN',
            'department': 'ITD',
            'position': 'Intern',
            'is_active': True,
            'created_at': datetime.now()
        },
        {
            'employee_id': 'dmdat@cmc.com.vn',
            'email': 'dmdat@cmc.com.vn',
            'full_name': 'DOÃN MINH ĐẠT',
            'department': 'ITD',
            'position': 'Intern',
            'is_active': True,
            'created_at': datetime.now()
        },
        {
            'employee_id': 'ndgiang1@cmc.com.vn',
            'email': 'ndgiang1@cmc.com.vn',
            'full_name': 'NGUYỄN ĐÌNH GIANG',
            'department': 'ITD',
            'position': 'Intern',
            'is_active': True,
            'created_at': datetime.now()
        },
        {
            'employee_id': 'pthieu5@cmc.com.vn',
            'email': 'pthieu5@cmc.com.vn',
            'full_name': 'PHẠM TRUNG HIẾU',
            'department': 'ITD',
            'position': 'Intern',
            'is_active': True,
            'created_at': datetime.now()
        },
        {
            'employee_id': 'ntntuyet1@cmc.com.vn',
            'email': 'ntntuyet1@cmc.com.vn',
            'full_name': 'NGUYỄN THỊ NGỌC TUYẾT',
            'department': 'ITD',
            'position': 'Intern',
            'is_active': True,
            'created_at': datetime.now()
        },
    ]

    seed_data_sql = """
INSERT INTO employees (employee_id, email, full_name, department, position, is_active, created_at)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (employee_id) DO NOTHING
RETURNING employee_id, full_name;
"""
    
    try:
        conn = await AsyncConnection.connect( connection_url )
        print( "✅ Kết nối thành công!" )

        cursor = conn.cursor()

        employees_tuples = [
            (
                emp[ 'employee_id' ],
                emp[ 'email' ],
                emp[ 'full_name' ],
                emp[ 'department' ],
                emp[ 'position' ],
                emp[ 'is_active' ],
                emp[ 'created_at' ]
            )
            for emp in employees_data
        ]

        await cursor.executemany( seed_data_sql, employees_tuples )
        await conn.commit()

        print( "✅ Seed dữ liệu employee thành công!" )
        
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
