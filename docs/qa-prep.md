# Chuẩn bị phản biện: 5 câu hỏi (Buổi 12, slide 34)

> Tài liệu bổ trợ cho phần trình bày. Mỗi câu trả lời dẫn tới bằng chứng trong repo.

### 1. "Tại sao dùng AI mà không dùng if-else truyền thống?"

- **Phần cần AI:** đề bài là văn bản tự do, mỗi giảng viên viết một kiểu, trộn tiếng Việt và tiếng Anh, PDF còn bị vỡ dòng. Quy tắc cứng không phân biệt được "mốc giữa kỳ" với "hạn chính thức", hay nhận ra "cá nhân" mâu thuẫn với "nhóm 3 người" nằm cách nhau nửa trang.
- **Phần không cần AI thì TaskLens dùng if-else:** kiểm tra trích dẫn có thật không, ngày có hợp lệ không, mốc kế hoạch có vượt hạn không, che PII, chặn đầu vào rác, chặn yêu cầu ngoài phạm vi.
- **Bằng chứng:** chạy bộ test V2 với *model giả* vẫn đạt 4/11 ca nhờ riêng các cổng code. Còn những ca cần hiểu nội dung (TC01, TC05, TC09) thì chỉ đạt khi có model thật.

### 2. "Nếu người dùng cố tình đưa dữ liệu giả, hệ thống có phát hiện không?"

- **Phát hiện được:** những gì kiểm tra được bằng code. Ngày không có thật (30/02) bị bắt bằng lịch (TC04). Hạn nộp không xuất hiện trong đề bị gỡ. Trích dẫn bịa bị gỡ và báo lại.
- **Không phát hiện được:** dữ liệu giả nhưng hợp lý (một ngày có thật nhưng sai sự thật). Hệ thống chỉ biết đề nói gì, không biết đề nói đúng hay sai. Giới hạn này được công khai ở `docs/limitations-safety.md`.

### 3. "Sửa V1 lên V2, làm sao đảm bảo không làm hỏng các ca vốn đang chạy tốt?"

- **Regression:** mỗi thay đổi đều chạy lại **toàn bộ** bộ 11 ca (cộng 3 ca đề thật) trên cả 2 model, không chỉ các ca đã FAIL. Kết quả ở `evals/v1-vs-v2.md` và heatmap theo từng ca.
- **Bộ chấm cũng có test riêng** (`tests/`), và mọi kết quả được chấm lại bằng cùng một phiên bản bộ chấm từ log thô.
- **Cấu hình V2 được chốt trước khi chạy bộ đầy đủ.** Không chỉnh prompt để "học tủ" từng ca FAIL.

### 4. "Nếu ngày mai công ty chuyển sang model mã nguồn mở nội bộ, mất bao lâu để chuyển?"

- **Chỉ cần viết thêm 1 file adapter** (khoảng 40 dòng, xem `src/tasklens/adapters/groq_adapter.py`: 15 dòng vì API tương thích OpenAI), rồi chạy lại `evals/run_evals.py --model <mới>` để có số liệu so sánh trong vài giờ. Logic, schema, prompt, cổng kiểm tra và bộ Evals giữ nguyên.
- **Đã làm thật:** TaskLens đã chạy trên 2 model mã nguồn mở (gpt-oss-120b, Gemma 4) và thử thêm 3 model khác trong quá trình làm.
- **Không phải model nào cũng hợp mọi tính năng:** chế độ JSON schema giúp gpt-oss nhưng làm Gemma suy biến. Phải đo bằng Evals, không đoán (`docs/model-swap-log.md`).

### 5. "Rủi ro lớn nhất cho người dùng là gì, trách nhiệm pháp lý thuộc về ai?"

- **Rủi ro lớn nhất:** người dùng **tin kế hoạch sai** (ví dụ hạn nộp sai) rồi trễ hạn. Đây chính là lỗi nghiêm trọng mà V1 mắc phải (TC02: lấy mốc giữa kỳ làm hạn nộp). V2 giảm rủi ro bằng cổng code: không có hạn nộp hợp lệ thì không có kế hoạch. Thêm vào đó là Human checkpoint bắt buộc trước khi xuất file.
- **Rủi ro thứ hai:** lộ dữ liệu cá nhân cho bên thứ ba. V2 che PII trước khi gửi.
- **Trách nhiệm:** quyết định cuối cùng thuộc người dùng. AI không có tư cách pháp lý (Buổi 12, slide 12). Người làm sản phẩm chịu trách nhiệm thiết kế an toàn và **công khai giới hạn**.
