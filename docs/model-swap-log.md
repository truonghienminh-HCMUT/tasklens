# 9. Nhật ký thử nghiệm đổi mô hình (Model Swap Test)

> Sản phẩm #9. Mục tiêu (Buổi 12, slide 25–27): chứng minh kiến trúc TaskLens không "chết" khi đổi model.
> Cùng prompt, cùng schema, cùng bộ kiểm thử, cùng bộ chấm. Chỉ đổi tham số `--model`.

## 9.1. Model được so sánh

| Vai trò | Nhà cung cấp | Model | Hãng / loại | Số lần chạy mỗi ca |
|---|---|---|---|---|
| Model A | Groq (free tier) | `openai/gpt-oss-120b` | OpenAI · open-weight, có suy luận | 1 (giới hạn 200k token/ngày) |
| Model B | Google Gemini API (free tier) | `gemma-4-26b-a4b-it` | Google · open-weight | 3 |

- Hai model thuộc **2 hãng khác nhau**, đều **mã nguồn mở**. Nhờ vậy, cặp này cũng mô phỏng tình huống "công ty chuyển sang model nội bộ" (slide 34, câu 4).
- Tổng chi phí: **0 đồng**.
- Đổi model chỉ là đổi tham số:

```bash
python evals/run_evals.py --version v2 --model groq                         # gpt-oss-120b
python evals/run_evals.py --version v2 --model gemini:gemma-4-26b-a4b-it    # Gemma 4
```

## 9.2. Nhật ký sự kiện (theo thời gian)

| Thời điểm | Sự kiện | Xử lý | Bài học |
|---|---|---|---|
| 28/09 | `llama-3.3-70b-versatile` (model dự định cho Groq) không còn trên Groq | Đổi sang `openai/gpt-oss-120b`: sửa 1 dòng `GROQ_MODEL` trong `.env` | Tên model thương mại là thứ "dễ lỗi thời" (slide 27) |
| 28/09 | `gemini-2.5-flash` vẫn có trong danh sách model nhưng gọi thì trả **404: ngừng cấp cho người dùng mới** | Nâng `scripts/check_setup.py`: ngoài liệt kê, **gọi thử thật** 1 câu | "Có trong danh sách" không phải bằng chứng "dùng được" |
| 28/09 | `gemini-3.8/3.7/3.5-flash` đều trả **503 quá tải**, kể cả sau 6 lần thử lại (~4,5 phút) | Chuyển sang `gemini-3-flash-preview` | Phụ thuộc 1 nhà cung cấp là rủi ro vận hành |
| 28/09 | `gemini-3-flash-preview` hết **quota miễn phí 20 request/ngày/model** sau 16 lượt V1 | Dừng. 16 lượt dở dang lưu ở `evals/results/_exploratory/` làm tham khảo, **không** dùng để so sánh | Gói miễn phí có thể không đủ cho một bộ Evals chạy lặp |
| 28/09 | `qwen/qwen3.8-27b` (Groq) bị chặn bởi **giới hạn 1.000 token đầu ra/phút**: 29/33 lượt lỗi, kể cả khi chờ 70 giây giữa các lượt | Loại. Dữ liệu ở `_exploratory/` | Rate limit có nhiều chiều (request, token vào, token ra, theo phút/ngày), phải thử thật |
| 29/09 | Chốt Model B = `gemma-4-26b-a4b-it`: chạy bằng key Gemini sẵn có, miễn phí, trả JSON đúng ngay lần đầu (~90 giây/lượt) | Đặt `GEMINI_MODEL=gemma-4-26b-a4b-it` | Không cần tạo thêm tài khoản |
| 29/09 | `gemma-4-31b-it` trả **500 INTERNAL** nhiều lần; `gemma-4-26b` thỉnh thoảng 500/503 | Runner tự thử lại; lượt vẫn lỗi được ghi là "lỗi API", không tính là model sai | Phân biệt lỗi hạ tầng với lỗi hành vi |
| 29/09 | gpt-oss chạm **giới hạn 200.000 token/ngày** của Groq | Chạy gpt-oss **1 lần/ca** (ưu tiên khả thi). Runner đọc "try again in …" và chờ đúng thời gian; `--resume` chạy tiếp phần còn thiếu | Thiết kế Evals phải tính tới quota |
| 29/09 | TC09 (110k ký tự) ở V1: gpt-oss **413** (35k token > 8k token/phút); Gemma **429** hết quota | V2 thêm `select_context` với ngân sách riêng từng model (`max_input_chars`) | Giới hạn của model là **tham số của adapter**, không phải của logic |
| 29/09 | V2 lần đầu: ngân sách Groq 14.000 ký tự vẫn **413** (tài liệu + prompt V2 = 9.144 token); ngân sách Gemma 200.000 ký tự làm 3 luồng kẹt ở TC09 (request 30.462 token vượt hạn mức/phút, chờ mãi không qua) | Đo lại bằng số liệu thật: Groq **8.000**, Gemma **36.000** ký tự. Chạy lại **chỉ** các ca có tài liệu vượt ngưỡng mới (TC09, RC03) để V2 nhất quán một cấu hình; kết quả cũ lưu ở `_exploratory/v2__gpt-oss__budget-14k/` | Ước lượng "ký tự/token" lệch theo ngôn ngữ và tokenizer: phải đo (`count_tokens`, thông báo lỗi 413), không đoán |
| 29/09 | Bật JSON schema mode ở V2: với **Gemma** thì suy biến (hết 8.192 token mà text rỗng; bị chặn `RECITATION` vì trích nguyên văn; nội dung vỡ `"content": ": "`) | **Tắt JSON schema riêng cho Gemma** trong `gemini_adapter.py`; gpt-oss vẫn dùng `json_object` | **Cùng một tính năng, model này được lợi, model kia bị hại**: phải đo, không đoán |
| 29/09 | Yêu cầu "tác vụ nhỏ, không suy luận vòng vo" | V2 truyền `effort="low"`: gpt-oss nhận `reasoning_effort=low`; Gemma bỏ qua (không có tham số tương ứng) | Mỗi adapter tự quy đổi cấu hình chung sang API riêng của hãng |

## 9.3. Kết quả so sánh

Nguồn: `evals/results/comparison.md`, `evals/results/failure-modes.md`.

| Tiêu chí | gpt-oss-120b (Groq) | Gemma 4 26B (Gemini API) |
|---|---|---|
| V1 → V2, 11 ca thử lửa | 3/11 → **10/11** | 3/11 → **8/11** |
| V1 → V2, 3 ca đề thật | 0/3 → **3/3** | 0/3 → **3/3** (9/9 lượt) |
| JSON hợp lệ V1 → V2 | 80% → 100% | 90% → 100% |
| Độ trễ trung bình / lượt có gọi model (V2) | ~25 s | ~85 s |
| Kháng injection ở V1 (chưa có lớp bảo vệ) | **Làm theo** (chèn mã, chép lộ system prompt) | **Chống được** 3/3 lượt |
| Output bị cắt ở V1 | Có (mặc định 3.072 token; model tiêu token cho suy luận) | Không |
| Dùng JSON schema mode | Có lợi → **bật** (`json_object`) | Suy biến → **tắt** |
| Ngân sách tài liệu (theo gói miễn phí) | 8.000 ký tự | 36.000 ký tự |
| TC09 (tài liệu ~50 trang) ở V2 | 0/1 (rút gọn mạnh, mất danh sách sản phẩm nộp) | 1/3 (đúng hạn nộp; 2/3 lượt báo thiếu nội dung đề tài) |
| Ca V2 chưa đạt | TC09 | TC09, TC04 (ghi đúng nhận xét nhưng sai trường), TC03 (1/3 lượt) |

## 9.4. Kết luận

1. **Kiến trúc sống sót qua đổi model.** Cùng một prompt V2, cùng các cổng code, cùng bộ test: cả 2 model của 2 hãng đều tăng từ 3/11 lên 8–10/11, và 3/3 trên đề thật (cả 2 model). Đúng thông điệp của slide 27: *model là linh kiện, kiến trúc mới là tài sản*.
2. **Mọi khác biệt giữa các model đều nằm gọn trong adapter**, gồm 3 tham số: bật/tắt JSON mode, ngân sách tài liệu, mức suy luận. Không dòng logic nào của pipeline phải sửa khi đổi model.
3. **An toàn không được phó mặc cho model.** Gemma tự chống injection còn gpt-oss thì không. Nếu chỉ thử trên Gemma, ta sẽ kết luận sai rằng "hệ thống an toàn". Phải có lớp bảo vệ độc lập với model và phải thử trên nhiều model.
4. **Trả lời câu hỏi "công ty chuyển sang model nội bộ thì mất bao lâu"** (slide 34): viết 1 adapter (Groq: 15 dòng, vì API tương thích OpenAI), chạy `run_evals.py --model <mới>` để có số liệu so sánh trong vài giờ, rồi chỉnh các tham số adapter nếu Evals chỉ ra vấn đề (như đã làm với Gemma).
5. **Chi phí vận hành thật của gói miễn phí** (quota, rate limit, model bị gỡ, quá tải) quyết định cả thiết kế Evals: chạy 1 lần/ca cho gpt-oss, runner có `--resume` và tự chờ theo "retry after".
