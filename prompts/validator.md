Dựa vào ngữ cảnh hiện tại cũng như câu trả lời trước đó của llm, hãy xác định xem câu trả lời mà llm trước đó đưa ra đã phù hợp chưa.

Ngữ cảnh hiện tại:
- Ngày hiện tại: {{ current_time }}
- Khoảng thời gian mà người dùng đang nhắc đến trong câu hỏi trước đó:
{{ time_query_in_string }}
- Chủ đề mà người dùng đang nhắc đến trong câu hỏi trước đó: {{ current_topic }}

- Câu hỏi trước đó của người dùng: {{ prev_question }}
- Câu trả lời cho câu hỏi trước đó: 
{{ prev_answer }}

- Câu hỏi của người dùng: {{ user_input }}
- Kết quả JSON của llm trước đó: {{ context }}

- Lưu ý:
    - Cặp câu hỏi và câu trả lời trước đó chỉ mang tính chất tham khảo và chỉ sử dụng nếu câu hỏi hiện tại yêu cầu liên kết với mốc thời gian đã được đề cập trong câu trước.
    - Ví dụ:
        - Câu 1: “Tuần vừa rồi có hôm nào tôi đi muộn không?”
        - Câu 2: “Thời gian check in những ngày đó?”
        → Ở câu 2, cần lấy mốc thời gian từ câu trả lời của câu 1 (“những ngày đó” = các ngày đi muộn trong tuần vừa rồi) để xác định chính xác khoảng thời gian.

Quy tắc xác định:
- Kiểm tra cấu trúc JSON
    - JSON phải có đúng 2 field:
        - "topic": string
        - "time_query": array các object {start_date, end_date} (format YYYY-MM-DD)
nếu sai cấu trúc thì "is_valid": "False"

- Xác định thời gian (time_query):
    - Nếu câu hỏi có ngày/tháng/năm, từ khóa chỉ mốc hoặc khoảng thời gian cụ thể/tương đối thì phải tạo cặp start_date, end_date phù hợp.
    - Nếu câu hỏi chứa nhiều mốc/khoảng → phải có nhiều cặp trong time_query.
    - Nếu câu hỏi dùng tham chiếu mơ hồ ("hôm đó", "những ngày đó") → time_query phải lấy từ ngữ cảnh trước.
    - Nếu không có thời gian → time_query là "Không có" hoặc giữ nguyên từ ngữ cảnh trước.
- Xác định chủ đề (topic):
    - Nếu câu hỏi về giờ vào/ra, check-in/out → "Thời gian Check-in / Check-out".
    - Nếu câu hỏi về đi muộn, về sớm, vi phạm → "Thông tin vi phạm".
    - Nếu câu hỏi về số ngày công, đủ công → "Ngày công".
    - Nếu câu hỏi không có chủ đề mới → dùng chủ đề ngữ cảnh trước; nếu cũng không có thì "Không có".
- Quan hệ thời gian & chủ đề:
    - Nếu câu hỏi chỉ nhắc đến thời gian mà không có chủ đề → "topic": "Không có".
    - Nếu có chủ đề nhưng thiếu thời gian → vẫn phải có time_query, lấy từ ngữ cảnh trước hoặc "Không có".
    - Nếu câu hỏi có cụm lọc ngày (“những ngày đủ công đó”, “những ngày đi muộn đó”) → không đổi topic, chỉ giới hạn time_query.

- Định dạng JSON hợp lệ:
    - Phải trả về object có 2 trường: "topic" (string), "time_query" (array các object {start_date, end_date}).
    - Ngày theo format YYYY-MM-DD.

Lưu ý:
- time_query từ LLM chỉ cần cover đầy đủ khoảng thời gian user hỏi, không quan trọng cách biểu diễn.
- Ví dụ: user hỏi từ 20–24/08, thì time_query có thể là 
[
    {"start_date": "2025-08-20", "end_date": "2025-08-24"}
] 
hoặc 
[
  {"start_date": "2025-08-20", "end_date": "2025-08-20"},
  {"start_date": "2025-08-21", "end_date": "2025-08-21"},
  {"start_date": "2025-08-22", "end_date": "2025-08-22"},
  {"start_date": "2025-08-23", "end_date": "2025-08-23"},
  {"start_date": "2025-08-24", "end_date": "2025-08-24"}
]
thì cả hai đều hợp lệ còn không cover đầy đủ thì tính là không hợp lệ.

Yêu cầu đầu ra JSON:
- Sau khi hoàn tất các bước phân tích, xác định trên, hãy trả về DUY NHẤT một chuỗi JSON hợp lệ (không có văn bản giải thích, không có chú thích) với cấu trúc sau:
    - Top-level object có các trường:
        - "is_valid": string - chỉ có thể nhận một trong hai giá trị chuỗi là "True" hoặc "False"

    - Ví dụ đầu ra hợp lệ:
        {
            "is_valid": "True"
        }

        {
            "is_valid": "False"
        }
