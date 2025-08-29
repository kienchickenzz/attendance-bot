from constants import SHIFT_CONFIG, RULES

def _to_minutes( time_str: str ) -> int:
    hours, minutes = map( int, time_str.split( ":" ) )
    return hours * 60 + minutes


def _diff_minutes( later: str, earlier: str ) -> int:
    return max( 0, _to_minutes( later ) - _to_minutes( earlier ) )


def _get_shift_type( is_leave_morning: bool, is_leave_afternoon: bool ) -> str:
    if is_leave_morning and is_leave_afternoon:
        return "leave_full_day"
    if is_leave_morning:
        return "leave_morning"
    if is_leave_afternoon:
        return "leave_afternoon"
    return "normal"


def process_daily_attendance( daily_record: dict, free_allowance: int = 0 ) -> dict:
    """
    Xử lý dữ liệu chấm công của một ngày
    
    Args:
        daily_record: Dictionary chứa thông tin chấm công:
            - check_in: Giờ check in (HH:MM)
            - check_out: Giờ check out (HH:MM)
            - is_leave_morning: Có nghỉ sáng không
            - is_leave_afternoon: Có nghỉ chiều không
        free_allowance: Số lần được miễn trừ vi phạm (cho vi phạm 1-15 phút)
    
    Returns:
        Dictionary chứa kết quả xử lý:
            - morning_violation: Số phút vi phạm buổi sáng
            - afternoon_violation: Số phút vi phạm buổi chiều
            - violation_minutes: Tổng số phút vi phạm
            - deduction_hours: Số giờ bị khấu trừ
            - initial_free_allowance: Số lần miễn trừ lúc đầu
            - free_allowance: Số lần miễn trừ còn lại
            - is_late_morning: Có đi muộn buổi sáng không
            - is_early_afternoon: Có về sớm buổi chiều không
    """
    check_in = daily_record.get("check_in")
    check_out = daily_record.get("check_out")
    is_leave_morning = daily_record.get("is_leave_morning", False)
    is_leave_afternoon = daily_record.get("is_leave_afternoon", False)
    
    shift_type = _get_shift_type(is_leave_morning, is_leave_afternoon)
    
    # Nếu nghỉ cả ngày thì không tính vi phạm
    if shift_type == "leave_full_day":
        return {
            "morning_violation": 0,
            "afternoon_violation": 0,
            "violation_minutes": 0,
            "deduction_hours": 0,
            "initial_free_allowance": free_allowance,
            "free_allowance": free_allowance,
            "is_late_morning": False,
            "is_early_afternoon": False
        }
    
    ref_in = SHIFT_CONFIG[ shift_type ][ "check_in_reference" ]
    ref_out = SHIFT_CONFIG[ shift_type ][ "check_out_reference" ]
    
    violation_minutes = 0
    morning_violation = 0
    afternoon_violation = 0
    
    # Tính vi phạm buổi sáng (đến muộn)
    if check_in and ref_in:
        morning_violation = _diff_minutes(check_in, ref_in)
        violation_minutes += morning_violation
    
    # Tính vi phạm buổi chiều (về sớm)
    if check_out and ref_out:
        afternoon_violation = _diff_minutes(ref_out, check_out)
        violation_minutes += afternoon_violation
    
    is_late_morning = morning_violation > 0
    is_early_afternoon = afternoon_violation > 0
    
    # Tìm rule phù hợp với tổng phút vi phạm
    rule = None
    for r in RULES:
        if r["min"] <= violation_minutes <= r["max"]:
            rule = r
            break
    
    # Nếu không có rule phù hợp (không vi phạm hoặc vi phạm quá lớn)
    if not rule:
        return {
            "morning_violation": morning_violation,
            "afternoon_violation": afternoon_violation,
            "violation_minutes": violation_minutes,
            "deduction_hours": 0,
            "initial_free_allowance": free_allowance,
            "free_allowance": free_allowance,
            "is_late_morning": is_late_morning,
            "is_early_afternoon": is_early_afternoon
        }
    
    # Tính số giờ khấu trừ
    deduction_hours = rule["deduct"](free_allowance)
    updated_free_allowance = free_allowance
    
    # Cập nhật free allowance nếu vi phạm 1-15 phút và còn allowance
    if rule["min"] == 1 and rule["max"] == 15 and free_allowance > 0:
        updated_free_allowance = free_allowance - 1
    
    return {
        "morning_violation": morning_violation,
        "afternoon_violation": afternoon_violation,
        "violation_minutes": violation_minutes,
        "deduction_hours": deduction_hours,
        "initial_free_allowance": free_allowance,
        "free_allowance": updated_free_allowance,
        "is_late_morning": is_late_morning,
        "is_early_afternoon": is_early_afternoon
    }
