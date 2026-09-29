# Hồ sơ nộp bài tập cuối khóa

**Khóa học:** Làm chủ kỹ thuật xây dựng Prompt và trợ lý AI (AOTS × HCMUT)
**Sản phẩm:** TaskLens, trợ lý AI phân rã đề bài tập lớn, biết dừng khi thiếu dữ kiện
**Học viên:** Trương Hiển Minh · MSSV: 2452771
**Repository:** https://github.com/truonghienminh-HCMUT/tasklens · **Video demo:** ⟦link⟧ · **Bài LinkedIn:** ⟦link⟧

**Kết quả chính:**

| | V1 | V2 |
|---|---|---|
| gpt-oss-120b | 3/11 | **10/11** |
| Gemma 4 | 3/11 | **8/11** |
| Đề thật (3 ca, cả 2 model) | 0/3 | **3/3** |

Chạy trên 2 model của 2 hãng, chi phí 0 đồng.

| # | Sản phẩm yêu cầu (Buổi 12, slide 41) | Vị trí trong repo |
|---|---|---|
| 1 | Bản mô tả bài toán & vấn đề thực tế | [docs/01-problem-statement.md](docs/01-problem-statement.md) |
| 2 | Bản thiết kế hệ thống 11 thành phần | [docs/system-design.md](docs/system-design.md) · [docs/workflow-diagram.png](docs/workflow-diagram.png) |
| 3 | Cấu hình / mã nguồn Prototype V1 | [instructions/system-prompt-v1.md](instructions/system-prompt-v1.md) · [src/tasklens/pipeline_v1.py](src/tasklens/pipeline_v1.py) |
| 4 | Bộ kiểm thử 10 kịch bản thử lửa (Eval Suite) | [evals/test-cases.csv](evals/test-cases.csv) (10 + 1 ca PII) · [evals/real-cases.csv](evals/real-cases.csv) (3 đề thật) · [evals/graders.py](evals/graders.py) |
| 5 | Bảng kết quả kiểm thử thực tế V1 | [evals/results/](evals/results/) · các file `v1__*.csv` (7 trường theo slide 18) + log thô `raw/v1__*/` |
| 6 | Báo cáo 5-Whys các ca thất bại | [evals/failure-analysis.md](evals/failure-analysis.md) · [evals/results/failure-modes.md](evals/results/failure-modes.md) |
| 7 | Cấu hình / mã nguồn Prototype V2 | [instructions/system-prompt-v2.md](instructions/system-prompt-v2.md) · [src/tasklens/pipeline_v2.py](src/tasklens/pipeline_v2.py) · [sanitize.py](src/tasklens/sanitize.py) · [validate.py](src/tasklens/validate.py) |
| 8 | Bảng đối chiếu định lượng V1 vs V2 | [evals/v1-vs-v2.md](evals/v1-vs-v2.md) · [evals/v1-vs-v2.png](evals/v1-vs-v2.png) · [evals/per-case-heatmap.png](evals/per-case-heatmap.png) |
| 9 | Nhật ký Model Swap Test | [docs/model-swap-log.md](docs/model-swap-log.md) |
| 10 | Hướng dẫn sử dụng, giới hạn, khuyến cáo an toàn | [docs/limitations-safety.md](docs/limitations-safety.md) · [README.md](README.md) |
| 11 | Video demo 3 phút / link trải nghiệm | Kịch bản: [demo/demo-script.md](demo/demo-script.md) · Video: ⟦link⟧ |
| 12 | Case Study chuẩn Portfolio | [docs/case-study.md](docs/case-study.md) (kèm bản LinkedIn) · Bài đăng: ⟦link⟧ |

**Tài liệu bổ trợ:**
- [docs/qa-prep.md](docs/qa-prep.md): trả lời 5 câu phản biện ở slide 34.
- `tests/`: 36 unit test cho bộ chấm, các cổng code và giao diện.
- Toàn bộ nội dung trên đã gộp thành 1 file PDF: `dist/BaoCao_CuoiKhoa_TaskLens.pdf`.

**Lưu ý về dữ liệu:** 2 đề bài thật dùng trong bộ `real-cases` là tài liệu của giảng viên, **không đưa lên repository** (nằm trong `demo/sample-inputs/private/`, bị `.gitignore` chặn). Log thô của bộ này cũng không công khai; repo chỉ có bảng kết quả tóm tắt.
