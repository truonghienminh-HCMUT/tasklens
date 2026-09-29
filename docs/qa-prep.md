# Chuẩn bị phản biện

Đây là phần em chuẩn bị cho 5 câu hỏi phản biện ở Buổi 12, slide 34, cùng hai câu em nghĩ có thể bị hỏi thêm. Mỗi câu trả lời đều ghi chỗ tìm bằng chứng trong repo.

### 1. "Tại sao em chọn giải bài toán này bằng AI mà không dùng if-else truyền thống?"

Đề bài là văn bản tự do, mỗi giảng viên viết một kiểu, có khi trộn cả tiếng Việt lẫn tiếng Anh, còn PDF thì hay bị vỡ dòng khi trích chữ. Một quy tắc cứng không phân biệt được "mốc giữa kỳ" với "hạn nộp chính thức", cũng không nhận ra chữ "cá nhân" ở đầu đề mâu thuẫn với "nhóm 3 người" ở nửa trang sau. Phần đó cần AI.

Nhưng việc gì làm được bằng if-else thì em vẫn dùng if-else: kiểm tra trích dẫn có thật không, ngày có hợp lệ không, mốc kế hoạch có vượt hạn nộp không, che dữ liệu cá nhân, chặn đầu vào rác và chặn yêu cầu ngoài phạm vi.

Bằng chứng là khi em chạy V2 với một model giả chỉ trả về kết quả vô nghĩa, riêng các cổng code vẫn giúp đạt 4/11 ca. Còn những ca cần hiểu nội dung như TC01, TC05 hay TC08 thì chỉ đạt khi có model thật (`evals/v1-vs-v2.md`, mục 8.5).

### 2. "Nếu người dùng cố tình cung cấp dữ liệu giả hoặc sai sự thật, hệ thống có phát hiện được không?"

Hệ thống phát hiện được những gì kiểm tra được bằng code. Ngày không có thật như 30/02 bị bắt khi đối chiếu với lịch (TC04). Hạn nộp không xuất hiện trong đề sẽ bị gỡ. Trích dẫn bịa cũng bị gỡ, và hệ thống báo lại cho người dùng.

Còn dữ liệu giả nhưng hợp lý, chẳng hạn một ngày có thật nhưng sai sự thật, thì hệ thống không phát hiện được. TaskLens chỉ biết đề nói gì, không biết đề nói đúng hay sai. Em đã ghi rõ giới hạn này trong `docs/limitations-safety.md`.

### 3. "Khi sửa từ V1 lên V2, làm sao em đảm bảo việc sửa không làm hỏng các ca vốn đang chạy tốt?"

Khi đánh giá V2, em chạy lại toàn bộ 11 ca và 3 đề thật trên cả hai model, chứ không chỉ chạy lại các ca từng FAIL. Kết quả nằm ở `evals/v1-vs-v2.md`, có cả heatmap theo từng ca, và mọi ca V1 đã đạt thì V2 vẫn đạt.

Trong lúc sửa code, em chạy 36 unit test trong `tests/` cho bộ chấm, các cổng code và giao diện. Mọi kết quả eval đều được chấm lại bằng cùng một phiên bản bộ chấm từ log thô. Ngoài ra, em chốt cấu hình V2 trước khi chạy bộ đầy đủ và không chỉnh prompt để "học tủ" từng ca FAIL.

### 4. "Nếu ngày mai công ty chuyển sang dùng một mô hình mã nguồn mở nội bộ, em mất bao lâu để chuyển giao toàn bộ hệ thống?"

Em chỉ cần viết thêm một file adapter, các adapter hiện có dài khoảng 50 dòng, riêng adapter Groq (`src/tasklens/adapters/groq_adapter.py`) chỉ khoảng 20 dòng vì API của Groq tương thích với OpenAI. Sau đó chạy lại `evals/run_evals.py --model <model mới>` là có số liệu so sánh trong vài giờ. Logic, schema, prompt, các cổng kiểm tra và bộ Evals đều giữ nguyên.

Em đã làm việc này thật: TaskLens đang chạy trên hai model open-weight là gpt-oss-120b và Gemma 4, và trong quá trình làm em đã phải đổi qua nhiều model khác vì các gói miễn phí liên tục gặp sự cố (ghi trong `docs/model-swap-log.md`).

Tuy vậy, không phải tính năng nào cũng hợp với mọi model. Chế độ JSON schema giúp gpt-oss nhưng làm Gemma suy biến, nên với model mới vẫn phải chạy Evals để kiểm tra chứ không đoán trước được.

### 5. "Rủi ro lớn nhất mà sản phẩm này có thể gây ra cho người dùng là gì, và trách nhiệm pháp lý cuối cùng thuộc về ai?"

Rủi ro lớn nhất là người dùng tin vào một kế hoạch sai, chẳng hạn hạn nộp sai, rồi bị trễ hạn. V1 đã mắc đúng lỗi này ở TC02 khi lấy mốc giữa kỳ làm hạn nộp. V2 giảm rủi ro bằng cổng code: chưa có hạn nộp hợp lệ thì không có kế hoạch. Thêm vào đó, người dùng bắt buộc phải xác nhận đã đối chiếu với đề gốc trước khi xuất file.

Rủi ro thứ hai là lộ dữ liệu cá nhân cho bên thứ ba. V2 che các thông tin này trước khi gửi đề đi.

Về trách nhiệm, quyết định cuối cùng thuộc về người dùng, vì AI không có tư cách pháp lý (Buổi 12, slide 12). Người làm sản phẩm như em chịu trách nhiệm thiết kế cho an toàn và công khai các giới hạn.

### Câu có thể bị hỏi thêm: "V2 được sửa dựa trên lỗi của chính bộ test rồi chấm lại trên bộ đó, vậy có phải học tủ không?"

Có rủi ro đó, và em đã ghi rõ trong `evals/v1-vs-v2.md`, mục 8.7. Em giảm rủi ro bằng cách chốt cấu hình V2 trước khi chạy bộ đầy đủ, không nới bộ chấm sau khi thấy kết quả, và giữ nguyên các ca vẫn FAIL. Ba đề thật do giảng viên viết chứ không phải em tự tạo, nên ít bị thiên theo cách em viết ca kiểm thử. Tuy vậy, lỗi của V1 trên các đề này cũng đã được dùng khi phân tích 5-Whys, nên đây chưa phải một tập kiểm tra độc lập hoàn toàn.

### Câu có thể bị hỏi thêm: "gpt-oss chỉ chạy 1 lần mỗi ca thì con số 10/11 có đáng tin không?"

Con số này yếu hơn kết quả của Gemma, vốn chạy 3 lần mỗi ca, vì nó chưa cho thấy độ dao động giữa các lần chạy. Lý do là gói miễn phí của Groq chỉ cho 200 nghìn token mỗi ngày. Em đã ghi điều này trong phần giới hạn, và nếu cần bằng chứng chắc hơn thì nên nhìn vào kết quả của Gemma (từ 3/11 lên 8/11).
