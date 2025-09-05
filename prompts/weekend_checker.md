Dựa vào ngữ cảnh hiện tại, hãy xác định xem toàn bộ các ngày trong danh sách các khoảng thời gian/ngày cụ thể mà người dùng đưa vào có phải là cuối tuần (thứ 7, CN) hay không.

Ngữ cảnh hiện tại:
- Ngày hiện tại: {{ current_time }}

- Danh sách các khoảng thời gian/ngày cụ thể mà người dùng đưa vào:
{{ query_time_str }}


Quy tắc xác định:

- Với mỗi dòng trong danh sách các khoảng thời gian/ngày cụ thể mà người dùng đưa vào:
    - Nếu là dạng "Từ YYYY-MM-DD đến YYYY-MM-DD": xác định toàn bộ các ngày trong khoảng.
    - Nếu là dạng "Ngày YYYY-MM-DD": coi đây là khoảng thời gian với start_date = end_date, tức chỉ có duy nhất ngày đó.
- Để xác định xem một ngày cụ thể là thứ mấy:
    - Bắt đầu từ "Ngày hiện tại" ({{ current_time }}) và ngày trong input.
    - Tính số ngày chênh lệch giữa ngày input và ngày hiện tại.
    - Dựa trên thứ của ngày hiện tại, cộng/trừ số ngày chênh lệch để suy ra ngày trong tuần của ngày input.
    - Thứ trong tuần được tính theo chu kỳ 7 ngày: sau Chủ nhật thì quay lại Thứ 2.
- Sau khi đã xác định chính xác thứ trong tuần cho toàn bộ các ngày, gộp tất cả các ngày lại thành một tập hợp chung.
- Kiểm tra xem toàn bộ các ngày trong tập hợp này có đều rơi vào Thứ 7 hoặc Chủ nhật không.
    - Nếu tất cả đều là cuối tuần → "is_weekend": "True"
    - Nếu có ít nhất 1 ngày không phải cuối tuần → "is_weekend": "False"
- Chỉ trả về một object JSON duy nhất theo schema:
{
    "is_weekend": "True" | "False"
}
- Ví dụ:
    - Input:
        Từ 2025-07-01 đến 2025-07-15
        Từ 2025-08-01 đến 2025-08-05
        Ngày 2025-08-10
    - Output:
        {
            "is_weekend": "False"
        }


Yêu cầu đầu ra JSON:
- Hãy trả về DUY NHẤT một chuỗi JSON hợp lệ (không có văn bản giải thích, không có chú thích) với cấu trúc sau:
    - Top-level object có các trường:
        - "is_weekend": string - chỉ có thể nhận một trong hai giá trị chuỗi là "True" hoặc "False"

    - Ví dụ đầu ra hợp lệ:
        {
            "is_weekend": "True"
        }

        {
            "is_weekend": "False"
        }
