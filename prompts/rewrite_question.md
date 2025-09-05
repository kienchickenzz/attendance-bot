Dựa vào ngữ cảnh hiện tại, viết lại câu hỏi của người dùng nếu cần thiết để đảm bảo sao cho câu hỏi được đầy đủ cả thông tin về thời gian và mục đích.

Ngữ cảnh hiện tại:
- Ngày hiện tại: {{ api_session.data.current_time }}
- Khoảng thời gian mà người dùng đang nhắc đến:
{{ api_session.data.time_query_str }}
- Chủ đề mà người dùng đang nhắc đến: {{ api_session.data.topic }}
- Câu hỏi trước đó của người dùng: {{ api_session.data.prev_question }}
- Câu trả lời cho câu hỏi trước đó: 
{{ api_session.data.prev_answer }}

Câu hỏi của người dùng: {{ raw_user_input }}

Quy tắc xử lý:
1. Nếu có thể xác định đầy đủ cả thời gian và mục đích từ câu hỏi hiện tại hoặc ngữ cảnh trước đó → viết lại câu hỏi một cách rõ ràng, tự nhiên.
2. Nếu không thể viết lại đầy đủ (thiếu cả thời gian lẫn mục đích, hoặc mơ hồ không có cách bổ sung) → trả về chuỗi "No".

Lưu ý: Theo quy định của công ty thì 1 tháng được hiểu là từ ngày 25 của tháng này đến ngày 26 của tháng sau, chứ không phải từ ngày 1 đến ngày cuối tháng.

Ví dụ:
User: "Trong tháng 8 tôi có bao nhiêu ngày đi muộn?"
Output: "Trong tháng 8 (từ ngày 25/07 đến ngày 26/08) tôi có bao nhiêu ngày đi muộn?"

User: "Hôm qua thì sao?"  
Output: "Hôm qua tôi check in lúc mấy giờ?"

User: "Thế có bị tính đi muộn không?" (ngữ cảnh trước đó: đã hỏi về tuần trước)  
Output: "Trong tuần trước tôi có bị tính đi muộn không?"

User: "Ngày 10/8 tôi đi làm lúc nào?"  
Output: "Ngày 10/8 tôi đi làm lúc nào?"

User: "Còn hôm đó thì thế nào?" (không có ngữ cảnh trước)  
Output: "No"