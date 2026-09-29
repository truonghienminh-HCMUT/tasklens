# 1. Mô tả bài toán và vấn đề thực tế

> Sản phẩm #1 của bài tập cuối khóa. Tư duy "vấn đề đi trước, công nghệ đi sau" (Buổi 12, slide 5).
> Các số liệu ở mục 1.1 do chính người làm bài tự báo cáo, không ước đoán.

## 1.1. Vấn đề

Mỗi học kỳ, sinh viên nhận 3–5 đề bài tập lớn/đồ án. Một đề thường dài 2–10 trang, trộn lẫn:
- yêu cầu chức năng
- ràng buộc công nghệ
- quy định nhóm
- sản phẩm phải nộp
- tiêu chí chấm
- các mốc thời gian

Có khi còn kèm phụ lục dài hoặc thông báo bổ sung trên LMS.

**Khâu đau nhất:** đọc đề và chuyển đề thành danh sách việc cần làm. Khâu này **lặp lại**, **tốn thời gian**, **dễ sai** và **đo được**:

| Chỉ số (đo trên chính người làm bài) | Giá trị |
|---|---|
| Thời gian tự đọc và phân rã 1 đề (từ lúc mở đề đến khi có checklist + kế hoạch) | **10–15 phút** (khi muốn hiểu sâu) |
| Số lần từng sót ràng buộc/sản phẩm nộp, hoặc hiểu chưa đúng yêu cầu, trong các học kỳ trước | **Nhiều lần** (tự báo cáo, không có số đếm chính xác) |
| Ví dụ dạng bẫy dễ sót (từ 2 đề thật dùng để kiểm thử) | Đề Hệ CSDL: hạn nộp khác nhau theo lớp, dòng của lớp A01 ghi "Friday, Thursday October 15" (tự mâu thuẫn). Đề CNPM: không ghi hạn nộp ("Deadlines will be announced on the LMS") |

**Rủi ro khi dán đề vào chatbot rồi hỏi "lập kế hoạch cho tôi":** AI trả lời trôi chảy nhưng có thể mắc các lỗi đã học ở Buổi 4 và Buổi 8:
- tự bịa hạn nộp khi đề không ghi
- lấy nhầm mốc giữa kỳ làm hạn chính thức
- bỏ qua chỗ đề mâu thuẫn
- làm theo một câu "ghi chú" cài trong tài liệu

Sinh viên tin theo thì hậu quả là trễ hạn hoặc làm sai yêu cầu.

**Hệ quả với thiết kế:** vì tự làm chỉ mất 10–15 phút, giá trị chính của TaskLens **không phải tiết kiệm thời gian** mà là **giảm sót và hiểu sai yêu cầu**, cùng với việc biết dừng khi đề thiếu hoặc mâu thuẫn. Đúng tinh thần Buổi 11: *nhanh hơn chưa chắc hiệu quả hơn*. Vì vậy các chỉ số thành công (mục 1.6) ưu tiên độ đúng và khả năng dừng, không ưu tiên tốc độ.

## 1.2. Người dùng

- **Người dùng trực tiếp:** sinh viên đại học (trước hết là chính người làm bài) khi nhận một đề bài tập lớn mới.
- **Chuyên môn:** hiểu nội dung môn học, nhưng dễ sót chi tiết khi đọc đề dài, nhiều mốc. Đủ năng lực để đối chiếu kết quả với đề gốc, nên có thể làm người kiểm tra cuối (Human checkpoint).
- **Không phục vụ:** giảng viên chấm bài, và "mọi người trên mạng" (red flag ở Buổi 12, slide 7).

## 1.3. Quy trình thủ công hiện tại

1. Mở đề (PDF/DOCX trên LMS) và đọc toàn bộ.
2. Gạch chân yêu cầu, ràng buộc, sản phẩm phải nộp, tiêu chí chấm.
3. Tìm hạn nộp và các mốc, đối chiếu với lịch cá nhân.
4. Ghi lại chỗ chưa rõ để hỏi giảng viên trên diễn đàn.
5. Chia việc thành các bước và đặt mốc hoàn thành trước hạn nộp.

## 1.4. AI tham gia ở mắt xích nào

TaskLens chỉ tham gia bước 2–5, ở mức **"AI làm – người kiểm tra"** (Buổi 11):
- AI trích xuất, gắn trích dẫn nguyên văn, phát hiện thiếu sót, mâu thuẫn, dữ liệu phi lý và đoạn văn đáng ngờ.
- AI chỉ đề xuất kế hoạch khi đủ dữ kiện.
- **Con người** đối chiếu với đề gốc và quyết định dùng hay không.

TaskLens **không** tự nộp bài, không gửi email, không viết hộ bài, không dự đoán điểm.

**Vì sao cần AI mà không dùng if-else truyền thống?**
- Đề bài là văn bản tự do, mỗi giảng viên viết một kiểu. Quy tắc cứng (regex tìm "hạn nộp") không hiểu được "mốc giữa kỳ" khác "hạn chính thức", hay "cá nhân" mâu thuẫn với "nhóm 3 người".
- Ngược lại, những gì kiểm tra được bằng quy tắc thì TaskLens **dùng code**, không để AI tự khẳng định: trích dẫn có thật trong đề không, ngày có hợp lệ không, mốc kế hoạch có vượt hạn không, có PII không. AI và code bù trừ cho nhau.

## 1.5. Kiểm tra tính khả thi (Feasibility Checklist, Buổi 12, slide 7)

| Tiêu chí | Câu trả lời | Red flag? |
|---|---|---|
| Người dùng | Sinh viên nhận đề bài tập lớn; trước hết là chính tác giả | Không |
| Đầu vào | Đề bài PDF/DOCX/TXT có sẵn trên LMS; văn bản rõ nguồn | Không. PDF scan không có lớp text được phát hiện và từ chối (TC10) |
| Đầu ra | JSON theo schema cố định (`src/tasklens/schema.py`), hiển thị thành bảng, xuất Markdown | Không |
| Quy trình | 5 bước thủ công ở mục 1.3, tác giả đã tự làm nhiều lần | Không |
| Giá trị | Giảm sót và hiểu sai yêu cầu; chặn lỗi "tự bịa deadline"; biết dừng khi đề thiếu hoặc mâu thuẫn (không nhắm vào tiết kiệm thời gian, xem mục 1.1) | Không. Đo bằng mục 1.6 |
| Kiểm thử | Có tiêu chí đúng/sai rõ: bộ 11 ca với check tự động (`evals/test-cases.csv`) | Không |
| Phạm vi | V1 chỉ là 1 lần gọi model + 1 prompt (`pipeline_v1.py` dưới 90 dòng); không cần backend phức tạp | Không |

## 1.6. Chỉ số thành công

| Chỉ số | Cách đo | Mục tiêu |
|---|---|---|
| Độ tin cậy | Số ca PASS ở mọi lượt chạy trên bộ Evals (Gemma: 3 lượt/ca; gpt-oss: 1 lượt/ca do quota gói miễn phí) | V2 > V1 |
| Không bịa | Tỉ lệ trích dẫn có thật trong đề (check `quotes_grounded`) | 100% sau cổng Validate |
| Biết dừng | Ca thiếu/mơ hồ/phi lý trả NEED_INFO, không lập kế hoạch | 100% ở V2 |
| Thời gian | Thủ công 10–15 phút/đề. TaskLens V2 mất trung bình ~25 giây mỗi lần gọi model với gpt-oss và ~85 giây với Gemma; ca bị chặn bằng code trả kết quả ngay | Thời gian người dùng tự đối chiếu kết quả **chưa được đo** |

## 1.7. Phạm vi

**Trong phạm vi:**
- Đọc 1 đề bài (văn bản có lớp text)
- Trích xuất có trích dẫn
- Phát hiện thiếu sót / mơ hồ / mâu thuẫn / dữ liệu phi lý / injection
- Kế hoạch có điều kiện
- Xuất Markdown/JSON sau khi người dùng xác nhận

**Ngoài phạm vi:**
- OCR ảnh scan
- Đồng bộ lịch/Trello
- Viết hộ bài
- Chấm hay dự đoán điểm
- Tự gửi câu hỏi cho giảng viên
