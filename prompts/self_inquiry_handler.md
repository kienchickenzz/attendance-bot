# Yêu cầu
Dựa vào ngữ cảnh hiện tại, hãy xác định xem người dùng đang hỏi về thông tin của chính họ hay hỏi về người khác.

# Ngữ cảnh hiện tại:
- Tên người dùng: {{ api_session.data.user_name }}
- Email người dùng: {{ api_session.data.user_email }}

# Câu hỏi của người dùng: 
{{ raw_user_input }}

# Quy tắc xác định:
- Nếu câu hỏi không chứa tên hoặc email khác với {{ api_session.data.user_name }} và {{ api_session.data.user_email }} thì dù có hay không xuất hiện đại từ nhân xưng “tôi”, “của tôi”, “mình”,… vẫn xác định là Người dùng đang hỏi về chính mình.
- Nếu câu hỏi có chứa tên hoặc email khác với {{ api_session.data.user_name }} và {{ api_session.data.user_email }}, hoặc đề cập đến một người khác trong ngữ cảnh. Ví dụ: “giúp tôi xem điểm danh của Nguyễn Văn A”, “check in của tôi vào ngày sinh nhật của bạn tôi”, “email của anh B có thời gian check in là lúc nào”… Thì xác định là Người dùng đang hỏi về người khác.

# Yêu cầu đầu ra
- Sau khi hoàn tất các bước phân tích trên, hãy trả về DUY NHẤT một chuỗi (string) hợp lệ, không kèm bất kỳ văn bản hay chú thích nào khác. Giá trị trả về chỉ được phép là một trong hai:
    - "Yes" → nếu xác định người dùng đang hỏi về người khác (out of scope).
    - "No" → nếu xác định người dùng đang hỏi về chính họ (không out of scope).
