# Giải thích chi tiết: backend/ketnoi_data.py

Tệp tin này quản lý việc **khởi tạo cơ sở dữ liệu SQLite cục bộ** để lưu giữ thông tin tài khoản người dùng trong dự án.

## ⚙️ Cơ chế hoạt động:

### 1. Đường dẫn file database cục bộ:
* SQLite không yêu cầu cài đặt phần mềm máy chủ database phức tạp (như MySQL hay PostgreSQL). Nó chỉ lưu toàn bộ dữ liệu trong một tệp tin duy nhất đặt tại thư mục dự án của bạn: `database/agent_edu.db`.

### 2. Hàm khởi tạo cơ sở dữ liệu `khoi_tao_database_neu_chua_co()`:
* **Tạo thư mục:** Kiểm tra nếu thư mục `database/` chưa tồn tại thì tự động tạo mới bằng lệnh `os.makedirs`.
* **Tạo cấu trúc bảng:**
  - Kết nối tới tệp `agent_edu.db` và tạo bảng `nguoi_dung` nếu chưa có.
  - Bảng này gồm các trường:
    - `id` (INTEGER PRIMARY KEY AUTOINCREMENT): Khóa chính tự động tăng định danh từng tài khoản.
    - `ten_dang_nhap` (TEXT UNIQUE): Tên tài khoản, ràng buộc là duy nhất không được trùng lặp.
    - `mat_khau` (TEXT): Mật khẩu người dùng.
    - `ho_ten` (TEXT): Họ tên thật của người dùng.
    - `ngay_tao` (TIMESTAMP): Tự động ghi nhận thời gian đăng ký.
* **Khởi tạo tài khoản quản trị mặc định:**
  - Thực hiện kiểm tra xem đã có tài khoản tên là `admin` chưa.
  - Nếu chưa có, hệ thống tự động chèn một tài khoản mặc định là `admin` với mật khẩu là `123456` để người dùng có thể đăng nhập thử nghiệm ngay lập tức.

### 3. Hàm lấy đối tượng kết nối `get_connection()`:
* Mỗi khi các module khác cần đọc hoặc ghi cơ sở dữ liệu (ví dụ: đăng nhập, đăng ký), họ sẽ gọi hàm này. Hàm sẽ kiểm tra cấu trúc bảng trước, sau đó trả về đối tượng kết nối SQLite đang mở.
