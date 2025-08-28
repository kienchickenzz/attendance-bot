import asyncio
import json
from datetime import date, datetime
from pathlib import Path

from db import DbConnPool
from utils import process_daily_attendance

async def _get_input_data( db_pool: DbConnPool, user_email, target_date):
    """
    Truy vấn dữ liệu từ bảng attendance_calculation_input cho 1 user và 1 ngày cụ thể
    """
    
    query = """
    SELECT user_email, date, leave_morning, leave_afternoon, free_allowance 
    FROM attendance_calculation_input 
    WHERE user_email = %s AND date = %s
    """
    
    params = [ user_email, target_date ]
    result = await db_pool.execute_query( query, params )
    
    if not result:
        return None
    
    row = result[ 0 ].cells
    return {
        'leave_morning': row[ 'leave_morning' ], 
        'leave_afternoon': row[ 'leave_afternoon' ],
        'free_allowance': row[ 'free_allowance' ]
    }

async def process_single_day( 
    db_pool: DbConnPool, 
    user_email, 
    target_date, 
    checkin_time=None, 
    checkout_time=None 
):
    """
    Xử lý dữ liệu chấm công cho 1 user trong 1 ngày cụ thể
    """
    print(f"\n🔄 Xử lý dữ liệu ngày {target_date} cho user: {user_email}")
    print("=" * 80)
    
    # Lấy dữ liệu từ database
    raw_data = await _get_input_data( db_pool, user_email, target_date)
    
    if not raw_data:
        print(f"⚠️  Không tìm thấy dữ liệu cho {user_email} ngày {target_date}")
        return None
    
    # Chuẩn bị dữ liệu đầu vào cho hàm process_daily_attendance
    input_data = {
        'date': str( target_date ),
        'check_in': checkin_time,
        'check_out': checkout_time, 
        'is_leave_morning': raw_data[ 'leave_morning' ],
        'is_leave_afternoon': raw_data[ 'leave_afternoon' ],
    }
    
    # Gọi hàm xử lý chấm công
    processed_result = process_daily_attendance( input_data, raw_data[ 'free_allowance' ] )
    
    # Kết hợp dữ liệu gốc và kết quả xử lý
    final_result = {
        'user_email': user_email,
        'date': target_date,
        'checkin_time': checkin_time,
        'checkout_time': checkout_time,
        'leave_morning': raw_data['leave_morning'],
        'leave_afternoon': raw_data['leave_afternoon'],
        'initial_free_allowance': raw_data['free_allowance'],
        **processed_result
    }
    
    # In kết quả
    print(
        f"📅 Date: {target_date} | "
        f"CheckIn: {checkin_time or 'N/A'} | CheckOut: {checkout_time or 'N/A'} | "
        f"Violation: {processed_result['violation_minutes']} mins | "
        f"Deduct: {processed_result['deduction_hours']} hrs | "
        f"Late morning: {'Yes' if processed_result['is_late_morning'] else 'No'} | "
        f"Early afternoon: {'Yes' if processed_result['is_early_afternoon'] else 'No'} | "
        f"Free allowance: {raw_data['free_allowance']} → {processed_result['free_allowance']}"
    )
    
    return final_result

def extract_date_from_filename(filename):
    """
    Trích xuất ngày từ tên file (VD: filtered_2025-08-20.json -> 2025-08-20)
    """
    try:
        # Tìm pattern YYYY-MM-DD trong tên file
        date_str = filename.split('_')[1].split('.')[0]  # filtered_2025-08-20.json -> 2025-08-20
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return None

async def process_json_file(db_pool, json_file_path, target_emails=None):
    """
    Xử lý dữ liệu từ file JSON cho các user được chỉ định
    """
    print(f"\n📁 Đang xử lý file: {json_file_path}")
    
    # Đọc dữ liệu từ file JSON
    with open( json_file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        if not json_data:
            print("⚠️  Không có dữ liệu trong file JSON")
            return
        
        # Trích xuất ngày từ tên file
        filename = Path(json_file_path).name
        date_str = filename.split('_')[1].split('.')[0] # filtered_2025-08-20.json -> 2025-08-20
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        print(f"📅 Ngày xử lý: {target_date}")
        
        # Lọc users theo email nếu được chỉ định
        if target_emails:
            filtered_data = [record for record in json_data if record['email'] in target_emails]
            print(f"🔍 Lọc được {len(filtered_data)}/{len(json_data)} users")
        else:
            filtered_data = json_data
            print(f"📊 Xử lý toàn bộ {len(filtered_data)} users")
        
        results = []
        
        # Xử lý từng user
        for record in filtered_data:
            user_email = record['email']
            user_name = record['full_name']
            
            # Trích xuất thời gian checkin/checkout
            checkin_time = None
            checkout_time = None
            
            if record.get('first_in'):
                checkin_time = record['first_in'].split(' ')[1]  # "2025-08-20 08:40" -> "08:40"
            
            if record.get('last_out'):
                checkout_time = record['last_out'].split(' ')[1]  # "2025-08-20 19:40" -> "19:40"
            
            print(f"\n👤 Xử lý user: {user_name} ({user_email})")
            
            # Gọi hàm xử lý từng ngày
            result = await process_single_day(
                db_pool, 
                user_email, 
                target_date, 
                checkin_time, 
                checkout_time
            )
            
            if result:
                results.append(result)
            
        print(f"\n✅ Hoàn thành xử lý file {filename}: {len(results)} kết quả")
        return results

async def main():
    connection_url = "postgresql://postgres:Pa55w.rd@localhost:5432/attendance_processed"
    db_pool = DbConnPool()
    
    try:
        await db_pool.connect( connection_url )
        print( "✅ Kết nối thành công!" )
        
        # Đường dẫn đến file JSON 
        json_file = "/home/nguyen-duc-kien/OneDrive/My codespace/Work/CMC/AttendanceBot/packages/airflow/dags/etl/data/filtered_2025-08-20.json"
        
        # Danh sách email cần xử lý (có thể None để xử lý tất cả)
        target_emails = [
            'ndkien.ts@cmc.com.vn', 
            'ndgiang1@cmc.com.vn', 
            'pthieu5@cmc.com.vn',
            'dmdat@cmc.com.vn', 
            'qthung@cmc.com.vn'
        ]
        
        # Xử lý file JSON
        results = await process_json_file(db_pool, json_file, target_emails)
        
        if results:
            print(f"\n🎉 Tổng kết: Đã xử lý thành công {len(results)} bản ghi")
        
    except Exception as e:
        print( f"❌ Error: { e }" )
    finally:
        await db_pool.close()

if __name__ == "__main__":
    asyncio.run( main() )
