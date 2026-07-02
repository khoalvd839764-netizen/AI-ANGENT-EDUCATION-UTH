# Giải thích chi tiết: backend/Rag.py

Đây là **phần cốt lõi xử lý tri thức của hệ thống RAG (Retrieval-Augmented Generation)**. File này liên kết các file xử lý văn bản, nhúng vector, lưu trữ CSDL Vector và gửi dữ liệu cho AI.

## 🛠️ Thư viện sử dụng chính:
* `chromadb`: Cơ sở dữ liệu vector gọn nhẹ chạy cục bộ. Dữ liệu được ghi thẳng xuống thư mục `database/chroma_db` trong dự án dưới dạng tệp tin đĩa cứng.
* `ollama`: Dùng để tạo Vector nhúng cho văn bản.

## ⚙️ Cơ chế hoạt động:

### 1. Hàm khởi tạo `__init__(self, ai_model="qwen2.5:3b")`:
* Tạo kết nối đến database ChromaDB cục bộ.
* Lấy hoặc tạo bảng (Collection) tên là `tai_lieu_on_tap` trong database.

### 2. Hàm tạo Vector nhúng `_get_embedding(self, text)`:
* Nhận một chuỗi ký tự và gửi sang mô hình nhúng `nomic-embed-text` của Ollama.
* Nhận về một Vector (mảng chứa 768 số thực biểu diễn ngữ nghĩa của đoạn văn bản đó).

### 3. Thuật toán `_cat_nho_van_ban(self, text, max_chunk_size=600, min_chunk_size=100)`:
* **Semantic Chunking (Cắt theo ngữ nghĩa):**
  - Bước 1: Ưu tiên cắt văn bản thành các đoạn văn thô dựa trên ký tự xuống dòng kép `\n\n` (Ranh giới ngữ nghĩa tự nhiên lớn nhất).
  - Bước 2: Nếu đoạn văn dài quá 600 ký tự (`max_chunk_size`), tiếp tục tách đoạn văn đó thành các câu nhỏ dựa trên dấu câu (`.`, `!`, `?`, `:`).
  - Bước 3: Nếu một câu đơn vẫn dài quá 600 ký tự (trường hợp hiếm), tách câu đó theo từng từ (khoảng trắng).
* **Gộp chunk ngắn:** Nếu đoạn văn bản sau khi cắt quá ngắn (nhỏ hơn 100 ký tự - `min_chunk_size`), hệ thống sẽ gộp nó vào đoạn liền trước. Điều này ngăn việc tạo ra quá nhiều đoạn nhỏ lẻ tẻ thiếu thông tin.

### 4. Hàm nạp file PDF `add_document_to_db(self, filepath)`:
* Gọi file_processor để lấy chữ ➔ Gọi cắt nhỏ văn bản ➔ Gọi tạo vector nhúng cho từng chunk ➔ Thêm toàn bộ văn bản thô, mảng vector nhúng và siêu dữ liệu `source` (tên file) vào ChromaDB.

### 5. Hàm hỏi đáp RAG `ask_with_rag(self, question, filename=None, n_results=5)`:
* **Hóa vector câu hỏi:** Chuyển câu hỏi của người dùng thành mảng vector.
* **Truy tìm tài liệu tương đồng:** Gọi `self.collection.query()` để so sánh khoảng cách Euclid giữa vector câu hỏi và các vector tri thức trong DB. Lấy ra 5 đoạn (`n_results=5`) có khoảng cách ngắn nhất (tương quan ngữ nghĩa nhất).
* **Gọi AI trả lời:** Ghép 5 đoạn văn đó lại thành chuỗi ngữ cảnh (`context`) gửi qua `Model_AI` để hỏi mô hình `qwen2.5:3b`.
