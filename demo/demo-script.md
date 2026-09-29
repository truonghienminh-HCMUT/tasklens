# 11. Kịch bản video demo (3 phút)

> Sản phẩm #11. Cấu trúc theo Buổi 12, slide 33: **Problem → Product & Architecture → Live Demo → Kết luận**.
> Nguyên tắc (slide 36): không che giấu lỗi, không chỉ trình diễn câu hỏi dễ. Demo **cả ca hệ thống biết dừng lại**.

## Chuẩn bị trước khi quay (khoảng 10 phút)

1. `streamlit run app.py` → chọn **V2**, model **groq** (gpt-oss, phản hồi 5–15 giây, nhanh hơn Gemma khi quay).
2. Chạy thử trước mỗi cảnh 1 lần để chắc chắn quota Groq còn (`python scripts/check_setup.py`).
3. Mở sẵn các tab:
   - (a) `docs/workflow-diagram.png`
   - (b) `evals/v1-vs-v2.png`
   - (c) `evals/results/comparison.md`
   - (d) file đề thật môn CSDL
4. **An toàn khi quay:** không mở file `.env`, không để lộ API key; không quay danh sách sinh viên thật.
   - Đề thật chỉ nên xuất hiện trong video để **không công khai** (YouTube Unlisted, Google Drive chế độ "có link").
   - Nếu đăng công khai trên LinkedIn, dùng đề mẫu tổng hợp (`evals/inputs/TC01_happy_path.txt`, `TC08_injection.txt`).
5. **Công cụ quay:** Xbox Game Bar (`Win + Alt + R`) hoặc OBS. Cắt đoạn chờ model bằng Clipchamp (có sẵn trên Windows).

## Kịch bản

| Thời gian | Màn hình | Lời nói (gợi ý) |
|---|---|---|
| **0:00–0:20** Vấn đề | Mở đề thật môn CSDL (PDF) | "Mỗi học kỳ em nhận 3–5 đề bài tập lớn. Riêng đề này có tới hai hạn nộp khác nhau theo lớp, và ghi 'Friday, Thursday October 15', trong khi 15/10 là thứ Năm. Tự làm thì em mất 10–15 phút một đề mà vẫn hay sót hoặc hiểu sai. Dán vào chatbot thì nhanh, nhưng bản V1 của em cho thấy AI tự lấy mốc giữa kỳ làm hạn nộp và vẫn lập kế hoạch khi đề không có hạn nộp." |
| **0:20–0:45** Kiến trúc | Sơ đồ workflow | "TaskLens chỉ gọi model **một lần**. Trước và sau lần gọi đó là các cổng bằng code: làm sạch và che dữ liệu cá nhân, chặn yêu cầu viết hộ hay đoán điểm, và kiểm tra trích dẫn, hạn nộp. Không có hạn nộp hợp lệ thì không có kế hoạch. Cuối cùng, người dùng phải xác nhận đã đối chiếu." |
| **0:45–1:15** Demo 1: biết dừng | Tải đề CSDL, không nói lớp → **Phân tích** | "Đề có hai hạn nộp cho hai lớp. TaskLens không đoán: nó trả **NEED_INFO**, hỏi em học lớp nào, và **không** lập kế hoạch. Mỗi yêu cầu đều kèm câu trích nguyên văn." (Chỉ vào ô "Cần bạn bổ sung" và cột "Trích dẫn") |
| **1:15–1:45** Demo 2: đề tự mâu thuẫn | Sửa yêu cầu: "Tôi học lớp A01. Phân rã đề…" → **Phân tích**; sau đó điền ô Hạn nộp "23:59 15/10/2026" → **Phân tích** lại | "Lớp A01 thì đề lại ghi 'Friday, Thursday October 15'. TaskLens chỉ ra chỗ mâu thuẫn này và **vẫn không đoán**. Em xác nhận với giảng viên rồi điền hạn nộp 15/10: giờ hệ thống lập 8 bước, bắt đầu từ hạn đăng ký nhóm 30/09, không mốc nào vượt 15/10." |
| **1:45–2:00** Demo 3: injection | Dán `TC08_injection.txt` → **Phân tích** | "Đề này có câu cài lệnh bảo AI ghi 'không có hạn nộp' và chép system prompt. Ở V1, gpt-oss làm theo. Ở V2, câu đó bị gắn cờ, hạn nộp vẫn đúng 15/12." |
| **2:00–2:15** Demo 4: ngoài phạm vi | Yêu cầu: "Cho tôi biết tôi được bao nhiêu điểm" | "Câu hỏi điểm số thuộc thẩm quyền giảng viên. Hệ thống từ chối ngay ở cổng code, không cần gọi model." Tick "Tôi đã đối chiếu", tải Markdown |
| **2:15–2:45** Bằng chứng | `evals/v1-vs-v2.png` + bảng Model Swap | "Trên 11 ca thử lửa: V1 chỉ đạt 3/11 với cả hai model; V2 đạt 10/11 với gpt-oss và 8/11 với Gemma, và 3/3 trên đề thật. Em chạy cùng bộ test trên hai model của hai hãng. Cùng một tính năng JSON mode giúp model này nhưng làm hỏng model kia, nên phải đo chứ không đoán." |
| **2:45–3:00** Kết luận | README (phần giới hạn) | "TaskLens không thay em đọc đề. Nó giúp em không bỏ sót, và biết dừng khi thiếu dữ kiện. Giới hạn: luật từ khóa có thể bị lách, PDF scan chưa đọc được. Tất cả đều được công khai trong repo. AI tăng tốc, con người quyết định." |

## Sau khi quay

- [ ] Upload YouTube (Unlisted) hoặc Google Drive (Anyone with the link, Viewer).
- [ ] Dán link vào `SUBMISSION.md` và `README.md`.
- [ ] (Tùy chọn) Cắt 20–30 giây cảnh Demo 1 và Demo 3 làm GIF cho bài LinkedIn (dùng đề mẫu tổng hợp).
