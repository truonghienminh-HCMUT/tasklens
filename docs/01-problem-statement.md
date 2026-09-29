# 1. Bài toán và vấn đề thực tế

Tôi chọn bài toán này vì đây là việc tôi gặp ở mọi học kỳ: nhận một đề bài tập lớn và phải biến nó thành danh sách việc cần làm. Các số liệu ở mục 1.1 là do tôi tự ghi nhận trên chính mình, không phải ước đoán.

## 1.1. Vấn đề

Mỗi học kỳ tôi nhận khoảng 3–5 đề bài tập lớn hoặc đồ án. Một đề thường dài 2–10 trang, trong đó yêu cầu chức năng, ràng buộc công nghệ, quy định làm nhóm, danh sách sản phẩm phải nộp, tiêu chí chấm và các mốc thời gian nằm lẫn vào nhau. Nhiều đề còn có phụ lục dài, hoặc giảng viên thông báo bổ sung trên LMS sau khi phát đề.

Khâu mất công nhất là đọc đề và chuyển nó thành việc cần làm. Việc này lặp lại ở mọi môn, tốn thời gian, dễ sai, và đo được:

| Chỉ số (đo trên chính tôi) | Giá trị |
|---|---|
| Thời gian tự đọc và phân rã một đề, tính từ lúc mở đề đến khi có checklist và kế hoạch | 10–15 phút nếu muốn hiểu kỹ |
| Số lần từng sót ràng buộc, sót sản phẩm nộp hoặc hiểu sai yêu cầu ở các học kỳ trước | Nhiều lần (tự nhận, không có số đếm chính xác) |
| Ví dụ về chỗ dễ sót, lấy từ 2 đề thật dùng để kiểm thử | Đề Hệ cơ sở dữ liệu có hạn nộp khác nhau theo lớp, và dòng của lớp A01 ghi "Friday, Thursday October 15" (tự mâu thuẫn). Đề Công nghệ phần mềm không ghi hạn nộp, chỉ nói "Deadlines will be announced on the LMS" |

Cách nhanh nhất là dán đề vào chatbot rồi nhờ lập kế hoạch. Câu trả lời thường rất trôi chảy, nhưng dễ mắc đúng những lỗi đã học ở Buổi 4 và Buổi 8: tự bịa hạn nộp khi đề không ghi, lấy nhầm mốc giữa kỳ làm hạn chính thức, bỏ qua chỗ đề mâu thuẫn, hoặc làm theo một câu "ghi chú" cài sẵn trong tài liệu. Nếu tin theo, sinh viên có thể trễ hạn hoặc làm sai yêu cầu.

Vì tự làm cũng chỉ mất 10–15 phút, tôi không đặt mục tiêu tiết kiệm thời gian. Điều tôi cần là ít sót và ít hiểu sai hơn, và một công cụ biết dừng lại khi đề thiếu hoặc mâu thuẫn thay vì đoán bừa. Buổi 11 cũng nhắc rằng nhanh hơn chưa chắc đã hiệu quả hơn. Vì vậy các chỉ số ở mục 1.6 ưu tiên độ đúng và khả năng dừng, không ưu tiên tốc độ.

## 1.2. Người dùng

Người dùng trực tiếp là sinh viên đại học vừa nhận một đề bài tập lớn, trước hết là chính tôi. Họ hiểu nội dung môn học nhưng dễ sót chi tiết khi đề dài và có nhiều mốc. Họ cũng đủ khả năng tự đối chiếu kết quả với đề gốc, nên có thể đóng vai người kiểm tra cuối cùng (Human checkpoint).

TaskLens không hướng tới giảng viên chấm bài, và cũng không nhắm tới "mọi người trên mạng", một red flag được nêu ở Buổi 12, slide 7.

## 1.3. Quy trình thủ công hiện tại

1. Mở đề (PDF hoặc DOCX trên LMS) và đọc hết.
2. Gạch chân yêu cầu, ràng buộc, sản phẩm phải nộp và tiêu chí chấm.
3. Tìm hạn nộp cùng các mốc, rồi so với lịch cá nhân.
4. Ghi lại những chỗ chưa rõ để hỏi giảng viên trên diễn đàn.
5. Chia việc thành các bước và đặt mốc hoàn thành trước hạn nộp.

## 1.4. AI tham gia ở đâu

TaskLens chỉ tham gia từ bước 2 đến bước 5, theo cách "AI làm, người kiểm tra" ở Buổi 11. AI trích xuất thông tin kèm trích dẫn nguyên văn, chỉ ra chỗ thiếu, chỗ mâu thuẫn, dữ liệu phi lý và đoạn văn đáng ngờ, và chỉ đề xuất kế hoạch khi đủ dữ kiện. Người dùng đối chiếu với đề gốc rồi tự quyết định có dùng kết quả hay không.

TaskLens không nộp bài, không gửi email, không viết bài hộ và không dự đoán điểm.

Tại sao lại cần AI mà không viết if-else? Đề bài là văn bản tự do, mỗi giảng viên viết một kiểu. Một quy tắc cứng, chẳng hạn dùng regex tìm chữ "hạn nộp", không phân biệt được "mốc giữa kỳ" với "hạn chính thức", cũng không nhận ra "làm cá nhân" mâu thuẫn với "nhóm 3 người". Ngược lại, việc gì kiểm tra được bằng quy tắc thì TaskLens dùng code chứ không để AI tự khẳng định: trích dẫn có thật trong đề không, ngày có hợp lệ không, mốc kế hoạch có vượt hạn nộp không, trong đề có dữ liệu cá nhân không. Hai phần này bổ sung cho nhau.

## 1.5. Kiểm tra tính khả thi (Feasibility Checklist, Buổi 12, slide 7)

| Tiêu chí | Câu trả lời | Red flag? |
|---|---|---|
| Người dùng | Sinh viên nhận đề bài tập lớn, trước hết là chính tôi | Không |
| Đầu vào | Đề bài PDF, DOCX hoặc TXT có sẵn trên LMS, nguồn rõ ràng | Không. PDF scan không có lớp chữ sẽ bị phát hiện và từ chối (TC10) |
| Đầu ra | JSON theo schema cố định (`src/tasklens/schema.py`), hiển thị thành bảng và xuất được Markdown | Không |
| Quy trình | 5 bước thủ công ở mục 1.3, tôi đã tự làm nhiều lần | Không |
| Giá trị | Giảm sót và hiểu sai yêu cầu, chặn lỗi tự bịa hạn nộp, biết dừng khi đề thiếu hoặc mâu thuẫn. Không nhắm vào tiết kiệm thời gian (xem mục 1.1) | Không. Đo bằng các chỉ số ở mục 1.6 |
| Kiểm thử | Có tiêu chí đúng sai rõ ràng: bộ 11 ca với các check tự động (`evals/test-cases.csv`) | Không |
| Phạm vi | V1 chỉ là 1 lần gọi model và 1 prompt (`pipeline_v1.py` dưới 90 dòng), không cần backend phức tạp | Không |

## 1.6. Chỉ số thành công

| Chỉ số | Cách đo | Mục tiêu |
|---|---|---|
| Độ tin cậy | Số ca PASS ở mọi lượt chạy trên bộ Evals (Gemma chạy 3 lượt/ca, gpt-oss 1 lượt/ca do quota gói miễn phí) | V2 cao hơn V1 |
| Không bịa | Tỉ lệ trích dẫn có thật trong đề (check `quotes_grounded`) | 100% sau cổng Validate |
| Biết dừng | Các ca thiếu, mơ hồ hoặc phi lý phải trả NEED_INFO và không có kế hoạch | 100% ở V2 |
| Thời gian | Tự làm mất 10–15 phút một đề. Với V2, mỗi lần gọi model mất trung bình khoảng 25 giây (gpt-oss) và 85 giây (Gemma); các ca bị code chặn có kết quả ngay | Chưa đặt mục tiêu, vì chưa đo thời gian người dùng tự đối chiếu kết quả |

## 1.7. Phạm vi

Trong phạm vi: đọc một đề bài có lớp chữ; trích xuất thông tin kèm trích dẫn; phát hiện chỗ thiếu, mơ hồ, mâu thuẫn, dữ liệu phi lý và prompt injection; lập kế hoạch khi đủ điều kiện; xuất Markdown hoặc JSON sau khi người dùng xác nhận.

Ngoài phạm vi: OCR ảnh scan, đồng bộ với lịch hay Trello, viết bài hộ, chấm hoặc dự đoán điểm, tự gửi câu hỏi cho giảng viên.
