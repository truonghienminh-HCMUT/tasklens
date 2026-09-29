# 10. Hướng dẫn sử dụng, giới hạn và khuyến cáo an toàn

> Sản phẩm #10. Bàn giao minh bạch trả lời 4 câu hỏi (Buổi 12, slide 29):
> sản phẩm tạo giá trị gì cho ai, input/output ra sao, người khác chạy thế nào, giới hạn và rủi ro nào phải công khai.

## 10.1. TaskLens làm gì, cho ai

Cho **sinh viên** vừa nhận đề bài tập lớn. TaskLens đọc đề và trả về:
- yêu cầu, ràng buộc, sản phẩm phải nộp, tiêu chí chấm, hạn nộp, **mỗi mục kèm câu trích nguyên văn** để bạn tự đối chiếu
- những gì **đề còn thiếu, mơ hồ, mâu thuẫn hoặc phi lý**, kèm câu hỏi nên gửi giảng viên
- **kế hoạch thực hiện, chỉ khi đủ dữ kiện**; thiếu hạn nộp hợp lệ thì TaskLens dừng lại và hỏi

TaskLens **không** làm bài hộ, **không** dự đoán điểm, **không** tự nộp bài hay gửi email.

## 10.2. Cài đặt và chạy

```bash
pip install -r requirements.txt
cp .env.example .env            # điền GEMINI_API_KEY và/hoặc GROQ_API_KEY (đều có gói miễn phí)
python scripts/check_setup.py   # kiểm tra key và gọi thử model
streamlit run app.py            # mở http://localhost:8501
```

**Cách dùng giao diện:**
1. Chọn phiên bản **V2** (khuyến nghị) và model ở thanh bên trái.
2. Tải đề (PDF có lớp chữ, DOCX, TXT) hoặc dán nội dung.
3. Ghi yêu cầu, ví dụ: *"Tôi học lớp CC04. Phân rã đề và lập kế hoạch cho tôi."* Nếu đề ghi hạn nộp khác nhau theo lớp, **hãy nói lớp của bạn**.
4. Nếu đề không ghi hạn nộp mà bạn đã biết (ví dụ giảng viên thông báo trên LMS), điền vào ô "Hạn nộp".
5. Đọc phần **"Cần bạn bổ sung / làm rõ"** và các **ghi chú của hệ thống** (PII đã che, trích dẫn bị gỡ, tài liệu bị rút gọn...).
6. Đối chiếu với đề gốc, tick **"Tôi đã đối chiếu..."** rồi mới tải kết quả (Markdown/JSON).

**Chạy bộ kiểm thử:** xem `README.md` và `evals/`.

## 10.3. Input / Output

| | Mô tả |
|---|---|
| Input | Đề bài (PDF có lớp chữ / DOCX / TXT / MD, hoặc văn bản dán); yêu cầu của người dùng; hạn nộp đã biết (tùy chọn) |
| Output | JSON theo schema cố định `src/tasklens/schema.py`, hiển thị thành bảng và xuất được Markdown |
| Trạng thái | `OK` (đủ dữ kiện, có kế hoạch) · `NEED_INFO` (cần bạn bổ sung, **không** có kế hoạch) · `REFUSED` (yêu cầu ngoài phạm vi) · `INVALID_INPUT` (không phải đề bài đọc được) |

## 10.4. Dữ liệu của bạn đi đâu

1. Máy của bạn **làm sạch văn bản và che** email, số điện thoại, MSSV (dãy 7–10 chữ số), API key, mật khẩu, **trước khi gửi**.
2. Đề đã che được gửi tới **một** nhà cung cấp model bạn chọn:
   - Google (Gemini API, model Gemma)
   - hoặc Groq (model gpt-oss)

   Hãy đọc điều khoản dữ liệu của họ. **Gói miễn phí của một số nhà cung cấp (ví dụ Gemini API) có thể dùng nội dung gửi lên để cải thiện dịch vụ.** Đừng gửi tài liệu mật hay tài liệu bạn không có quyền chia sẻ.
3. File `logs/audit.jsonl` chỉ ghi siêu dữ liệu: thời điểm, model, trạng thái, số token, độ dài và mã băm của đề. **Không lưu nội dung đề hay câu trả lời.**
4. API key nằm trong `.env`, đã bị `.gitignore` chặn, không bao giờ lên GitHub.

## 10.5. Giới hạn đã biết (công khai, có bằng chứng)

| # | Giới hạn | Bằng chứng / nguồn | Hệ quả cho người dùng |
|---|---|---|---|
| 1 | **Cổng từ chối dựa trên từ khóa.** Có thể bị lách nếu diễn đạt khác (ví dụ "làm giúp mình phần backend"). Lớp thứ hai là chính sách trong prompt, nhưng model có thể vẫn làm theo | `sanitize.classify_request`; TC06/TC07 chỉ thử 1 cách diễn đạt | Không dùng TaskLens làm cơ chế chống gian lận |
| 2 | **Phát hiện injection dựa trên mẫu câu.** Câu ra lệnh khéo léo, không dùng các cụm quen thuộc, có thể lọt. Cổng validate chỉ gỡ được mã/chuỗi mà câu nghi vấn chỉ định rõ | `sanitize.find_injections`; TC08 | Khi hệ thống báo "đoạn văn đáng ngờ", hãy đọc kỹ đoạn đó trong đề gốc |
| 3 | **Rút gọn ngữ cảnh có thể bỏ sót.** Tài liệu vượt ngân sách của model (gói miễn phí: Groq 8.000 ký tự, Gemma 36.000 ký tự) được lọc theo từ khóa; yêu cầu nằm ở đoạn không chứa từ khóa có thể bị lược | TC09 ở V2: hạn nộp tìm **đúng**, nhưng gpt-oss chỉ liệt kê 2/3 sản phẩm nộp, Gemma 2/3 lượt báo "thiếu nội dung đề tài" vì mục "Yêu cầu chức năng" bị lược | Hệ thống luôn báo khi đã rút gọn: hãy tự đọc phần bị lược; với tài liệu dài, dán riêng phần đề bài |
| 4 | **Kiểm tra trích dẫn chỉ xác nhận câu đó CÓ trong đề**, không xác nhận AI **hiểu đúng** câu đó | `validate.is_grounded` | Vẫn phải đọc "Nội dung" và đối chiếu, đây là lý do có bước Human checkpoint |
| 5 | **PDF scan (ảnh), bảng biểu phức tạp, sơ đồ** không đọc được: chỉ dùng lớp chữ của PDF (Buổi 4: "điểm mù PDF quét") | TC10; `io_utils` | Hệ thống trả `INVALID_INPUT`; hãy dán văn bản hoặc dùng OCR trước |
| 6 | **Che PII theo mẫu:** tên người **không** bị che; dãy 7–10 chữ số bất kỳ bị coi là MSSV (có thể che nhầm số khác) | `sanitize.mask_pii`; TC11 | Đừng đưa danh sách thông tin cá nhân không cần thiết vào đề |
| 7 | **Kết quả dao động giữa các lần chạy** (cùng đề, cùng model) | Cột "Runs Pass" trong `evals/results/*.csv` | Chạy lại nếu thấy thiếu; luôn đối chiếu đề gốc |
| 8 | **Phụ thuộc gói miễn phí:** quota theo ngày/phút, model bị gỡ hoặc quá tải (lỗi 404/429/500/503) | `docs/model-swap-log.md` | Có thể phải chờ hoặc đổi model; logic không đổi |
| 9 | **Chỉ nhận ngày dạng số hoặc tiếng Anh/Việt thông dụng.** Cách viết lạ ("thứ Sáu tuần 15") không được hiểu là hạn nộp | `validate.dates_in` | Điền hạn nộp vào ô riêng nếu hệ thống không nhận ra |
| 10 | **Bộ kiểm thử có giới hạn:** 11 ca tổng hợp và 3 ca đề thật; gpt-oss chỉ chạy 1 lần/ca do quota | `evals/` | Kết quả là bằng chứng có phạm vi, không phải bảo đảm tuyệt đối |

## 10.6. Khuyến cáo an toàn khi sử dụng

1. **Đề gốc và thông báo của giảng viên luôn là căn cứ cuối cùng.** TaskLens là trợ lý đọc đề, không thay thế việc bạn đọc đề.
2. **Khai báo việc dùng AI** nếu môn học yêu cầu. Ví dụ, đề Công nghệ phần mềm HK261 **bắt buộc** khai báo công cụ, phạm vi và mức đóng góp của AI.
3. Không dùng TaskLens để hỏi điểm số, khiếu nại điểm, hay bất kỳ quyết định nào thuộc thẩm quyền giảng viên.
4. Không tải lên tài liệu mật, tài liệu nội bộ, hay thông tin cá nhân của người khác.
5. Khi TaskLens trả `NEED_INFO`, **đừng tự đoán rồi ép hệ thống lập kế hoạch**: hãy hỏi giảng viên.

## 10.7. Trách nhiệm

Mọi quyết định cuối cùng (làm gì, nộp gì, khi nào) thuộc về **người dùng**. TaskLens không có tư cách pháp lý và không chịu trách nhiệm thay (Buổi 12, slide 12). Tác giả chịu trách nhiệm về thiết kế và công khai đầy đủ các giới hạn ở trên.
