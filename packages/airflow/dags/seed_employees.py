import asyncio
from datetime import datetime

from db import DbConnPool

async def main():
    connection_url = "postgresql://postgres:Pa55w.rd@localhost:5432/attendance"
    db_pool = DbConnPool()

    employee_data = {
        'employee_id': 'ndkien.ts@cmc.com.vn',
        'email': 'ndkien.ts@cmc.com.vn',
        'full_name': 'NGUYỄN ĐỨC KIÊN',
        'department': 'ITD',
        'position': 'Intern',
        'is_active': True,
        'created_at': datetime.now()
    }

    seed_data_sql = """
INSERT INTO employees (employee_id, email, full_name, department, position, is_active, created_at)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (employee_id) DO NOTHING;
"""
    
    try:
        await db_pool.connect( connection_url )
        print( "✅ Kết nối thành công!" )

        await db_pool.execute_query(
            seed_data_sql, 
            (
                employee_data[ 'employee_id' ],
                employee_data[ 'email' ], 
                employee_data[ 'full_name' ],
                employee_data[ 'department' ],
                employee_data[ 'position' ],
                employee_data[ 'is_active' ],
                employee_data[ 'created_at' ]
            ), 
            readonly=False
        )
        print( "✅ Seed dữ liệu employee thành công!" )
        print( f"📊 Đã thêm employee: { employee_data[ 'full_name' ] } ({ employee_data[ 'email' ] })" )
        
    except Exception as e:
        print( f"❌ Error: { e }" )
        
    finally:
        await db_pool.close()

if __name__ == "__main__":
    asyncio.run( main() )
