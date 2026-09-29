# 10. Hướng dẫn sử dụng, giới hạn và khuyến cáo an toàn

Tài liệu này dành cho người muốn dùng hoặc chạy lại TaskLens. Nó trả lời bốn câu hỏi bàn giao ở Buổi 12, slide 29: sản phẩm tạo ra giá trị gì và cho ai, đầu vào và đầu ra ra sao, người khác chạy nó thế nào, và có những giới hạn, rủi ro gì cần biết.

## 10.1. TaskLens làm gì, cho ai

TaskLens dành cho sinh viên vừa nhận đề bài tập lớn. Bạn đưa đề vào, TaskLens trả về các yêu cầu, ràng buộc, sản phẩm phải nộp, tiêu chí chấm và hạn nộp, mỗi mục kèm câu trích nguyên văn để bạn tự đối chiếu. Nó cũng chỉ ra những chỗ đề còn thiếu, mơ hồ, mâu thuẫn hoặc phi lý, kèm câu hỏi nên gửi giảng viên. Kế hoạch thực hiện chỉ được lập khi đủ dữ kiện; nếu chưa có hạn nộp hợp lệ, TaskLens sẽ dừng lại và hỏi bạn.

TaskLens không làm bài hộ, không dự đoán điểm, và không tự nộp bài hay gửi email.

## 10.2. Cài đặt và chạy

```bash
pip install -r requirements.txt
cp .env.example .env            # điền GEMINI_API_KEY và/hoặc GROQ_API_KEY (đều có gói miễn phí)
python scripts/check_setup.py   # kiểm tra key và gọi thử model
streamlit run app.py            # mở http://localhost:8501
```

Cách dùng giao diện:

1. Ở thanh bên trái, chọn phiên bản V2 (nên dùng) và chọn model.
2. Tải đề lên (PDF có lớp chữ, DOCX, TXT) hoặc dán nội dung vào.
3. Ghi yêu cầu, ví dụ: "Tôi học lớp CC04. Phân rã đề và lập kế hoạch cho tôi." Nếu đề ghi hạn nộp khác nhau theo lớp, hãy nói rõ bạn học lớp nào.
4. Nếu đề không ghi hạn nộp nhưng bạn đã biết (chẳng hạn giảng viên thông báo trên LMS), hãy điền vào ô "Hạn nộp".
5. Đọc phần "Cần bạn bổ sung / làm rõ" và các ghi chú của hệ thống, ví dụ dữ liệu cá nhân đã được che, trích dẫn bị gỡ, hay tài liệu đã bị rút gọn.
6. Đối chiếu với đề gốc, tick ô "Tôi đã đối chiếu..." rồi mới tải kết quả về (Markdown hoặc JSON).

Hướng dẫn chạy bộ kiểm thử có trong `README.md` và thư mục `evals/`.

## 10.3. Đầu vào và đầu ra

| | Mô tả |
|---|---|
| Đầu vào | Đề bài (PDF có lớp chữ, DOCX, TXT, MD, hoặc văn bản dán vào); yêu cầu của người dùng; hạn nộp đã biết (không bắt buộc) |
| Đầu ra | JSON theo schema cố định trong `src/tasklens/schema.py`, hiển thị thành bảng và xuất được sang Markdown |
| Trạng thái | `OK`: đủ dữ kiện, có kế hoạch. `NEED_INFO`: cần bạn bổ sung, chưa có kế hoạch. `REFUSED`: yêu cầu nằm ngoài phạm vi. `INVALID_INPUT`: không đọc được đề bài |

## 10.4. Dữ liệu của bạn đi đâu

1. Trước khi gửi đi, TaskLens làm sạch văn bản ngay trên máy bạn và che email, số điện thoại, MSSV (dãy 7–10 chữ số), API key và mật khẩu.
2. Đề đã che được gửi tới một nhà cung cấp model do bạn chọn: Google (Gemini API, model Gemma) hoặc Groq (model gpt-oss). Bạn nên đọc điều khoản dữ liệu của họ. Gói miễn phí của một số nhà cung cấp, ví dụ Gemini API, có thể dùng nội dung gửi lên để cải thiện dịch vụ, nên đừng gửi tài liệu mật hoặc tài liệu bạn không có quyền chia sẻ.
3. File `logs/audit.jsonl` chỉ ghi thông tin mô tả: thời điểm, model, trạng thái, số token, độ dài và mã băm của đề. Nội dung đề và câu trả lời không được lưu.
4. API key nằm trong file `.env`. File này đã bị `.gitignore` chặn nên không bao giờ bị đưa lên GitHub.

## 10.5. Giới hạn đã biết

Các giới hạn dưới đây đều có bằng chứng trong repo.

| # | Giới hạn | Bằng chứng | Điều người dùng nên biết |
|---|---|---|---|
| 1 | Cổng từ chối dựa trên từ khóa, nên có thể bị lách nếu diễn đạt khác đi (ví dụ "làm giúp mình phần backend"). Lớp thứ hai là quy tắc trong prompt, nhưng model vẫn có thể làm theo | `sanitize.classify_request`; TC06 và TC07 mới chỉ thử một cách diễn đạt | Đừng dùng TaskLens như một cơ chế chống gian lận |
| 2 | Bộ phát hiện injection dựa trên mẫu câu. Một câu ra lệnh khéo léo, không dùng các cụm quen thuộc, có thể lọt qua. Cổng kiểm tra đầu ra chỉ gỡ được mã hoặc chuỗi mà câu đáng ngờ chỉ định rõ | `sanitize.find_injections`; TC08 | Khi hệ thống báo có đoạn văn đáng ngờ, hãy đọc kỹ đoạn đó trong đề gốc |
| 3 | Bước rút gọn ngữ cảnh có thể bỏ sót. Tài liệu vượt ngân sách của model (với gói miễn phí: Groq 8.000 ký tự, Gemma 36.000 ký tự) được lọc theo từ khóa, nên yêu cầu nằm ở đoạn không chứa từ khóa có thể bị lược đi | TC09 ở V2: hạn nộp tìm đúng, nhưng gpt-oss chỉ liệt kê 2/3 sản phẩm nộp, còn Gemma 2/3 lượt báo "thiếu nội dung đề tài" vì mục "Yêu cầu chức năng" bị lược | Hệ thống luôn báo khi đã rút gọn. Khi đó hãy tự đọc phần bị lược; với tài liệu dài, nên dán riêng phần đề bài |
| 4 | Bước kiểm tra trích dẫn chỉ xác nhận câu đó có trong đề, không xác nhận AI hiểu đúng câu đó | `validate.is_grounded` | Vẫn phải đọc phần nội dung và đối chiếu. Đây là lý do có bước Human checkpoint |
| 5 | PDF scan (ảnh), bảng biểu phức tạp và sơ đồ không đọc được, vì hệ thống chỉ dùng lớp chữ của PDF (Buổi 4 gọi đây là "điểm mù PDF quét") | TC10; `io_utils` | Hệ thống sẽ trả `INVALID_INPUT`. Hãy dán văn bản, hoặc chạy OCR trước |
| 6 | Việc che dữ liệu cá nhân dựa trên mẫu: tên người không được che, và dãy 7–10 chữ số bất kỳ đều bị coi là MSSV (có thể che nhầm số khác) | `sanitize.mask_pii`; TC11 | Đừng đưa danh sách thông tin cá nhân không cần thiết vào đề |
| 7 | Kết quả có thể khác nhau giữa các lần chạy, dù cùng đề và cùng model | Cột "Runs Pass" trong `evals/results/*.csv` | Chạy lại nếu thấy thiếu, và luôn đối chiếu với đề gốc |
| 8 | Hệ thống phụ thuộc vào gói miễn phí: có quota theo ngày và theo phút, model có thể bị gỡ hoặc quá tải (lỗi 404, 429, 500, 503) | `docs/model-swap-log.md` | Có thể phải chờ hoặc đổi model; logic không thay đổi |
| 9 | Chỉ nhận ngày viết dạng số hoặc dạng tiếng Anh, tiếng Việt thông dụng. Cách viết lạ như "thứ Sáu tuần 15" sẽ không được hiểu là hạn nộp | `validate.dates_in` | Nếu hệ thống không nhận ra, hãy điền hạn nộp vào ô riêng |
| 10 | Bộ kiểm thử có giới hạn: 11 ca tổng hợp và 3 ca đề thật, và gpt-oss chỉ chạy 1 lần/ca do quota | `evals/` | Kết quả là bằng chứng trong một phạm vi nhất định, không phải bảo đảm tuyệt đối |

## 10.6. Khuyến cáo khi sử dụng

1. Đề gốc và thông báo của giảng viên luôn là căn cứ cuối cùng. TaskLens giúp bạn đọc đề, không đọc thay bạn.
2. Nếu môn học yêu cầu, hãy khai báo việc dùng AI. Ví dụ, đề Công nghệ phần mềm HK261 bắt buộc khai báo công cụ, phạm vi và mức đóng góp của AI.
3. Không dùng TaskLens để hỏi điểm, khiếu nại điểm, hay cho bất kỳ quyết định nào thuộc thẩm quyền giảng viên.
4. Không tải lên tài liệu mật, tài liệu nội bộ, hay thông tin cá nhân của người khác.
5. Khi TaskLens trả `NEED_INFO`, đừng tự đoán rồi ép hệ thống lập kế hoạch. Hãy hỏi giảng viên.

## 10.7. Trách nhiệm

Mọi quyết định cuối cùng (làm gì, nộp gì, nộp khi nào) thuộc về người dùng. TaskLens không có tư cách pháp lý nên không thể chịu trách nhiệm thay ai (Buổi 12, slide 12). Tôi, với tư cách người làm ra sản phẩm, chịu trách nhiệm về thiết kế và về việc công khai đầy đủ các giới hạn ở trên.
