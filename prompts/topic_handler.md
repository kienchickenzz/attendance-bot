Dựa vào ngữ cảnh hiện tại, hãy phân tích câu hỏi của người dùng để đưa ra phản hồi phù hợp.

Ngữ cảnh hiện tại:
- Ngày hiện tại: {{ api_session.data.current_time }}
- Khoảng thời gian mà người dùng đang nhắc đến:
{{ api_session.data.time_query_str }}
- Chủ đề mà người dùng đang nhắc đến: {{ api_session.data.topic }}
- Câu hỏi trước đó của người dùng: {{ api_session.data.prev_question }}
- Câu trả lời cho câu hỏi trước đó: 
{{ api_session.data.prev_answer }}
- Lưu ý:
    - Cặp câu hỏi và câu trả lời trước đó chỉ mang tính chất tham khảo và chỉ sử dụng nếu câu hỏi hiện tại yêu cầu liên kết với mốc thời gian đã được đề cập trong câu trước.
    - Ví dụ:
        - Câu 1: “Tuần vừa rồi có hôm nào tôi đi muộn không?”
        - Câu 2: “Thời gian check in những ngày đó?”
        → Ở câu 2, cần lấy mốc thời gian từ câu trả lời của câu 1 (“những ngày đó” = các ngày đi muộn trong tuần vừa rồi) để xác định chính xác khoảng thời gian.

Câu hỏi của người dùng: {{ user_input }}

Quy tắc xử lí tuần tự: (Phải thực hiện tuần tự các bước từ 1 đến 3, không được bỏ qua hoặc hoán đổi thứ tự. Chỉ khi hoàn tất bước trước đó thì mới được chuyển sang bước tiếp theo.)

1. Nhận diện thông tin chủ đề trong câu hỏi
- Nếu người dùng có đề cập đến chủ đề ví dụ như:
    - “Hôm qua tôi đi muộn không?”
    - “Thời gian check in của tôi thứ 4 tuần trước là lúc nào?”
    - “Tôi được bao nhiêu ngày công trong tuần này?”
    - “Ngày 1/8 tôi có bị đi muộn không?”
thì xác định Có đề cập đến chủ đề và chuyển sang **Bước 2**
- Nếu người dùng không đề cập đến bất kỳ chủ đề nào ở trên, hoặc chỉ nói đến thời gian chung chung mà không gắn với chủ đề, ví dụ:
    - “Hôm nay thì sao?”
    - “Hôm trước thì thế nào?”
    - “Thứ 7 tuần trước thì sao?”
    - "Thứ 2 vừa rồi thì sao?"
    - "Thứ 3 vừa qua thì thế nào"
    - "Thứ 3 tuần trước nữa?"
thì xác định Không đề cập đến chủ đề và chuyển sang **Bước 3** luôn

2. Xác định chủ đề:
- Nếu người dùng hỏi về thời gian check-in / check-out cụ thể trong ngày. Ví dụ:
    - Hôm qua tôi vào làm lúc mấy giờ?
    - Ngày 10/7 tôi chấm công mấy giờ?
    - Hôm nay tôi có quên chấm công không?
    - Thời gian check-in hôm kia của tôi là mấy giờ?
    - Hôm trước tôi check out lúc nào?
    - Thời gian check in, out của tôi?
    - Còn thời gian check out thì thế nào?
thì xác định chủ đề là "Thời gian Check-in / Check-out" và trả về luôn, không cần chuyển sang **Bước 3**
- Nếu người dùng hỏi về thông tin vi phạm (bao gồm cả đi muộn, về sớm, và số giờ/phút vi phạm). Ví dụ:
    - Tháng trước tôi đi muộn bao nhiêu ngày?
    - Tuần trước tôi về sớm mấy lần?
    - Tuần vừa rồi tôi bị trừ bao nhiêu phút vì đi trễ?
    - Tôi có bị tính đi trễ ngày nào trong tuần trước không?
    - Tổng số lần đi trễ của tôi trong tháng 6 là bao nhiêu?
    - Tổng thời gian vi phạm tuần trước là bao nhiêu?
    - Thời gian vi phạm của tôi hôm qua?
    - Vậy là có bị tính về sớm không?
    - Thế là có bị coi là đi muộn không?
    - Thế bị tính là đi muộn không? 

thì xác định chủ đề là "Thông tin vi phạm" và trả về luôn, không cần chuyển sang **Bước 7**
- Nếu người dùng hỏi về số ngày công hoặc việc đi làm đủ ngày. Ví dụ:
    - Tháng này tôi có bao nhiêu ngày công?
    - Tôi đi làm đủ công trong tháng 6 không?
    - Tổng số ngày công của tôi 2 tuần vừa rồi là bao nhiêu?
thì xác định chủ đề là "Ngày công" và trả về luôn, không cần chuyển sang **Bước 7**
- Lưu ý: 
    - Nếu trong câu hỏi vừa chứa thông tin về một chủ đề cụ thể (ví dụ: check-in/check-out, vi phạm) vừa có thêm cụm từ điều kiện lọc (ví dụ: “những ngày đủ công đó”, “các ngày đi muộn đó”), thì **ưu tiên xác định chủ đề chính theo câu hỏi gốc**. 
        - Các cụm như “ngày đủ công”, “ngày vi phạm”, “ngày đi muộn” chỉ dùng để **giới hạn tập ngày trong time_query**, không thay đổi topic.
        - Ví dụ:
            - Với câu hỏi: “Thời gian check in, out của tôi những ngày đủ công đó?” thì Topic = "Thời gian Check-in / Check-out" và Time_query = tập ngày đủ công đã xác định từ câu trước
    - Nếu câu hỏi thuộc loại nguyên nhân/giải thích (chứa từ khóa WHY-intent: vì sao, tại sao, do đâu, nguyên nhân, lý do, …) thì ưu tiên chủ đề “Thông tin vi phạm”, vì mọi nguyên nhân dẫn tới mất công hay sai lệch đều nằm ở layer “vi phạm”.

3. Nếu không xác định được chủ đề:
- Nếu ngữ cảnh hiện tại không có thông về Chủ đề mà người dùng đang nhắc đến thì trả về chuỗi "Không có"
- Nếu ngữ cảnh hiện tại đã có thông tin về Chủ đề mà người dùng đang nhắc đến thì BẮT BUỘC phải lấy thông tin đó làm chủ đề.

Yêu cầu đầu ra JSON:
- Sau khi hoàn tất các bước phân tích trên, hãy trả về DUY NHẤT một chuỗi JSON hợp lệ (không có văn bản giải thích, không có chú thích) với cấu trúc sau:
    - Top-level object có các trường:
        - "topic": string — giá trị chủ đề đã nhận diện ở Bước 1, 2, 3.

    - Ví dụ đầu ra hợp lệ:
        {
            "topic": "Thời gian Check-in / Check-out",
        }

        {
            "topic": "Ngày công",
        }
