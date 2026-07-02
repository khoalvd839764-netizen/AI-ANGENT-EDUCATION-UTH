# Giải thích chi tiết: backend/Model_ai.py

Tệp tin này chịu trách nhiệm **kết nối, kiểm tra và gửi yêu cầu sinh câu trả lời** đến mô hình ngôn ngữ lớn (LLM) cục bộ chạy trên ứng dụng Ollama.

## 🛠️ Thư viện sử dụng chính:
* `ollama`: Thư viện chính thức của hãng để giao tiếp với dịch vụ AI chạy trên cổng mạng `11434` của máy tính.

## ⚙️ Cơ chế hoạt động:

### 1. Hàm khởi tạo `__init__(self, ai_model="qwen2.5:3b")`:
* Lưu tên mô hình chính dùng để chat (mặc định là `qwen2.5:3b`).
* Gọi hàm `check_and_pull_model` cho hai mô hình:
  - Mô hình chat: `qwen2.5:3b`.
  - Mô hình nhúng vector: `nomic-embed-text` (mô hình này bắt buộc phải có để hệ thống RAG hoạt động).
* Nếu cả 2 mô hình đã sẵn sàng, gán cờ trạng thái `self.status_ai = True`.

### 2. Hàm kiểm tra và tự động tải mô hình `check_and_pull_model(self, model_name)`:
* Gọi lệnh `ollama.list()` để xem danh sách các mô hình đã tải về máy bạn.
* Nếu chưa có mô hình cần thiết, gọi lệnh `ollama.pull(model_name)` để tự động tải về từ thư viện của Ollama qua internet.

### 3. Hàm gọi AI trả lời `ai_reply(self, prompt, context="")`:
* **System Prompt:** Thiết lập một chỉ thị hệ thống cố định (`prompt_system`) định hình AI là "Trợ lý Ôn tập & Học tập AI chuyên nghiệp", bắt buộc AI trả lời ngắn gọn, trung thực, bằng tiếng Việt và bám sát tài liệu.
* **Đóng gói tham số:**
  - Nếu có truyền kèm ngữ cảnh (`context` trích xuất từ ChromaDB): Đóng gói câu hỏi và ngữ cảnh theo định dạng: `Ngữ cảnh tài liệu tham khảo: ... Câu hỏi: ...`.
  - Nếu không có ngữ cảnh (chat tự do): Gửi trực tiếp câu hỏi người dùng.
* **Gọi Ollama Chat:** Gọi lệnh `ollama.chat` với các tham số điều chỉnh:
  - `temperature = 0.2`: Nhiệt độ thấp giúp AI phản hồi chính xác thông tin tài liệu, hạn chế việc AI tự sáng tạo hay nói nhảm.
  - `top_p = 0.7`: Giới hạn phân phối từ ngữ để kiểm soát độ tập trung cao.
* **Xử lý lỗi kết nối:** Nếu dịch vụ Ollama đột ngột bị tắt trong lúc sinh câu trả lời, khối ngoại lệ sẽ bắt lỗi và trả về câu thông báo lỗi mặc định an toàn.
