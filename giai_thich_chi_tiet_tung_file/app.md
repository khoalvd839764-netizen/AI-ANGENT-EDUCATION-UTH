# Giải thích chi tiết: app.py

Đây là **tệp tin giao diện người dùng chính (Main UI)** của toàn bộ hệ thống Agent Education. Nó đóng vai trò kết nối tất cả các logic từ backend để hiển thị lên màn hình.

## 🛠️ Thư viện sử dụng chính:
* `tkinter`: Thư viện GUI có sẵn của Python, gọn nhẹ và dễ sử dụng.
* `PIL` (Pillow): Thư viện xử lý hình ảnh dùng để tải hình ảnh Logo UTH hiển thị lên form đăng ký/đăng nhập.
* `threading`: Thư viện đa luồng (Đa tiến trình).

## ⚙️ Cơ chế hoạt động và Thiết kế:

### 1. Quản lý trạng thái màn hình (Forms Control):
* Khi chạy tệp, lớp `AgentEduApp` sẽ được khởi tạo. Hệ thống sẽ hiển thị màn hình Đăng nhập trước bằng phương thức `_tao_giao_dien_dang_nhap()`.
* Khi học viên đăng ký hoặc đăng nhập thành công, lớp giao diện đăng nhập sẽ bị hủy (`login_frame.destroy()`), và giao diện chat chính sẽ được dựng lên qua `_tao_giao_dien()`.

### 2. Sử dụng Đa luồng (Multi-threading) - Điểm kỹ thuật quan trọng nhất:
* Trong các ứng dụng giao diện (như Tkinter), nếu bạn gọi các hàm mất thời gian dài để xử lý (như đọc file PDF nặng, gửi yêu cầu mạng lên AI để suy nghĩ mất 5-10 giây) trực tiếp trên luồng chính, giao diện ứng dụng sẽ bị **treo cứng (Freeze/Đóng băng)**, người dùng không thể bấm chuột hay di chuyển cửa sổ.
* **Giải pháp trong code:** Tất cả các tác vụ nặng:
  - Khởi tạo backend AI (`_khoi_tao_backend`)
  - Nạp tệp PDF vào ChromaDB (`_xu_ly_upload_file` -> `_nap_file`)
  - Hỏi đáp AI RAG (`_xu_ly_gui_tin_nhan` -> `_hoi_ai`)
  - Tự động phân tích tóm tắt tài liệu (`_xu_ly_phan_tich` -> `_phan_tich`)
  Đều được bọc trong các hàm phụ chạy nền và kích hoạt bằng `threading.Thread(target=..., daemon=True).start()`.
* **Cập nhật giao diện an toàn:** Từ các luồng nền, khi cần cập nhật chữ lên giao diện chính, bắt buộc phải dùng phương thức `self.root.after(0, lambda: ...)` để đẩy yêu cầu cập nhật về cho luồng chính xử lý, tránh xung đột bộ nhớ đồ họa.
