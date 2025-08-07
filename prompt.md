Dựa vào ngữ cảnh hiện tại, hãy phân tích câu hỏi của người dùng để đưa ra phản hồi phù hợp.

Ngữ cảnh hiện tại:
- Ngày hiện tại: {{$flow.state.current_time
- Khoảng thời gian mà người dùng đang nhắc đến:
{{$flow.state.time_query_in_string
- Chủ đề mà người dùng đang nhắc đến: {{$flow.state.topic
- Câu hỏi trước đó của người dùng: {{$flow.state.prev_question

Câu hỏi của người dùng: {{$flow.state.user_question 

Quy tắc xử lí tuần tự: (Phải thực hiện tuần tự các bước từ 1 đến 7, không được bỏ qua hoặc hoán đổi thứ tự. Chỉ khi hoàn tất bước trước đó thì mới được chuyển sang bước tiếp theo.)

1. Nhận diện thông tin thời gian trong câu hỏi
- Nếu người dùng có đề cập đến thông tin thời gian bao gồm ngày, tháng, năm, tuần, hoặc các từ khóa chỉ mốc thời gian cụ thể hoặc tương đối như:
    - “hôm nay”, “ngày mai”, “hôm qua”
    - “tuần này”, “tháng trước”, “quý này”
    - “ngày 1/8”, “tháng 7”, “năm 2025”
    - “lúc 8 giờ”, “9h sáng”, “chiều nay”
    - “trong 3 ngày gần đây”, “7 ngày qua”, “cuối tuần”
thì xác định Có đề cập đến thời gian và chuyển sang **Bước 2**
- Nếu người dùng không đề cập đến bất kỳ thời gian nào, câu hỏi không có thông tin thời gian, không thể xác định được mốc thời gian liên quan, ví dụ:
    - “Tôi đã check-in chưa?”
    - "Tôi check in lúc nào?"
    - “Tôi check-out mấy giờ?”
    - “Giờ vào là lúc nào?”
    - "Tôi đi muộn không?"
    - "Tôi được bao nhiêu ngày công?"
    - "Thời gian check in thì sao?"
    - "Còn thời gian chek out của tôi?"
hoặc không chứa các từ khóa thời gian như “hôm nay”, “ngày”, “tháng”, “tuần”, v.v. thì xác định Không đề cập đến thời gian và chuyển sang **Bước 4**
- Ngoài ra, nếu câu hỏi có chứa các từ khóa chỉ thời gian mơ hồ, không xác định rõ ràng như:
    - “hôm ấy”, “hôm đấy”, “hôm đó”, “ngày hôm đó”
    - “tuần đấy”, “tháng đấy”, “tháng đó”
    - "những ngày đó", "những hôm đấy", "những hôm ấy"
hoặc các biến thể tương tự: “lúc đó”, “dạo ấy”, “thời điểm ấy”
thì cũng xác định là Không đề cập đến thời gian và chuyển sang **Bước 4**

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
hoặc chứa các cụm từ thể hiện khoảng thời gian, như: “trong tuần trước”, “trong tháng này”, “2 tuần vừa rồi”, “từ ngày ... đến ngày ...”, “từ thứ 2 đến thứ 6”, v.v.
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
        - “thứ [x] tuần trước” → ngày tương ứng với thứ đó của tuần trước
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
    - Nếu là một ngày cụ thể hoặc một khoảng thời gian cụ thể duy nhất thì sau khi xác định được start_date và end_date, chuyển sang **Bước 5** luôn, không cần lặp lại bước này.
    - Nếu là nhiều ngày/mốc thời gian cụ thể hoặc nhiều khoảng thời gian khác nhau thì phải lặp lại **Bước 3** này cho từng khoảng/mốc thời gian riêng biệt, đến khi xử lý xong toàn bộ. Chỉ khi đã tính đủ tất cả các cặp start_date, end_date, mới được chuyển sang **Bước 5**.

4. Nếu không xác định được mốc thời gian
- Nếu ngữ cảnh hiện tại đã có khoảng thời gian thì giữ nguyên.
- Nếu không có ngữ cảnh thì trả về chuỗi "Không có"

5. Nhận diện thông tin chủ đề trong câu hỏi
- Nếu người dùng có đề cập đến chủ đề ví dụ như:
    - “Hôm qua tôi đi muộn không?”
    - “Thời gian check in của tôi thứ 4 tuần trước là lúc nào?”
    - “Tôi được bao nhiêu ngày công trong tuần này?”
    - “Ngày 1/8 tôi có bị đi muộn không?”
thì xác định Có đề cập đến chủ đề và chuyển sang **Bước 6**
- Nếu người dùng không đề cập đến bất kỳ chủ đề nào ở trên, hoặc chỉ nói đến thời gian chung chung mà không gắn với chủ đề, ví dụ:
    - “Hôm nay thì sao?”
    - “Hôm trước thì thế nào?”
    - “Thứ 7 tuần trước thì sao?”
    - "Thứ 2 vừa rồi thì sao?"
    - "Thứ 3 vừa qua thì thế nào"
    - "Thứ 3 tuần trước nữa?"
thì xác định Không đề cập đến chủ đề và chuyển sang **Bước 7** luôn

6. Xác định chủ đề:
- Nếu người dùng hỏi về thời gian check-in / check-out cụ thể trong ngày. Ví dụ:
    - Hôm qua tôi vào làm lúc mấy giờ?
    - Ngày 10/7 tôi chấm công mấy giờ?
    - Hôm nay tôi có quên chấm công không?
    - Thời gian check-in hôm kia của tôi là mấy giờ?
thì xác định chủ đề là "Thời gian Check-in / Check-out cụ thể" và trả về luôn, không cần chuyển sang **Bước 7**
- Nếu người dùng hỏi về số ngày hoặc lần đi muộn. Ví dụ:
    - Tháng trước tôi đi muộn bao nhiêu ngày?
    - Tôi có bị tính đi trễ ngày nào trong tuần trước không?
    - Tổng số lần đi trễ của tôi trong tháng 6 là bao nhiêu?
thì xác định chủ đề là "Đi muộn" và trả về luôn, không cần chuyển sang **Bước 7**
- Nếu người dùng hỏi về số ngày công hoặc việc đi làm đủ ngày. Ví dụ:
    - Tháng này tôi có bao nhiêu ngày công?
    - Tôi đi làm đủ công trong tháng 6 không?
    - Tổng số ngày công của tôi 2 tuần vừa rồi là bao nhiêu?
thì xác định chủ đề là "Ngày công" và trả về luôn, không cần chuyển sang **Bước 7**

7. Nếu không xác định được chủ đề:
- Nếu ngữ cảnh hiện tại đã có thông tin về chủ đề thì giữ nguyên.
- Nếu không có ngữ cảnh thì trả về chuỗi "Không có"
