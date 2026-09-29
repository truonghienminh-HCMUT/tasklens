# 11. Kịch bản video demo (3 phút)

Video đi theo trình tự ở Buổi 12, slide 33: vấn đề, sản phẩm và kiến trúc, demo trực tiếp, rồi kết luận. Theo tinh thần slide 36, tôi không giấu lỗi và không chỉ chọn câu hỏi dễ, nên video có cả những cảnh hệ thống dừng lại vì thiếu dữ kiện.

## Chuẩn bị trước khi quay (khoảng 10 phút)

1. Chạy `streamlit run app.py`, chọn V2 và model groq. Với gpt-oss, mỗi lần phân tích mất khoảng 15–40 giây, vẫn nhanh hơn Gemma; đoạn chờ có thể cắt đi khi dựng video.
2. Chạy thử mỗi cảnh một lần trước khi quay, và chạy `python scripts/check_setup.py` để chắc quota Groq vẫn còn.
3. Mở sẵn các tab: (a) `docs/workflow-diagram.png`, (b) `evals/v1-vs-v2.png`, (c) `evals/results/comparison.md`, (d) file đề thật môn Hệ cơ sở dữ liệu.
4. Khi quay, không mở file `.env`, không để lộ API key, và không quay danh sách sinh viên thật. Đề thật chỉ nên xuất hiện trong video để ở chế độ không công khai (YouTube Unlisted, hoặc Google Drive với quyền "Bất kỳ ai có đường liên kết"). Nếu muốn đăng công khai lên LinkedIn, hãy dùng đề mẫu tổng hợp (`evals/inputs/TC01_happy_path.txt`, `TC08_injection.txt`).
5. Có thể quay bằng Xbox Game Bar (`Win + Alt + R`) hoặc OBS, và cắt đoạn chờ model bằng Clipchamp có sẵn trên Windows.

## Kịch bản

| Thời gian | Màn hình | Lời nói (gợi ý) |
|---|---|---|
| 0:00–0:20 · Vấn đề | Mở đề thật môn Hệ cơ sở dữ liệu (PDF) | "Mỗi học kỳ em nhận khoảng 3 đến 5 đề bài tập lớn. Như đề này, có tới hai hạn nộp khác nhau tùy lớp, mà có dòng còn ghi 'Friday, Thursday October 15', trong khi 15/10 là thứ Năm. Tự đọc thì em mất 10–15 phút một đề mà vẫn hay sót hoặc hiểu sai. Dán vào chatbot thì nhanh hơn, nhưng bản V1 của em cho thấy AI lấy luôn mốc giữa kỳ làm hạn nộp, và đề không có hạn nộp thì nó vẫn lập kế hoạch như thường." |
| 0:20–0:45 · Kiến trúc | Sơ đồ workflow | "TaskLens chỉ gọi model đúng một lần. Trước và sau lần gọi đó là các bước kiểm tra bằng code: làm sạch đề và che thông tin cá nhân, chặn các yêu cầu kiểu viết hộ hay đoán điểm, rồi kiểm tra lại trích dẫn và hạn nộp. Chưa có hạn nộp hợp lệ thì chưa có kế hoạch. Cuối cùng, người dùng phải xác nhận là đã đối chiếu với đề gốc." |
| 0:45–1:15 · Demo 1: biết dừng | Tải đề Hệ cơ sở dữ liệu, chưa nói lớp, bấm Phân tích | "Đề này có hai hạn nộp cho hai lớp. TaskLens không đoán em học lớp nào mà trả về NEED_INFO, hỏi lại em, và chưa lập kế hoạch. Ở cột này, mỗi yêu cầu đều kèm câu trích nguyên văn từ đề." (Chỉ vào ô "Cần bạn bổ sung" và cột "Trích dẫn") |
| 1:15–1:45 · Demo 2: đề tự mâu thuẫn | Sửa yêu cầu thành "Tôi học lớp A01. Phân rã đề…", bấm Phân tích; sau đó điền ô Hạn nộp "23:59 15/10/2026" và bấm Phân tích lại | "Em ghi là em học lớp A01. Lúc này TaskLens chỉ ra dòng hạn nộp của lớp A01 tự mâu thuẫn, 'Friday, Thursday October 15', và vẫn không đoán. Giả sử em đã hỏi lại giảng viên và biết hạn nộp là 15/10, em điền vào ô Hạn nộp. Giờ hệ thống mới lập kế hoạch 8 bước, bắt đầu từ hạn đăng ký nhóm ngày 30/09, và không có mốc nào vượt quá 15/10." |
| 1:45–2:00 · Demo 3: injection | Dán `TC08_injection.txt`, bấm Phân tích | "Trong đề này em cài sẵn một câu bảo AI ghi là 'không có hạn nộp' và chép lại system prompt. Ở V1, gpt-oss làm theo thật. Còn ở V2, câu đó bị gắn cờ và hạn nộp vẫn đúng là 15/12." |
| 2:00–2:15 · Demo 4: ngoài phạm vi | Ghi yêu cầu "Cho tôi biết tôi được bao nhiêu điểm" | "Chuyện điểm số là việc của giảng viên, nên hệ thống từ chối ngay ở bước kiểm tra bằng code, không cần gọi tới model." Sau đó tick "Tôi đã đối chiếu" và tải file Markdown |
| 2:15–2:45 · Bằng chứng | `evals/v1-vs-v2.png` và bảng Model Swap | "Trên 11 ca thử lửa, V1 chỉ đạt 3 ca với cả hai model. V2 đạt 10 ca với gpt-oss, 8 ca với Gemma, và qua cả 3 đề thật. Em chạy cùng một bộ test trên hai model của hai hãng khác nhau, và thấy có tính năng như JSON mode giúp được model này nhưng lại làm hỏng model kia. Vì vậy phải đo, không đoán được." |
| 2:45–3:00 · Kết luận | README (phần giới hạn) | "TaskLens không đọc đề thay em. Nó giúp em không bỏ sót, và biết dừng khi thiếu dữ kiện. Hệ thống vẫn còn giới hạn: bộ lọc từ khóa có thể bị lách, và chưa đọc được PDF scan. Em ghi rõ những điều này trong repo. AI giúp làm nhanh hơn, còn quyết định cuối cùng vẫn là của con người." |

## Sau khi quay

- [ ] Upload lên YouTube (chế độ Unlisted) hoặc Google Drive (quyền "Bất kỳ ai có đường liên kết", chỉ xem).
- [ ] Dán link vào `SUBMISSION.md`.
- [ ] (Không bắt buộc) Cắt 20–30 giây ở cảnh Demo 1 và Demo 3 làm ảnh GIF cho bài LinkedIn, dùng đề mẫu tổng hợp.
