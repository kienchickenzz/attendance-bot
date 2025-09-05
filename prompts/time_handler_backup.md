Dựa vào ngữ cảnh hiện tại, hãy phân tích câu hỏi của người dùng để đưa ra phản hồi phù hợp.

Ngữ cảnh hiện tại:
- Ngày hiện tại: {{ api_session.data.current_time }}
- Khoảng thời gian mà người dùng đang đề cập đến:
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

Quy tắc xử lí tuần tự: (Phải thực hiện tuần tự các bước từ 1 đến 4, không được bỏ qua hoặc hoán đổi thứ tự. Chỉ khi hoàn tất bước trước đó thì mới được chuyển sang bước tiếp theo.)

1. Nhận diện thông tin thời gian trong câu hỏi
- Nếu người dùng có đề cập đến thông tin thời gian bao gồm ngày, tháng, năm, tuần, hoặc các từ khóa chỉ mốc thời gian cụ thể hoặc tương đối như:
    - “hôm nay”, “ngày mai”, “hôm qua”
    - “thứ 3 vừa qua”, “thứ 3 tuần này”, “hôm thứ 3”, “hôm thứ 3 vừa rồi”
    - “tuần này”, “tháng trước”, “quý này”
    - “ngày 1/8”, “tháng 7”, “năm 2025”
    - “lúc 8 giờ”, “9h sáng”, “chiều nay”
    - “trong 3 ngày gần đây”, “7 ngày qua”, “cuối tuần”
    - “tháng [số] này”, “tháng này”, “tháng vừa rồi”, “tháng vừa qua”
thì chuyển sang **Bước 2**
- Nếu người dùng không đề cập đến bất kỳ thông tin thời gian nào (tức là câu hỏi không chứa ngày, tháng, năm, tuần, hoặc các từ khóa chỉ mốc thời gian cụ thể/tương đối như trên), thì xác định là Không đề cập đến thời gian và chuyển sang **Bước 4**.
    - Quy tắc này áp dụng cho mọi loại câu hỏi (check-in, check-out, vi phạm, ngày công, …). Chỉ cần không xuất hiện thông tin thời gian, coi như Không có thời gian.
- Ngoài ra, nếu câu hỏi có chứa các từ khóa chỉ thời gian mơ hồ, không xác định rõ ràng như:
    - “hôm ấy”, “hôm đấy”, “hôm đó”, “ngày hôm đó”
    - “tuần đấy”, “tháng đấy”, “tháng đó”
    - "những ngày đó", "những hôm đấy", "những hôm ấy"
hoặc các biến thể tương tự: “lúc đó”, “dạo ấy”, “thời điểm ấy”
thì chuyển sang **Bước 4**

2. Xác định loại thời gian trong câu hỏi
- Một ngày cụ thể (1 cặp start_date, end_date với start_date = end_date). 
    - Ví dụ:
        - Hôm nay tôi check-in chưa?
        - Ngày 10 tháng 7 tôi vào làm mấy giờ?
        - Tôi có quên chấm công hôm qua không?
        - Giờ check out hôm kia là lúc nào?
        - Thứ 3 tuần trước tôi check in lúc nào?
        - Thứ 5 tuần trước nữa tôi check out mấy giờ?
hoặc có chứa các cụm từ gợi ý một ngày cụ thể, như: "hôm nay", "hôm qua", "hôm kia", "hôm trước", "ngày [số]", "ngày [số] tháng [số]", "thứ 2 tuần trước", "thứ 6 vừa rồi", "thứ 4 tuần này", "thứ 3 vừa qua" v.v.
- Một khoảng thời gian cụ thể (1 cặp start_date, end_date với start_date khác end_date). 
    - Ví dụ:
        - “Trong tháng 6 tôi đi làm mấy giờ mỗi ngày?”
        - “Từ ngày 3/8 đến 18/8 tôi có đi làm đầy đủ không?”
        - Trong tháng 6 tôi đi làm mấy giờ mỗi ngày?
        - Thời gian check-in của tôi tuần vừa rồi?
        - Có ngày nào trong 2 tuần vừa rồi tôi quên chấm công không?
        - Từ ngày 3/8 đến 18/8 tôi có đi làm đầy đủ không?
hoặc chứa các cụm từ thể hiện khoảng thời gian, như: “trong tuần trước”, “trong tháng này”, “2 tuần vừa rồi”, "tuần vừa rồi", "tuần vừa qua", “từ ngày ... đến ngày ...”, “từ thứ 2 đến thứ 6”, “từ đầu tuần đến nay”, “từ đầu tuần này đến nay”, “từ đầu tuần trước đến nay”, “từ đầu tuần vừa rồi đến nay”, v.v.
- Nhiều khoảng/mốc thời gian cụ thể (nhiều cặp start_date, end_date). 
    - Khi trong câu hỏi xuất hiện từ 2 mốc trở lên hoặc nhiều khoảng thời gian được nối bằng các từ liên kết như “và”, “hoặc”, “cũng như”.
    - Ví dụ:
        - Câu "Mùng 10, 12, 15 tháng trước tôi check in lúc nào?" có 3 ngày cụ thể
        - Câu "Các ngày 10, 12, 15 của tháng vừa rồi tôi có đi muộn không?" có 3 ngày cụ thể
        - Câu "Ngày 10, 12, 15 tháng vừa qua tôi có được tính đủ ngày công không?" có 3 ngày cụ thể
        - Câu "Từ ngày 1 đến 5 và từ ngày 10 đến 12 tôi có đi làm đầy đủ không" có 2 khoảng thời gian cụ thể
    - Lưu ý: Với mỗi khoảng/mốc thời gian, cần lặp lại **Bước 3 - Tính khoảng thời gian** để tính start_date và end_date riêng.
- Sau khi xác định được loại thời gian thì chuyển sang **Bước 3**

3. Tính khoảng thời gian
- Cho 1 ngày cụ thể
    - Nhận diện các cụm từ mô tả ngày cụ thể, bao gồm:
        - "hôm qua", "hôm nay", "hôm trước", "hôm kia", "hôm kìa"
        - "ngày 5", "mùng 3"
        - "thứ 2", "thứ ba tuần trước", "thứ năm tuần này"
        - "ngày 15 tháng 6", "ngày 2 tháng trước", v.v.
    - Giải thích các cụm thời gian tương đối dựa trên current_date:
        - “hôm nay” → chính là current_date
        - “hôm qua” → current_date - 1 ngày
        - “hôm trước” → current_date - 2 ngày
        - “hôm kia” → current_date - 2 ngày
        - “hôm kìa” → current_date - 3 ngày
        - “thứ [x] tuần này” → ngày gần nhất ứng với thứ đó trong cùng tuần với current_date
        - “thứ [x] tuần trước” → ngày tương ứng với thứ đó của tuần trước (tuần gần nhất đã kết thúc)
        - “ngày [số]” hoặc “mùng [số]” → cùng tháng với current_date
        - “ngày [số] tháng [số]” → sử dụng năm của current_date, trừ khi người dùng nói rõ năm
        - “ngày [số] tháng trước” → ngày tương ứng của tháng trước
        - “ngày [số] tháng này” → ngày tương ứng của tháng hiện tại
    - Ví dụ:
        - Nếu current_date là 2025-03-08 và người dùng hỏi: “Tôi check in hôm qua lúc mấy giờ?” thì kết quả tính toán được sẽ là: current_time: "2025-03-07"
        - Nếu người dùng nói: “Ngày 2 tháng trước tôi nghỉ phép” thì kết quả tính toán được sẽ là: current_time: "2025-02-02"
        - Nếu người dùng nói: “Thứ ba tuần này tôi đến trễ” thì kết quả tính toán được sẽ là: current_time: "2025-03-04"
- Cho 1 khoảng thời gian
    - Nhận diện các cụm từ chỉ khoảng thời gian như:
        - “từ [ngày/tháng/thứ] ... đến [ngày/tháng/thứ]”
        - “từ ngày ... đến ngày ...”
    - Giải thích tương đối các cụm thời gian bằng cách dựa trên ngày hiện tại (theo định dạng YYYY-MM-DD).
        - Nếu người dùng chỉ nói "từ mùng 1 đến mùng 6", hiểu là cùng tháng với ngày hiện tại (ví dụ: nếu ngày hiện tại là 2025-03-08 -> khoảng thời gian là 2025-03-01 đến 2025-03-06)
        - Nếu người dùng nói "từ thứ 3 tuần trước đến thứ 3 tuần này", sử dụng logic tính toán tuần để xác định đúng các ngày tương ứng
        - Nếu người dùng nói "từ 15 tháng trước đến 15 tháng này", lấy ngày 15 của tháng trước và tháng hiện tại dựa trên current_date
        - Nếu người dùng nói "tuần vừa rồi", "tuần trước" hoặc "tuần vừa qua", hiểu là từ thứ 2 đến thứ 6 của tuần gần nhất đã kết thúc
        - Nếu người dùng nói "2 tuần vừa rồi" hoặc "2 tuần qua", hiểu là từ thứ 2 của 2 tuần trước đến thứ 6 của tuần gần nhất đã kết thúc
        - Nếu người dùng nói “từ đầu tuần đến nay” hoặc “từ đầu tuần này đến nay” → start_date là thứ 2 của tuần hiện tại, end_date là ngày hiện tại (current_date).
        - Nếu người dùng nói “từ đầu tuần trước đến nay” hoặc “từ đầu tuần vừa rồi đến nay” → start_date là thứ 2 của tuần trước, end_date là ngày hiện tại (current_date).
        - Nếu người dùng nói "tuần trước nữa" hoặc "hai tuần trước" thì kết quả tính toán được sẽ là: từ thứ 2 đến Chủ nhật của tuần liền trước "tuần trước" (tức cách tuần hiện tại 2 tuần). Ví dụ: Nếu current_date là 2025-03-08 và người dùng hỏi "tuần trước nữa" → start_date = 2025-02-17, end_date = 2025-02-23.
    - Ví dụ:
        - Nếu current_date là 2025-03-08 và người dùng hỏi: "Từ mùng 1 đến mùng 6" thì kết quả tính toán được sẽ là: "start_date": "2025-03-01", "end_date": "2025-03-06"
        - Nếu current_date là 2025-03-08 và người dùng hỏi: "Từ 15 tháng trước đến 15 tháng này" thì kết quả tính toán được sẽ là: "start_date": "2025-02-15", "end_date": "2025-03-15"
        - Nếu current_date là 2025-03-08 và người dùng hỏi: "Từ thứ 3 tuần trước đến thứ 3 tuần này" thì kết quả tính toán được sẽ là: "start_date": "2025-02-25", "end_date": "2025-03-04" (do 25/2 là thứ Ba tuần trước, 4/3 là thứ Ba tuần này)
        - Nếu current_date là 2025-03-08 và người dùng hỏi: "tuần trước" thì kết quả tính toán được sẽ là: "start_date": "2025-02-24", "end_date": "2025-03-02"
        - Nếu current_date là 2025-03-08 và người dùng hỏi: "tuần này" thì kết quả tính toán được sẽ là: "start_date": "2025-03-03", "end_date": "2025-03-08"
        - Nếu current_date là 2025-03-08 và người dùng hỏi: "hai tuần vừa rồi" thì kết quả tính toán được sẽ là: "start_date": "2025-02-19", "end_date": "2025-03-04"
        - Nếu current_date là 2025-03-08 và người dùng hỏi: "ba ngày gần nhất" thì kết quả tính toán được sẽ là: "start_date": "2025-03-05", "end_date": "2025-03-07"
        - Nếu current_date là 2025-03-08 và người dùng hỏi: "ba ngày vừa qua" thì kết quả tính toán được sẽ là: "start_date": "2025-03-05", "end_date": "2025-03-07"
        - Nếu current_date là 2025-03-08 và người dùng hỏi: "tháng này" thì kết quả tính toán được sẽ là: "start_date": "2025-03-01", "end_date": "2025-03-08"
        - Nếu current_date là 2025-03-08 và người dùng hỏi: "tháng trước" thì kết quả tính toán được sẽ là: "start_date": "2025-02-01", "end_date": "2025-02-29"
        - Nếu current_date là 2025-03-08 và người dùng hỏi: "nửa đầu tháng này" thì kết quả tính toán được sẽ là: "start_date": "2025-03-01", "end_date": "2025-03-08"
- Kết thúc bước này:
    - Nếu là một ngày cụ thể hoặc một khoảng thời gian cụ thể duy nhất thì sau khi xác định được start_date và end_date.
    - Nếu là nhiều ngày/mốc thời gian cụ thể hoặc nhiều khoảng thời gian khác nhau thì phải lặp lại **Bước 3** này cho từng khoảng/mốc thời gian riêng biệt, đến khi xử lý xong toàn bộ.

4. Nếu không xác định được mốc thời gian
- Nếu ngữ cảnh hiện tại không có thông tin về Khoảng thời gian mà người dùng đang đề cập đến thì để trống giá trị cho time_query
- Nếu ngữ cảnh hiện tại đã có thông tin về Khoảng thời gian mà người dùng đang đề cập đến thì BẮT BUỘC phải lấy thông tin khoảng thời gian đó làm giá trị cho time_query. Tuy nhiên việc lấy thông tin về khoảng thời gian đó làm giá trị cho time_query cũng cần lưu ý điểm sau:
    - Nếu câu hỏi chứa các cụm tham chiếu trực tiếp (ví dụ: “hôm đó”, “hôm đấy”, “hôm ấy”, “ngày hôm đó”, “những ngày đó”, “tuần đó”, “tháng ấy”…) thì time_query sẽ lấy từ chính Khoảng thời gian mà người dùng đang đề cập.
    - Nếu câu hỏi chứa các cụm từ tham chiếu ngữ cảnh như:
        - “những ngày đó”, “những hôm đó”, “các ngày đó”
        - “những hôm đi muộn đó”, “những ngày đủ công đó”, “các ngày vi phạm đó”
        - hoặc biến thể tương tự: “các ngày ấy”, “những lúc đó”, …
        và đồng thời ngữ cảnh hiện tại đã có thông tin về Khoảng thời gian mà người dùng đang đề cập đến thì time_query sẽ không phải toàn bộ khoảng thời gian trước đó, mà chính là **tập con các ngày đã được kết quả câu hỏi trước xác định**. 
            - Ví dụ:
                - Câu trước: “Tuần vừa rồi tôi có bao nhiêu ngày đủ công?” thì kết quả là các ngày 2025-08-12, 2025-08-13, 2025-08-15.
                - Câu sau: “Thời gian check in, out của tôi những ngày đủ công đó?” thì time_query sẽ là các ngày 2025-08-12, 2025-08-13, 2025-08-15.


Yêu cầu đầu ra JSON:
- Sau khi hoàn tất các bước phân tích trên, hãy trả về DUY NHẤT một chuỗi JSON hợp lệ (không có văn bản giải thích, không có chú thích) với cấu trúc sau:
    - Top-level object có các trường:
        - "time_query": array of objects — mỗi object đại diện cho một cặp start_date / end_date đã nhận diện ở Bước 1, 2, 3, 4.

    - Schema cho time_query (mỗi phần tử):
        {
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
        }

    - Ví dụ đầu ra hợp lệ:
        {
            "time_query": [
                {
                    "start_date": "2025-08-07",
                    "end_date": "2025-08-07"
                }
            ]
        }

        {
            "time_query": [
                {
                    "start_date": "2025-07-01",
                    "end_date": "2025-07-15"
                }
            ]
        }
