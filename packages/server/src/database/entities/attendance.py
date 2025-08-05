from sqlalchemy import Column, Integer, String, DateTime, Boolean

from database.entities.utils.base import Base

class EmployeeAttendance( Base ):
    __tablename__ = "employee_attendance"

    id = Column( Integer, primary_key=True, index=True, autoincrement=True )
    user_email = Column( String( 255 ), nullable=False, index=True )
    user_name = Column( String( 255 ), nullable=False )
    checkin_time = Column( DateTime, nullable=False )
    checkout_time = Column( DateTime, nullable=True )
    is_late = Column( Boolean, default=False )
    attendance_count = Column( Integer, nullable=False )
