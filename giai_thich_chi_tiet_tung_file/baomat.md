# Giải thích chi tiết: backend/baomat.py

Tệp tin này đảm nhiệm vai trò **xác thực tài khoản người dùng** cho chức năng Đăng ký và Đăng nhập.

## 🛠️ Thư viện sử dụng chính:
* `sqlite3`: Thư viện kết nối cơ sở dữ liệu quan hệ SQLite cục bộ.
* `backend.ketnoi_data`: Module tự viết để lấy đối tượng kết nối cơ sở dữ liệu.

## ⚙️ Cơ chế hoạt động:

### 1. Hàm kiểm tra đăng nhập `kiem_tra_dang_nhap(username, password)`:
* Thực hiện mở kết nối SQLite.
* Thực thi câu lệnh truy vấn tìm tài khoản: `SELECT ho_ten, mat_khau FROM nguoi_dung WHERE ten_dang_nhap = ?`. Dấu chấm hỏi `?` đóng vai trò là tham số hóa câu lệnh giúp chống lỗi bảo mật SQL Injection cực kỳ an toàn.
* Nếu tìm thấy tài khoản, so khớp trực tiếp mật khẩu người dùng nhập vào với mật khẩu trong Database.
* Nếu khớp, trả về trạng thái đăng nhập thành công cùng họ tên thật của người dùng.

### 2. Hàm đăng ký tài khoản `dang_ky_tai_khoan(username, password, fullname)`:
* **Kiểm tra điều kiện hợp lệ dữ liệu nhập (Validation):**
  - Tài khoản, mật khẩu, họ tên không được để trống.
  - Tên tài khoản đăng ký phải dài từ 3 ký tự trở lên.
  - Mật khẩu đăng ký phải dài từ 6 ký tự trở lên để bảo đảm độ an toàn.
* **Kiểm tra trùng lặp:** Thực hiện truy vấn kiểm tra xem tên đăng nhập mong muốn đã tồn tại trong database hay chưa. Nếu đã có người đăng ký tên đó, hệ thống sẽ báo lỗi và dừng tiến trình.
* **Chèn dữ liệu mới:** Thực thi lệnh `INSERT INTO nguoi_dung (ten_dang_nhap, mat_khau, ho_ten) VALUES (?, ?, ?)`.
* **Commit dữ liệu:** Gọi lệnh `conn.commit()` để lưu vĩnh viễn tài khoản mới vào file đĩa cứng.
