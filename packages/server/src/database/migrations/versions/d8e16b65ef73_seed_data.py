"""seed data

Revision ID: d8e16b65ef73
Revises: f61b830206e2
Create Date: 2025-08-05 11:21:44.609588

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


from datetime import datetime, timedelta
import random

def calculate_attendance_count(checkin_time, checkout_time, work_start_hour=8, work_start_minute=15, 
                             work_end_hour=17, work_end_minute=30):
    """
    Returns:
        float: Attendance count (0.0 to 1.0)
    """
    # Define expected work schedule for this date
    expected_start = checkin_time.replace(hour=work_start_hour, minute=work_start_minute, 
                                        second=0, microsecond=0)
    expected_end = checkin_time.replace(hour=work_end_hour, minute=work_end_minute, 
                                      second=0, microsecond=0)
    
    # Calculate actual work duration
    actual_start = max(checkin_time, expected_start)  # Can't work before expected start
    actual_end = min(checkout_time, expected_end)     # Can't work after expected end
    
    # Handle case where someone checks in after expected end or checks out before expected start
    if actual_start >= actual_end:
        actual_work_minutes = 0
    else:
        actual_work_minutes = (actual_end - actual_start).total_seconds() / 60
    
    # Calculate expected work duration (standard work day)
    expected_work_minutes = (expected_end - expected_start).total_seconds() / 60
    
    # Calculate absence duration
    absence_minutes = expected_work_minutes - actual_work_minutes
    absence_hours = absence_minutes / 60
    
    # Apply attendance rules based on absence duration
    if absence_minutes <= 15:
        return 1.0          # Full day - no significant absence
    elif absence_hours <= 2:
        return 0.75         # Deduct 1/4 day
    elif absence_hours <= 4:
        return 0.5          # Deduct 1/2 day  
    elif absence_hours <= 6:
        return 0.25         # Deduct 3/4 day
    else:
        return 0.0          # Deduct full day

def generate_attendance_data( 
    start_date, end_date, user_email="ndkien.ts@cmc.com.vn", user_name="Nguyen Duc Kien" 
):

    start_dt = datetime.strptime( start_date, '%Y-%m-%d' )
    end_dt = datetime.strptime( end_date, '%Y-%m-%d' )
    
    attendance_records = []
    current_date = start_dt
    
    while current_date <= end_dt:
        if current_date.weekday() < 5:
            
            # Sinh giờ vào làm ngẫu nhiên quanh 8:15
            # Tạo biến động từ -15 đến +30 phút so với 8:15
            checkin_base = current_date.replace( hour=8, minute=15, second=0, microsecond=0 )
            checkin_variation = random.randint( -15, 30 )  # phút
            checkin_time = checkin_base + timedelta( minutes=checkin_variation )
            
            # Sinh giờ tan làm ngẫu nhiên quanh 17:30
            # Tạo biến động từ -20 đến +45 phút so với 17:30
            checkout_base = current_date.replace( hour=17, minute=30, second=0, microsecond=0 )
            checkout_variation = random.randint( -20, 45 )  # phút
            checkout_time = checkout_base + timedelta( minutes=checkout_variation )

            deadline = current_date.replace( hour=8, minute=15, second=0, microsecond=0 )
            is_late = checkin_time > deadline

            attendance_count = calculate_attendance_count( checkin_time, checkout_time )
            
            attendance_record = {
                "user_email": user_email,
                "user_name": user_name,
                "checkin_time": checkin_time.strftime( '%Y-%m-%dT%H:%M:%S.000Z' ),
                "checkout_time": checkout_time.strftime( '%Y-%m-%dT%H:%M:%S.000Z' ),
                "is_late": is_late,
                "attendance_count": attendance_count,
            }
            
            attendance_records.append( attendance_record )
        
        current_date += timedelta( days=1 ) # Move to next day
    
    return attendance_records


# revision identifiers, used by Alembic.
revision: str = 'd8e16b65ef73'
down_revision: Union[str, Sequence[str], None] = 'f61b830206e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    connection = op.get_bind()

    metadata = sa.MetaData()
    employee_attendance = sa.Table(
        'employee_attendance',
        metadata,
        sa.Column( 'id', sa.Integer, primary_key=True ),
        sa.Column( 'user_email', sa.String( 255 ), nullable=False ),
        sa.Column( 'user_name', sa.String( 255 ), nullable=False ),
        sa.Column( 'checkin_time', sa.DateTime, nullable=False ),
        sa.Column( 'checkout_time', sa.DateTime, nullable=True ),
        sa.Column( 'is_late', sa.Boolean, default=False ),
        sa.Column( 'attendance_count', sa.Integer, default=False ),
    )

    start_date = "2025-06-01"
    end_date = "2025-08-31"
    demo_records = generate_attendance_data( start_date, end_date )
    
    connection.execute(
        employee_attendance.insert(),
        demo_records
    )
    print( f"Successfully inserted { len( demo_records ) } attendance records" )


def downgrade() -> None:
    """Downgrade schema."""
    connection = op.get_bind()
    
    connection.execute(
        sa.text( """
            DELETE FROM employee_attendance 
            WHERE user_email = 'ndkien.ts@cmc.com.vn'
        """ )
    )
    print( "Successfully removed demo attendance records for user email ndkien.ts@cmc.com.vn" )
