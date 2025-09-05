attendance_data = {{ attendance_data }}

def process_data(attendance_data):
    summary_parts = []

    total_deduction_hours = 0
    total_violation_days = 0
    total_late_days = 0
    total_late_minutes = 0
    total_early_days = 0
    total_early_minutes = 0

    for record in attendance_data["data"]:
        checkin_violation = float( record.get("checkin_violation", 0) )
        checkout_violation = float( record.get("checkout_violation", 0) )
        deduction_hours = float( record.get("deduction_hours", 0) )

        if checkin_violation > 0 or checkout_violation > 0:
            total_violation_days += 1

        total_deduction_hours += deduction_hours
        if checkin_violation > 0:
            total_late_days += 1
            total_late_minutes += checkin_violation
        if checkout_violation > 0:
            total_early_days += 1
            total_early_minutes += checkout_violation

    # Chuỗi tổng hợp
    summary_header = (
        f"Tổng số ngày vi phạm bao gồm cả đi muộn và về sớm: {total_violation_days} ngày\n"
        f"Tổng số giờ công bị trừ: {total_deduction_hours}h\n"
        f"Tổng số ngày đi muộn: {total_late_days} (tổng {total_late_minutes} phút)\n"
        f"Tổng số ngày về sớm: {total_early_days} (tổng {total_early_minutes} phút)\n"
    )
    summary_parts.append(summary_header)

    for index, record in enumerate(attendance_data["data"]):
        # Xác định trạng thái dựa trên tổng số vi phạm
        total_violation = float( record.get("total_violation", 0) )
        if total_violation > 0:
            # Tạo thông tin chi tiết về vi phạm
            checkin_violation = float( record.get("checkin_violation", 0) )
            checkout_violation = float( record.get("checkout_violation", 0) )
            deduction_hours = float( record.get("deduction_hours", 0) )
            
            # Xây dựng chuỗi mô tả vi phạm
            violation_details = []
            if checkin_violation > 0:
                violation_details.append(f"đi muộn {checkin_violation} phút")
            else:
                violation_details.append("không đi muộn")

            if checkout_violation > 0:
                violation_details.append(f"về sớm {checkout_violation} phút")
            else:
                violation_details.append("không về sớm")

            violation_text = " và ".join(violation_details)
            status_text = f"Vi phạm: {violation_text} (trừ {deduction_hours}h)"
        else:
            status_text = "Không vi phạm (trừ 0h)"
        
        # Tạo chuỗi tóm tắt cho từng ngày
        summary_parts.append(f"Ngày: {record.get('date', 'không có')} - {status_text}")

        # Thêm dòng trống giữa các bản ghi (trừ bản ghi cuối cùng)
        if index < len(attendance_data["data"]) - 1:
            summary_parts.append("")

    final_summary = "\n".join(summary_parts)
    return final_summary

print( process_data( attendance_data ) )
