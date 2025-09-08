Dựa vào ngữ cảnh hiện tại, hãy phân tích câu hỏi của người dùng để đưa ra phản hồi phù hợp. 

Ngữ cảnh hiện tại: 
- Ngày hiện tại: {{ api_session.data.current_time }} 
Câu hỏi của người dùng: {{ user_input }} 

Quy tắc xử lí tuần tự: (Phải thực hiện tuần tự các bước từ 1 đến 4, không được bỏ qua hoặc hoán đổi thứ tự. Chỉ khi hoàn tất bước trước đó thì mới được chuyển sang bước tiếp theo.) 

1. Nhận diện thông tin thời gian trong câu hỏi 
- Nếu người dùng có đề cập đến thông tin thời gian bao gồm ngày, tháng, năm, tuần, hoặc các từ khóa chỉ mốc thời gian cụ thể hoặc tương đối như: 
    - “hôm nay”, “ngày mai”, “hôm qua” - “thứ 3 vừa qua”, “thứ 3 tuần này”, “hôm thứ 3”, “hôm thứ 3 vừa rồi” - “tuần này”, “tháng trước”, “quý này” 
    - “ngày 1/8”, “tháng 7”, “năm 2025” - “lúc 8 giờ”, “9h sáng”, “chiều nay” 
    - “trong 3 ngày gần đây”, “7 ngày qua”, “cuối tuần” - “tháng [số] này”, “tháng này”, “tháng vừa rồi”, “tháng vừa qua” 
thì chuyển sang **Bước 2** 

2. Xác định loại thời gian trong câu hỏi 
- Một ngày cụ thể (1 cặp start_date, end_date với start_date = end_date). 
    - Ví dụ: 
        - Hôm nay tôi check-in chưa? 
        - Ngày 10 tháng 7 tôi vào làm mấy giờ? 
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
        - Tháng này tôi đi muộn bao nhiêu buổi? 
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
        - "ngày 5", "mùng 3" - "thứ 2", "thứ ba tuần trước", "thứ năm tuần này" 
        - "ngày 15 tháng 6", "ngày 2 tháng trước", v.v. 
    - Giải thích các cụm thời gian tương đối dựa trên current_date: 
        - “hôm nay” → chính là current_date 
        - “hôm qua” → current_date - 1 ngày 
        - “hôm trước” → current_date - 2 ngày 
        - “hôm kia” → current_date 
        - 2 ngày - “hôm kìa” → current_date 
        - 3 ngày - “thứ [x] tuần này” → ngày gần nhất ứng với thứ đó trong cùng tuần với current_date 
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
    - Định nghĩa chuẩn
        - Quy ước về tuần làm việc: Từ thứ Hai đến thứ Sáu
        - Quy ước về tháng
            - Tháng hiện tại: Từ ngày 26 của tháng trước đến 25 của tháng hiện tại
            - Tháng đã qua: Từ ngày 26 của tháng trước đó đến 25 của tháng mà người dùng muốn hỏi
    - Các pattern nhận diện và xử lý
        - Pattern 1: Khoảng thời gian tuyệt đối
            - Cấu trúc: "từ [ngày cụ thể] đến [ngày cụ thể]"
            - Ví dụ:
                - "từ ngày 1 đến ngày 5" → start_date: YYYY-MM-01, end_date: YYYY-MM-05 (cùng tháng với current_date)
                - "từ 15 tháng trước đến 20 tháng này" → start_date: (tháng trước)-15, end_date: (tháng hiện tại)-20
        - Pattern 2: Khoảng thời gian theo tuần
            - Các cụm từ nhận diện:
                - "tuần này", "tuần hiện tại"
                - "tuần trước", "tuần vừa rồi", "tuần vừa qua"
                - "tuần trước nữa", "hai tuần trước"
                - "X tuần trước", "X tuần vừa rồi"
            - Logic tính toán tuần:
                current_week = tuần chứa current_date
                week_offset = số tuần cần lùi về quá khứ

                Với "tuần này":
                - start_date = thứ Hai của current_week
                - end_date = current_date (nếu chưa hết tuần) hoặc thứ Sáu (nếu đã hết tuần)

                Với "tuần trước":
                - target_week = current_week - 1
                - start_date = thứ Hai của target_week  
                - end_date = thứ Sáu của target_week

                Với "X tuần trước":
                - target_week = current_week - X
                - start_date = thứ Hai của target_week
                - end_date = thứ Sáu của target_week

                Với "X tuần vừa rồi/qua":
                - start_date = thứ Hai của (current_week - X)
                - end_date = thứ Sáu của (current_week - 1)
        - Pattern 3: Khoảng thời gian theo tháng
            - Các cụm từ nhận diện:
                - "tháng này", "tháng hiện tại"
                - "tháng trước", "tháng vừa rồi"
                - "tháng [số]", "tháng [số] năm [năm]"
            - Logic tính toán:
                - "tháng này": start_date = ngày 1 của tháng hiện tại, end_date = current_date
                - "tháng trước": start_date = ngày 1 của tháng trước, end_date = ngày cuối tháng trước
                - "tháng [số]": sử dụng năm hiện tại nếu không chỉ định năm
        - Pattern 4: Khoảng thời gian theo ngày
            Các cụm từ nhận diện:
                "X ngày qua", "X ngày vừa rồi", "X ngày gần đây"
                "từ đầu tuần đến nay"
                "từ đầu tháng đến nay"
            Logic tính toán:
                "X ngày qua": start_date = current_date - X, end_date = current_date - 1
                "từ đầu tuần đến nay": start_date = thứ Hai tuần hiện tại, end_date = current_date
                "từ đầu tháng đến nay": start_date = ngày 1 tháng hiện tại, end_date = current_date
    Ví dụ tính toán với current_date = 2025-03-08 (thứ Bảy)
        Ví dụ Pattern 1:

        "từ mùng 1 đến mùng 6" → start_date: "2025-03-01", end_date: "2025-03-06"
        "từ 15 tháng trước đến 20 tháng này" → start_date: "2025-02-15", end_date: "2025-03-20"

        Ví dụ Pattern 2:

        "tuần này" → start_date: "2025-03-03" (thứ Hai), end_date: "2025-03-08" (current_date)
        "tuần trước" → start_date: "2025-02-24" (thứ Hai), end_date: "2025-02-28" (thứ Sáu)
        "hai tuần trước" → start_date: "2025-02-17" (thứ Hai), end_date: "2025-02-21" (thứ Sáu)
        "hai tuần vừa rồi" → start_date: "2025-02-17" (thứ Hai), end_date: "2025-02-28" (thứ Sáu tuần trước)

        Ví dụ Pattern 3:

        "tháng này" → start_date: "2025-04-26", end_date: "2025-04-25"
        "tháng trước" → start_date: "2025-03-26", end_date: "2025-03-25"

        Ví dụ Pattern 4:

        "ba ngày vừa qua" → start_date: "2025-03-05", end_date: "2025-03-07"
        "từ đầu tuần đến nay" → start_date: "2025-03-03", end_date: "2025-03-08"
        "từ đầu tháng đến nay" → start_date: "2025-03-01", end_date: "2025-03-08"

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
