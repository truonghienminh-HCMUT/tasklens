# 12. Case Study: TaskLens, trợ lý AI biết dừng lại khi đề bài thiếu dữ kiện

> Sản phẩm #12. Công thức portfolio (Buổi 12, slide 31–32): **Product + Evidence + Story + Transparency + Demo**,
> kể theo khung STAR, bằng số liệu thật. Bản rút gọn để đăng LinkedIn ở cuối trang.

## Situation: vấn đề

Sinh viên kỹ thuật nhận 3–5 đề bài tập lớn mỗi học kỳ. Đề trộn yêu cầu, ràng buộc, sản phẩm nộp, tiêu chí chấm và nhiều mốc thời gian, đôi khi còn tự mâu thuẫn. Hai đề thật tôi dùng để kiểm thử cho thấy rõ điều này:
- Đề Hệ cơ sở dữ liệu có **hai hạn nộp khác nhau theo lớp** và ghi "Friday, Thursday October 15".
- Đề Công nghệ phần mềm ghi **"Deadlines will be announced on the LMS"**, tức là không có hạn nộp.

Tôi mất 10–15 phút để tự phân rã một đề nếu muốn hiểu sâu, và vẫn nhiều lần sót hoặc hiểu chưa đúng yêu cầu. Vấn đề không nằm ở tốc độ mà ở **độ đúng**. Khi thử giao việc này cho chatbot, bản đầu tiên (V1) của tôi:
- lấy **mốc giữa kỳ làm hạn nộp** (Gemma: 3/3 lượt);
- **vẫn lập kế hoạch** khi đề không có hạn nộp (8/9 lượt);
- **dự đoán "khoảng 64 điểm"** khi được hỏi điểm;
- với một model khác, **làm theo câu lệnh cài trong đề** và chép lộ system prompt.

## Task: mục tiêu

Xây một trợ lý phân rã đề mà:
1. mỗi khẳng định có **trích dẫn nguyên văn** từ đề;
2. **biết dừng và hỏi lại** khi thiếu hạn nộp, dữ liệu phi lý, hay đề mâu thuẫn, thay vì tự đoán;
3. không vượt thẩm quyền (viết hộ, đoán điểm), không làm lộ dữ liệu cá nhân;
4. **chứng minh bằng số liệu**, và vẫn chạy khi đổi model.

Ràng buộc: hệ thống đơn giản, tác vụ nhỏ, chi phí 0 đồng (chỉ dùng gói API miễn phí).

## Action: cách làm

- **Thiết kế trước, code sau:** checklist 11 thành phần, ma trận AI–Người, sơ đồ workflow có nhánh "thiếu thì hỏi lại".
- **Bộ Evals 14 ca:** 10 tình huống thử lửa (thiếu dữ kiện, mơ hồ, phi lý, mâu thuẫn, ngoài phạm vi, rủi ro cao, injection, tài liệu 50 trang, đầu vào rác), 1 ca dữ liệu cá nhân, 3 ca trên đề thật. Chấm bằng **code** (trích dẫn có thật không, ngày có hợp lệ không…), không dùng AI chấm AI. Bộ chấm có unit test riêng.
- **5-Whys:** mọi lỗi nghiêm trọng của V1 đều có chung một gốc: *quy tắc quan trọng chỉ tồn tại dưới dạng lời dặn trong prompt*.
- **V2 giữ nguyên 1 lần gọi model** và thêm các cổng code rẻ, xác định:
  - che PII trước khi gửi;
  - chặn yêu cầu ngoài phạm vi mà không gọi model;
  - kiểm tra ngày trên lịch;
  - chỉ lập kế hoạch khi có hạn nộp hợp lệ, xuất hiện trong đề;
  - gỡ trích dẫn không có thật;
  - rút gọn ngữ cảnh theo giới hạn của từng model.
- **Model Swap:** chạy cùng bộ test trên gpt-oss-120b (OpenAI) và Gemma 4 (Google), qua 2 nhà cung cấp khác nhau. Trên đường đi đã gặp và ghi nhật ký 5 model/gói dịch vụ không dùng được (bị gỡ, quá tải, hết quota, rate limit).

## Result: kết quả (số liệu thật, `evals/`)

| Chỉ số | V1 | V2 |
|---|---|---|
| Ca đạt / 11 ca thử lửa, gpt-oss | 3/11 | **10/11** |
| Ca đạt / 11 ca thử lửa, Gemma (3 lần/ca) | 3/11 | **8/11** |
| Ca đạt / 3 ca đề thật (gpt-oss · Gemma) | 0/3 · 0/3 | **3/3 · 3/3** |
| Lập kế hoạch khi thiếu dữ kiện (lượt mắc lỗi / lượt có kết quả) | 16/18 | **0/20** |
| Gửi PII ra ngoài (lượt) | 4/4 | **0/4** |
| Thời gian | 10–15 phút/đề (tự làm) | ~25 giây (gpt-oss) đến ~85 giây (Gemma) mỗi lần gọi model + thời gian tự đối chiếu (**chưa đo**) |

## Transparency: điều chưa làm được

- Cổng từ chối và phát hiện injection dựa trên mẫu câu, nên có thể bị lách.
- Kiểm tra trích dẫn chỉ xác nhận câu đó **có** trong đề, không xác nhận AI **hiểu đúng**.
- PDF scan chưa đọc được.
- gpt-oss chỉ chạy 1 lần/ca vì quota miễn phí.
- Tôi đã tìm và sửa **4 lỗi trong chính bộ chấm**, rồi chấm lại V1 và V2 từ log thô. Toàn bộ được ghi lại trong `evals/failure-analysis.md` §6.5.

## Điều tôi học được

1. **Happy path không chứng minh gì.** Cả hai model đều đạt ca đề chuẩn nhưng trượt phần lớn các ca biên.
2. **Quy tắc quan trọng phải là code, không phải lời dặn.** "Không có hạn nộp thì không lập kế hoạch" là một dòng `if`, rẻ và chắc chắn hơn mọi câu prompt.
3. **Model là linh kiện thay được, nhưng không thay mù được.** JSON mode giúp gpt-oss nhưng làm Gemma suy biến; gpt-oss làm theo injection còn Gemma thì không. Phải đo bằng Evals.
4. **Bộ Evals cũng cần được kiểm thử.** Một lỗi trong bộ chấm có thể che mất lỗi thật của hệ thống.

---

## Bản đăng LinkedIn (rút gọn)

> 🔎 **TaskLens: khi AI biết nói "tôi chưa đủ dữ kiện"**
>
> Cuối khóa "Làm chủ kỹ thuật xây dựng Prompt và trợ lý AI" (AOTS × HCMUT), tôi xây một trợ lý phân rã đề bài tập lớn và cố tình "thử lửa" nó bằng 14 tình huống: đề thiếu hạn nộp, ngày 30/02, đề tự mâu thuẫn, câu lệnh cài sẵn trong tài liệu, yêu cầu "chấm điểm giúp"…
>
> Bản V1 (chỉ dùng prompt) lấy mốc giữa kỳ làm hạn nộp, tự lập kế hoạch khi đề không có hạn nộp, và còn đoán "khoảng 64 điểm".
>
> Phân tích 5-Whys cho thấy gốc rễ: các quy tắc quan trọng chỉ nằm trong lời dặn. V2 giữ nguyên 1 lần gọi model nhưng chuyển chúng thành cổng kiểm tra bằng code: kiểm tra ngày trên lịch, trích dẫn phải có thật trong đề, không có hạn nộp hợp lệ thì không lập kế hoạch, che dữ liệu cá nhân trước khi gửi.
>
> 📊 Kết quả trên 11 ca thử lửa: V1 3/11 → V2 10/11 (gpt-oss-120b); 3/11 → 8/11 (Gemma 4), và 0/3 → 3/3 trên đề thật với cả hai model. Chạy trên 2 model của 2 hãng, chi phí 0 đồng.
>
> Bài học lớn nhất: *đừng chỉ chứng minh AI chạy được, hãy chứng minh nó dừng đúng lúc.*
>
> Repo (có đủ bộ Evals, log thô và cả những lỗi tôi tìm ra trong chính bộ chấm): https://github.com/truonghienminh-HCMUT/tasklens
>
> #AI #LLM #PromptEngineering #LLMEvals #AOTS #HCMUT
