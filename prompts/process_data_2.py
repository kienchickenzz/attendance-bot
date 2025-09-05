attendance_data = {{ attendance_data }}

def process_data(attendance_data):
    # Khởi tạo biến thống kê
    total_attendance = 0.0  # Đổi thành float để tính tổng chính xác
    full_days = 0
    partial_days = 0  # Đổi tên từ half_days thành partial_days vì không chỉ có 0.5
    total_working_days = 0
    total_actual_hours = 0.0  # Thêm biến để tính tổng giờ làm việc thực tế
    total_deduction_hours = 0.0

    full_day_dates = []
    partial_day_dates = []  # Lưu cả ngày và hệ số công tương ứng

    # Xử lý dữ liệu - duyệt qua từng bản ghi để tính toán và phân loại
    for record in attendance_data["data"]:
        working_days = float( record.get("workingDays", 0) )
        actual_hours = float( record.get("actualHours", 0) )
        deduction_hours = float( record.get("deductionHours", 0) )
        date = record.get("date", "")
        
        # Cộng dồn các giá trị tổng
        total_attendance += working_days
        total_actual_hours += actual_hours
        total_deduction_hours += deduction_hours
        total_working_days += 1

        # Phân loại dựa trên hệ số workingDays
        # Ngày đủ công: workingDays >= 1.0 (hoặc gần bằng 1.0 do làm tròn số thực)
        if working_days >= 0.99:  # Sử dụng 0.99 thay vì 1.0 để tránh lỗi làm tròn số thực
            full_days += 1
            full_day_dates.append(date)
        # Ngày làm một phần: workingDays > 0 nhưng < 1.0
        elif working_days > 0:
            partial_days += 1
            # Lưu cả ngày và hệ số công để hiển thị chi tiết
            partial_day_dates.append((date, working_days, actual_hours))

    # Tạo nội dung summary với thông tin chi tiết hơn
    summary_parts = []
    
    # Thông tin tổng quan
    summary_parts.append(f"Tổng số ngày công: {total_attendance:.3f}")  # Hiển thị 3 số thập phân
    summary_parts.append("")
    summary_parts.append(f"Tổng số giờ công bị trừ: {total_deduction_hours:.3f}")  # Hiển thị 3 số thập phân
    summary_parts.append("")
    summary_parts.append(f"Tổng số giờ công (giờ làm việc): {total_actual_hours:.1f} giờ")
    summary_parts.append("")
    
    # Chi tiết ngày làm đủ công
    summary_parts.append(f"Số ngày làm đủ công (≥1.0): {full_days}")
    for idx, date in enumerate(full_day_dates, start=1):
        summary_parts.append(f"  {idx}. {date}")
    summary_parts.append("")

    # Chi tiết ngày làm một phần công
    summary_parts.append(f"Số ngày làm một phần công (<1.0): {partial_days}")
    for idx, (date, working_days, actual_hours) in enumerate(partial_day_dates, start=1):
        # Hiển thị thông tin chi tiết: ngày, hệ số công, số giờ thực tế
        summary_parts.append(f"  {idx}. {date} - {working_days:.3f} công ({actual_hours}h)")

    # Ghép thành chuỗi kết quả
    final_summary = "\n".join(summary_parts)
    return final_summary

print( process_data( attendance_data ) )
