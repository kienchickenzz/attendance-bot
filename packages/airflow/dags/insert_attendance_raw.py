import asyncio
import json
from datetime import datetime, date
from typing import Any

from etl.db import DbConnPool


async def _get_employee_email( db_pool: DbConnPool, employee_id: str ) -> str | None:
    query = "SELECT email FROM employees WHERE employee_id = %s"
    params = [ employee_id ]
    result = await db_pool.execute_query( query, params )
    if not result:
        return None
    return result[ 0 ].cells[ "email" ]

async def _get_existing_data(
    db_pool: DbConnPool, employee_id: str, target_date: date
) -> dict | None:
    query = """
        SELECT first_in, last_out 
        FROM attendance_raw 
        WHERE employee_id = %s AND date = %s
    """
    params = [ employee_id, target_date ]
    result = await db_pool.execute_query( query, params )
    if not result:
        return None
    
    row = result[ 0 ].cells
    return {
        "first_in": row[ "first_in" ],
        "last_out": row[ "last_out" ]
    }

def _load_user_records_from_json(
    json_file: str, 
    target_email: str
) -> tuple[ date, list[ dict[ str, Any ] ] ]:

    # Trích xuất ngày từ tên file (vd: filtered_2025-08-20.json -> 2025-08-20)
    date_str = json_file.split('_')[1].split('.')[0]
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    # Đọc dữ liệu từ file JSON
    with open( json_file, "r", encoding="utf-8" ) as f:
        json_data = json.load( f )

    # Lọc ra record của user cần thiết
    target_records = [ record for record in json_data if record.get( "email" ) == target_email ]

    return target_date, target_records

async def main():
    connection_url = "postgresql://postgres:Pa55w.rd@localhost:5432/attendance"
    db_pool = DbConnPool()
    
    try:
        await db_pool.connect( connection_url )
        print( "✅ Kết nối thành công!" )
        
        target_employee_id = 'ndkien.ts@cmc.com.vn'

        target_email = await _get_employee_email( db_pool, target_employee_id )
        if not target_email:
            print( f"⚠️  Can not find employee_id { target_employee_id } in employees table" )
            return
        
        print( f"📧 Email từ bảng employees: { target_email }" )
                
        # SQL để insert dữ liệu mới
        insert_sql = """
        INSERT INTO attendance_raw (employee_id, date, first_in, last_out)
        VALUES (%s, %s, %s, %s)
        """
        
        # SQL để update dữ liệu
        update_sql = """
        UPDATE attendance_raw 
        SET first_in = %s, last_out = %s, last_updated = CURRENT_TIMESTAMP, data_version = data_version + 1
        WHERE employee_id = %s AND date = %s
        """
        
        json_file = "./etl/data/filtered_2025-08-20.json"
        target_date, target_records = _load_user_records_from_json( json_file, target_email )
        
        if not target_records:
            print( f"⚠️  Không tìm thấy dữ liệu cho { target_email }" )

        total_records = 0
        skipped_records = 0
        
        # Xử lý từng record
        for record in target_records:
            # Chuyển đổi first_in và last_out từ string thành timestamp
            new_first_in = None
            new_last_out = None
            
            if record.get( 'first_in' ):
                new_first_in = datetime.strptime( record[ 'first_in' ], '%Y-%m-%d %H:%M' )
            
            if record.get( 'last_out' ):
                new_last_out = datetime.strptime( record['last_out' ], '%Y-%m-%d %H:%M' )
            
            existing_data = await _get_existing_data( db_pool, target_employee_id, target_date )
            
            # Dữ liệu đã tồn tại, so sánh giá trị
            if existing_data:
                existing_first_in = existing_data[ 'first_in' ]
                existing_last_out = existing_data[ 'last_out' ]
                
                # So sánh giá trị (chuyển về cùng định dạng để so sánh)
                first_in_same = (new_first_in == existing_first_in) if (new_first_in and existing_first_in) else (new_first_in is None and existing_first_in is None)
                last_out_same = (new_last_out == existing_last_out) if (new_last_out and existing_last_out) else (new_last_out is None and existing_last_out is None)
                
                if first_in_same and last_out_same:
                    print(f"⏭️  Skip {target_employee_id} - {target_date}: Dữ liệu không thay đổi")
                    skipped_records += 1
                    continue
                else:
                    try:
                        await db_pool.execute_query(
                            update_sql,
                            (new_first_in, new_last_out, target_employee_id, target_date),
                            readonly=False
                        )
                        print(f"🔄 Update {target_employee_id} - {target_date}: CheckIn={new_first_in.strftime('%H:%M') if new_first_in else 'N/A'}, CheckOut={new_last_out.strftime('%H:%M') if new_last_out else 'N/A'}")
            
                    except Exception as e:
                        print( f"❌ Error: { e }" )

            else: # Insert dữ liệu mới
                await db_pool.execute_query(
                    insert_sql,
                    (target_employee_id, target_date, new_first_in, new_last_out),
                    readonly=False
                )
                print(f"➕ Insert {target_employee_id} - {target_date}: CheckIn={new_first_in.strftime('%H:%M') if new_first_in else 'N/A'}, CheckOut={new_last_out.strftime('%H:%M') if new_last_out else 'N/A'}")
            
            total_records += 1
        
        print(f"\n🎉 Hoàn thành! Đã xử lý {total_records} bản ghi, bỏ qua {skipped_records} bản ghi không thay đổi cho {target_employee_id}")
        
    except Exception as e:
        print( f"❌ Error: { e }" )
        
    finally:
        await db_pool.close()

if __name__ == "__main__":
    asyncio.run( main() )
