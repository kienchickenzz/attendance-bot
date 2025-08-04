"""seed_data_2

Revision ID: 4a978286506a
Revises: 51e10d436bd2
Create Date: 2025-08-04 13:24:07.204749

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


from datetime import datetime, timedelta
import random

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
            
            attendance_record = {
                "user_email": user_email,
                "user_name": user_name,
                "checkin_time": checkin_time.strftime( '%Y-%m-%dT%H:%M:%S.000Z' ),
                "checkout_time": checkout_time.strftime( '%Y-%m-%dT%H:%M:%S.000Z' ),
                "is_late": is_late
            }
            
            attendance_records.append( attendance_record )
        
        current_date += timedelta( days=1 ) # Move to next day
    
    return attendance_records



# revision identifiers, used by Alembic.
revision: str = '4a978286506a'
down_revision: Union[str, Sequence[str], None] = '51e10d436bd2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Upgrade schema."""

    connection = op.get_bind()

    metadata = sa.MetaData()
    employee_attendance = sa.Table(
        'employee_attendance',
        metadata,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_email', sa.String(255), nullable=False),
        sa.Column('user_name', sa.String(255), nullable=False),
        sa.Column('checkin_time', sa.DateTime, nullable=False),
        sa.Column('checkout_time', sa.DateTime, nullable=True),
        sa.Column('is_late', sa.Boolean, default=False),
    )

    start_date = "2025-06-01"
    end_date = "2025-08-31"
    demo_records = generate_attendance_data(start_date, end_date, user_email="ndgiang1@cmc.com.vn", user_name="Nguyen Dinh Giang")
    
    if demo_records:
        connection.execute(
            employee_attendance.insert(),
            demo_records
        )
        print(f"Successfully inserted {len(demo_records)} attendance records")


def downgrade() -> None:
    """Downgrade schema."""
    connection = op.get_bind()
    
    connection.execute(
        sa.text("""
            DELETE FROM employee_attendance 
            WHERE user_email = 'duckien@gmail.com'
        """)
    )
    print("Successfully removed demo attendance records")
