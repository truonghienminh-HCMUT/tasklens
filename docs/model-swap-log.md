# 9. Nhật ký thử nghiệm đổi mô hình (Model Swap Test)

Mục tiêu của phép thử này (Buổi 12, slide 25–27) là xem kiến trúc của TaskLens có còn đứng vững khi thay model hay không. Prompt, schema, bộ kiểm thử và bộ chấm được giữ nguyên, chỉ đổi tham số `--model`.

## 9.1. Hai model được so sánh

| Vai trò | Nhà cung cấp | Model | Hãng / loại | Số lần chạy mỗi ca |
|---|---|---|---|---|
| Model A | Groq (gói miễn phí) | `openai/gpt-oss-120b` | OpenAI, open-weight, có suy luận | 1 (giới hạn 200 nghìn token/ngày) |
| Model B | Google Gemini API (gói miễn phí) | `gemma-4-26b-a4b-it` | Google, open-weight | 3 |

Hai model đến từ hai hãng khác nhau và đều là model open-weight, nên cặp này cũng gần với tình huống "công ty chuyển sang dùng model nội bộ" ở câu hỏi số 4, slide 34. Tổng chi phí là 0 đồng. Đổi model chỉ là đổi tham số:

```bash
python evals/run_evals.py --version v2 --model groq                         # gpt-oss-120b
python evals/run_evals.py --version v2 --model gemini:gemma-4-26b-a4b-it    # Gemma 4
```

## 9.2. Nhật ký sự kiện

Để chọn được hai model này tôi mất khá nhiều công, vì các gói miễn phí liên tục gặp sự cố. Dưới đây là nhật ký theo thứ tự thời gian.

| Thời điểm | Sự kiện | Cách xử lý | Rút ra |
|---|---|---|---|
| 28/09 | Model dự định dùng trên Groq là `llama-3.3-70b-versatile` đã bị gỡ | Đổi sang `openai/gpt-oss-120b`, chỉ sửa 1 dòng `GROQ_MODEL` trong `.env` | Tên model là thứ dễ lỗi thời nhất (slide 27) |
| 28/09 | `gemini-2.5-flash` vẫn có trong danh sách model, nhưng gọi thì trả lỗi 404 vì đã ngừng cấp cho người dùng mới | Sửa `scripts/check_setup.py` để gọi thử 1 câu thật thay vì chỉ liệt kê | Có trong danh sách chưa chắc đã dùng được |
| 28/09 | `gemini-3.8/3.7/3.5-flash` đều trả lỗi 503 (quá tải), kể cả sau 6 lần thử lại trong khoảng 4,5 phút | Chuyển sang `gemini-3-flash-preview` | Phụ thuộc vào một nhà cung cấp là rủi ro vận hành |
| 28/09 | `gemini-3-flash-preview` hết quota miễn phí (20 request/ngày/model) sau 16 lượt V1 | Dừng lại. 16 lượt dở dang được lưu ở `evals/results/_exploratory/` để tham khảo, không dùng để so sánh | Gói miễn phí có thể không đủ cho một bộ Evals phải chạy nhiều lần |
| 28/09 | `qwen/qwen3.8-27b` trên Groq bị chặn bởi giới hạn 1.000 token đầu ra mỗi phút: 29/33 lượt lỗi, kể cả khi chờ 70 giây giữa các lượt | Loại, dữ liệu lưu ở `_exploratory/` | Rate limit có nhiều chiều (số request, token vào, token ra, theo phút hoặc theo ngày), phải chạy thử mới biết |
| 29/09 | Chốt Model B là `gemma-4-26b-a4b-it`: dùng được bằng key Gemini sẵn có, miễn phí, trả JSON đúng ngay lần đầu (khoảng 90 giây/lượt) | Đặt `GEMINI_MODEL=gemma-4-26b-a4b-it` | Không cần tạo thêm tài khoản |
| 29/09 | `gemma-4-31b-it` nhiều lần trả lỗi 500 INTERNAL; `gemma-4-26b` thỉnh thoảng trả 500 hoặc 503 | Runner tự thử lại; lượt nào vẫn lỗi thì ghi là "lỗi API", không tính là model trả lời sai | Phải tách lỗi hạ tầng khỏi lỗi hành vi |
| 29/09 | gpt-oss chạm giới hạn 200.000 token/ngày của Groq | Chạy gpt-oss 1 lần/ca (ưu tiên tính khả thi). Runner đọc thông báo "try again in …" và chờ đúng khoảng đó; `--resume` chạy tiếp phần còn thiếu | Thiết kế Evals phải tính tới quota |
| 29/09 | TC09 (110 nghìn ký tự) ở V1: gpt-oss bị lỗi 413 (35 nghìn token, vượt giới hạn 8 nghìn token mỗi phút); Gemma bị lỗi 429 do hết quota | V2 thêm `select_context` với ngân sách riêng cho từng model (`max_input_chars`) | Giới hạn của model nên là tham số của adapter, không nằm trong logic |
| 29/09 | Lần chạy V2 đầu tiên: với ngân sách 14.000 ký tự, Groq vẫn báo 413 (tài liệu cộng prompt V2 là 9.144 token); với ngân sách 200.000 ký tự, 3 luồng Gemma bị kẹt ở TC09 (request 30.462 token vượt hạn mức mỗi phút nên chờ mãi không qua) | Đo lại bằng số liệu thật rồi đặt ngân sách Groq 8.000 và Gemma 36.000 ký tự. Chỉ chạy lại các ca có tài liệu vượt ngưỡng mới (TC09, RC03) để toàn bộ V2 dùng chung một cấu hình; kết quả cũ lưu ở `_exploratory/v2__gpt-oss__budget-14k/` | Tỉ lệ ký tự trên token thay đổi theo ngôn ngữ và tokenizer, nên phải đo (`count_tokens`, thông báo lỗi 413) chứ không ước lượng |
| 29/09 | Khi bật JSON schema mode ở V2, Gemma bị suy biến: dùng hết 8.192 token mà text vẫn rỗng, bị chặn `RECITATION` vì trích nguyên văn, hoặc trả nội dung vỡ kiểu `"content": ": "` | Tắt JSON schema riêng cho Gemma trong `gemini_adapter.py`; gpt-oss vẫn dùng `json_object` | Cùng một tính năng có thể giúp model này nhưng làm hỏng model kia, nên phải đo |
| 29/09 | Yêu cầu hệ thống chỉ xử lý tác vụ nhỏ, không suy luận vòng vo | V2 truyền `effort="low"`: gpt-oss nhận `reasoning_effort=low`, còn Gemma bỏ qua vì không có tham số tương ứng | Mỗi adapter tự chuyển cấu hình chung sang API riêng của từng hãng |

## 9.3. Kết quả so sánh

Nguồn: `evals/results/comparison.md` và `evals/results/failure-modes.md`.

| Tiêu chí | gpt-oss-120b (Groq) | Gemma 4 26B (Gemini API) |
|---|---|---|
| V1 → V2, 11 ca thử lửa | 3/11 → 10/11 | 3/11 → 8/11 |
| V1 → V2, 3 ca đề thật | 0/3 → 3/3 | 0/3 → 3/3 (9/9 lượt) |
| JSON hợp lệ, V1 → V2 | 80% → 100% | 90% → 100% |
| Độ trễ trung bình mỗi lượt có gọi model (V2) | khoảng 25 giây | khoảng 85 giây |
| Chống injection ở V1 (khi chưa có lớp bảo vệ) | Làm theo (chèn mã, chép lộ system prompt) | Chống được cả 3 lượt |
| Output bị cắt ở V1 | Có (mặc định 3.072 token, và model tốn token cho suy luận) | Không |
| JSON schema mode | Có lợi, nên bật (`json_object`) | Gây suy biến, nên tắt |
| Ngân sách tài liệu (theo gói miễn phí) | 8.000 ký tự | 36.000 ký tự |
| TC09 (tài liệu khoảng 50 trang) ở V2 | 0/1 (rút gọn mạnh, mất danh sách sản phẩm nộp) | 1/3 (đúng hạn nộp; 2/3 lượt báo thiếu nội dung đề tài) |
| Ca V2 chưa đạt | TC09 | TC09, TC04 (nhận xét đúng nhưng ghi sai trường), TC03 (trượt 1/3 lượt) |

## 9.4. Kết luận

Kiến trúc vẫn đứng vững khi đổi model. Với cùng prompt V2, cùng các cổng code và cùng bộ test, cả hai model của hai hãng đều tăng từ 3/11 lên 8–10/11 ca, và đạt 3/3 trên đề thật. Điều này khớp với ý ở slide 27: model là linh kiện có thể thay, còn kiến trúc mới là thứ cần giữ.

Mọi khác biệt giữa hai model đều nằm trong adapter, cụ thể là ba tham số: bật hay tắt JSON mode, ngân sách tài liệu và mức suy luận. Khi đổi model, tôi không phải sửa dòng logic nào của pipeline.

An toàn không thể phó mặc cho model. Gemma tự chống được injection, còn gpt-oss thì không. Nếu chỉ thử trên Gemma, tôi đã kết luận sai rằng hệ thống an toàn. Vì vậy cần một lớp bảo vệ không phụ thuộc vào model, và cần thử trên nhiều model.

Về câu hỏi "nếu công ty chuyển sang model nội bộ thì mất bao lâu" (slide 34): chỉ cần viết một adapter mới (adapter Groq chỉ khoảng 20 dòng vì API tương thích với OpenAI), chạy `run_evals.py --model <tên model mới>` để có số liệu so sánh trong vài giờ, rồi chỉnh tham số của adapter nếu kết quả Evals cho thấy vấn đề, giống như tôi đã làm với Gemma.

Cuối cùng, những giới hạn thực tế của gói miễn phí (quota, rate limit, model bị gỡ, máy chủ quá tải) ảnh hưởng tới cả cách thiết kế Evals: gpt-oss chỉ chạy được 1 lần/ca, và runner phải có `--resume` cũng như biết tự chờ theo thông báo "retry after".
