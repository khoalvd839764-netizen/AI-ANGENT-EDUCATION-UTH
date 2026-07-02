# Giải thích chi tiết: backend/file_processor.py

Tệp tin này đảm nhiệm vai trò **trích xuất văn bản thô (Plain Text) từ tệp PDF** do học viên tải lên.

## 🛠️ Thư viện sử dụng chính:
* `pdfplumber`: Thư viện Python chuyên dụng để đọc tệp PDF kỹ thuật số. Thư viện này hỗ trợ trích xuất văn bản có cấu trúc tốt hơn PyPDF2 và xử lý tiếng Việt rất chuẩn.
* `os`: Thư viện hệ thống giúp làm việc với tên tệp và đường dẫn file.

## ⚙️ Cơ chế hoạt động của hàm `chuyen_file_pdf_to_text(self, filepath)`:
1. **Kiểm tra định dạng đuôi file:** Sử dụng `os.path.splitext` để lấy định dạng mở rộng của tệp. Nếu tệp không phải đuôi `.pdf` (ví dụ `.docx`, `.txt`), hệ thống sẽ từ chối và trả về chuỗi rỗng.
2. **Khởi tạo chuỗi kết quả:** Khai báo biến `full_text = ""` dùng để cộng dồn chữ.
3. **Duyệt qua từng trang PDF:**
   - Mở tệp PDF bằng `pdfplumber.open(filepath)`.
   - Vòng lặp `for page in pdf.pages` sẽ đi qua tất cả các trang của tài liệu.
   - Gọi phương thức `page.extract_text()` để lấy toàn bộ chữ có trên trang đó.
4. **Cộng dồn văn bản:** Văn bản của từng trang được ghép vào biến `full_text` kèm ký tự xuống dòng `\n` để tránh việc chữ của các trang bị dính liền vào nhau.
5. **Xử lý ngoại lệ (Try-Except):** Toàn bộ quy trình được bọc trong khối try-except. Nếu tệp PDF bị lỗi cấu trúc hoặc bị khóa quyền truy cập, hệ thống sẽ in thông báo lỗi ra màn hình console và trả về chuỗi rỗng thay vì làm sập ứng dụng.
