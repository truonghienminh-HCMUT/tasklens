# 12. Case study: TaskLens, trợ lý AI biết dừng khi đề bài thiếu dữ kiện

Bài viết kể lại quá trình làm TaskLens theo khung STAR, dùng số liệu thật từ repo. Theo gợi ý ở Buổi 12 (slide 31–32), một case study cho portfolio nên có đủ sản phẩm, bằng chứng, câu chuyện, sự minh bạch và demo. Bản rút gọn để đăng LinkedIn nằm ở cuối trang.

## Bối cảnh

Mỗi học kỳ tôi nhận 3–5 đề bài tập lớn. Đề thường trộn lẫn yêu cầu, ràng buộc, sản phẩm phải nộp, tiêu chí chấm và nhiều mốc thời gian, có khi còn tự mâu thuẫn. Hai đề thật tôi dùng để kiểm thử là ví dụ rõ nhất. Đề Hệ cơ sở dữ liệu có hai hạn nộp khác nhau theo lớp, và có dòng ghi "Friday, Thursday October 15". Đề Công nghệ phần mềm thì không có hạn nộp, chỉ ghi "Deadlines will be announced on the LMS".

Tự phân rã một đề mất của tôi 10–15 phút nếu muốn hiểu kỹ, và tôi vẫn nhiều lần sót hoặc hiểu sai yêu cầu. Vấn đề của tôi nằm ở độ chính xác hơn là tốc độ. Khi thử giao việc này cho chatbot, bản đầu tiên (V1) mắc đúng những lỗi tôi lo. Với Gemma, nó lấy mốc giữa kỳ làm hạn nộp ở cả 3/3 lượt, vẫn lập kế hoạch khi đề thiếu hoặc sai dữ kiện (8/9 lượt), và còn dự đoán "khoảng 64 điểm" khi được hỏi điểm. Với gpt-oss, nó làm theo câu lệnh cài sẵn trong đề và chép lộ cả system prompt.

## Mục tiêu

Tôi muốn làm một trợ lý phân rã đề đáp ứng bốn điều. Thứ nhất, mỗi khẳng định phải có trích dẫn nguyên văn từ đề. Thứ hai, khi thiếu hạn nộp, gặp dữ liệu phi lý hay đề mâu thuẫn, nó phải dừng lại và hỏi thay vì tự đoán. Thứ ba, nó không được vượt thẩm quyền (viết hộ, đoán điểm) và không được làm lộ dữ liệu cá nhân. Thứ tư, mọi điều trên phải được chứng minh bằng số liệu, và hệ thống vẫn phải chạy tốt khi đổi model.

Tôi cũng tự đặt ra ràng buộc: hệ thống phải đơn giản, chỉ xử lý tác vụ nhỏ, và không tốn tiền (chỉ dùng gói API miễn phí).

## Cách làm

Tôi thiết kế trước rồi mới viết code: điền checklist 11 thành phần, lập ma trận phân công giữa AI và con người, và vẽ sơ đồ workflow có nhánh "thiếu thì hỏi lại".

Sau đó tôi xây bộ Evals gồm 14 ca: 10 tình huống thử lửa (thiếu dữ kiện, mơ hồ, phi lý, mâu thuẫn, ngoài phạm vi, rủi ro cao, injection, tài liệu 50 trang, đầu vào rác), 1 ca về dữ liệu cá nhân và 3 ca trên đề thật. Mọi ca đều được chấm bằng code, chẳng hạn kiểm tra trích dẫn có thật không hay ngày có hợp lệ không, chứ không dùng AI để chấm AI. Bộ chấm cũng có unit test riêng.

Khi phân tích 5-Whys các lỗi của V1, tôi thấy chúng có chung một gốc: những quy tắc quan trọng chỉ tồn tại dưới dạng lời dặn trong prompt. Vì vậy V2 vẫn chỉ gọi model một lần, nhưng thêm các bước kiểm tra bằng code, vốn rẻ và cho kết quả xác định: che dữ liệu cá nhân trước khi gửi, chặn yêu cầu ngoài phạm vi mà không cần gọi model, kiểm tra ngày trên lịch, chỉ lập kế hoạch khi có hạn nộp hợp lệ xuất hiện trong đề, gỡ trích dẫn không có thật, và rút gọn tài liệu theo giới hạn của từng model.

Cuối cùng tôi chạy cùng bộ test trên hai model của hai hãng, gpt-oss-120b (OpenAI) và Gemma 4 (Google), qua hai nhà cung cấp khác nhau. Trước khi chốt được cặp này, tôi gặp 5 trường hợp model hoặc gói dịch vụ không dùng được vì bị gỡ, quá tải, hết quota hay vướng rate limit, và ghi lại tất cả trong nhật ký.

## Kết quả

Số liệu thật, lấy từ thư mục `evals/`:

| Chỉ số | V1 | V2 |
|---|---|---|
| Số ca đạt trên 11 ca thử lửa, gpt-oss (1 lần/ca) | 3/11 | 10/11 |
| Số ca đạt trên 11 ca thử lửa, Gemma (3 lần/ca) | 3/11 | 8/11 |
| Số ca đạt trên 3 đề thật, gpt-oss và Gemma | 0/3 và 0/3 | 3/3 và 3/3 |
| Lập kế hoạch khi thiếu dữ kiện (lượt mắc lỗi / lượt có kết quả) | 16/18 | 0/20 |
| Gửi dữ liệu cá nhân ra ngoài (lượt) | 4/4 | 0/4 |
| Thời gian | 10–15 phút một đề (tự làm) | Khoảng 25 giây (gpt-oss) đến 85 giây (Gemma) cho mỗi lần gọi model, cộng thêm thời gian tự đối chiếu (chưa đo) |

## Những gì chưa làm được

Bộ lọc yêu cầu ngoài phạm vi và bộ phát hiện injection dựa trên mẫu câu, nên có thể bị lách. Bước kiểm tra trích dẫn chỉ xác nhận câu trích có trong đề, chứ không xác nhận AI hiểu đúng câu đó. PDF scan chưa đọc được. gpt-oss chỉ chạy 1 lần/ca vì quota của gói miễn phí. Ngoài ra, tôi đã tìm và sửa 4 lỗi trong chính bộ chấm, sau đó chấm lại cả V1 và V2 từ log thô; mọi thứ được ghi ở `evals/failure-analysis.md`, mục 6.5.

## Điều tôi học được

Chạy đúng ở ca dễ chưa chứng minh được gì. Cả hai model đều qua ca đề chuẩn nhưng trượt phần lớn các ca biên.

Quy tắc quan trọng nên được viết thành code thay vì dặn trong prompt. "Không có hạn nộp thì không lập kế hoạch" chỉ là một câu lệnh `if`, vừa rẻ vừa chắc chắn hơn bất kỳ lời dặn nào.

Model có thể thay được, nhưng không thể thay mà không kiểm tra lại. JSON mode giúp gpt-oss nhưng làm Gemma suy biến; gpt-oss làm theo injection còn Gemma thì không. Chỉ có chạy Evals mới biết được.

Bản thân bộ Evals cũng cần được kiểm thử, vì một lỗi trong bộ chấm có thể che mất lỗi thật của hệ thống.

---

## Bản đăng LinkedIn

> **TaskLens: khi AI biết nói "tôi chưa đủ dữ kiện"**
>
> Trong bài tập cuối khóa "Làm chủ kỹ thuật xây dựng Prompt và trợ lý AI" (AOTS × HCMUT), tôi làm một trợ lý giúp phân rã đề bài tập lớn, rồi thử làm khó nó bằng 14 tình huống: đề không có hạn nộp, hạn nộp ngày 30/02, đề tự mâu thuẫn, câu lệnh cài sẵn trong tài liệu, hay nhờ "chấm điểm giúp".
>
> Bản đầu tiên chỉ dựa vào prompt. Nó lấy mốc giữa kỳ làm hạn nộp, tự lập kế hoạch dù đề không có hạn nộp, thậm chí còn đoán "khoảng 64 điểm".
>
> Khi tìm nguyên nhân, tôi nhận ra vấn đề nằm ở chỗ các quy tắc quan trọng chỉ được dặn trong prompt. Ở bản thứ hai, tôi vẫn chỉ gọi model một lần, nhưng chuyển các quy tắc đó thành bước kiểm tra bằng code: ngày phải có thật trên lịch, trích dẫn phải có trong đề, chưa có hạn nộp hợp lệ thì không lập kế hoạch, và dữ liệu cá nhân được che trước khi gửi đi.
>
> Trên 11 ca thử, kết quả tăng từ 3/11 lên 10/11 với gpt-oss-120b và từ 3/11 lên 8/11 với Gemma 4. Trên 3 đề thật, cả hai model đều tăng từ 0/3 lên 3/3. Tất cả chạy bằng gói API miễn phí.
>
> Điều tôi rút ra: chứng minh AI chạy được là chưa đủ, còn phải chứng minh nó biết dừng đúng lúc.
>
> Repo có đủ bộ Evals, log thô, và cả những lỗi tôi tìm ra trong chính bộ chấm: https://github.com/truonghienminh-HCMUT/tasklens
>
> #AI #LLM #PromptEngineering #LLMEvals #AOTS #HCMUT
