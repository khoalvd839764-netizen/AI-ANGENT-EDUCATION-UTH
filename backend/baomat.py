# -*- coding: utf-8 -*-
# =========================================================================
# THƯ MỤC: backend
# TÊN FILE: baomat.py
# CHỨC NĂNG CHÍNH: Xử lý xác thực người dùng (Đăng ký, Đăng nhập).
#                  Sử dụng CSDL SQLite để lưu trữ và quản lý tài khoản học viên.
# =========================================================================

from backend.ketnoi_data import get_connection  # Import hàm kết nối database SQLite
import sqlite3                                  # Thư viện SQLite3 của Python

def kiem_tra_dang_nhap(username, password):
    """
    Hàm xác thực đăng nhập của học viên.
    
    Tham số:
        username (str): Tên đăng nhập người dùng nhập vào.
        password (str): Mật khẩu dạng văn bản thường (plaintext).
        
    Trả về:
        tuple (bool, str, str/None): 
            - Trạng thái thành công (True/False).
            - Thông báo kết quả phản hồi lên giao diện.
            - Họ và tên người dùng (hoặc None nếu thất bại).
    """
    conn = None
    cursor = None
    try:
        # Bước 1: Mở kết nối tới database SQLite
        conn = get_connection()
        cursor = conn.cursor()

        # Bước 2: Thực thi truy vấn SQLite tìm kiếm thông tin tài khoản
        # Sử dụng dấu chấm hỏi '?' để làm tham số hóa câu lệnh, chống lỗi SQL Injection bảo mật
        query = "SELECT ho_ten, mat_khau FROM nguoi_dung WHERE ten_dang_nhap = ?"
        cursor.execute(query, (username,))
        result = cursor.fetchone()  # Lấy bản ghi đầu tiên khớp kết quả

        # Bước 3: So khớp mật khẩu
        if result:
            fullname, db_password = result
            # So sánh mật khẩu khớp trực tiếp (Plaintext)
            if db_password == password:
                return True, "Đăng nhập thành công!", fullname
            else:
                return False, "Mật khẩu không chính xác.", None
        else:
            return False, "Tài khoản không tồn tại.", None

    except sqlite3.Error as e:
        # Bắt các lỗi phát sinh từ cơ sở dữ liệu SQLite
        return False, f"Lỗi cơ sở dữ liệu SQLite: {e}", None
    except Exception as e:
        # Bắt mọi lỗi hệ thống khác (ví dụ: lỗi kết nối, lỗi logic dữ liệu,...)
        return False, f"Lỗi hệ thống: {e}", None
    finally:
        # Bước 4: Giải phóng kết nối và tài nguyên của SQLite
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def dang_ky_tai_khoan(username, password, fullname):
    """
    Hàm đăng ký một tài khoản học viên mới.
    
    Tham số:
        username (str): Tên đăng nhập mong muốn.
        password (str): Mật khẩu mong muốn.
        fullname (str): Họ và tên thật hiển thị.
        
    Trả về:
        tuple (bool, str):
            - Trạng thái thành công (True/False).
            - Thông báo mô tả kết quả cụ thể.
    """
    conn = None
    cursor = None
    try:
        # Bước 1: Ràng buộc tính hợp lệ của dữ liệu đầu vào (Validation)
        if not username or not password or not fullname:
            return False, "Vui lòng điền đầy đủ các trường thông tin."
        
        if len(username) < 3:
            return False, "Tên đăng nhập phải chứa ít nhất 3 ký tự."
        
        if len(password) < 6:
            return False, "Mật khẩu phải chứa ít nhất 6 ký tự."

        # Bước 2: Mở kết nối database SQLite
        conn = get_connection()
        cursor = conn.cursor()

        # Bước 3: Kiểm tra xem tên đăng nhập này đã được sử dụng hay chưa
        check_query = "SELECT id FROM nguoi_dung WHERE ten_dang_nhap = ?"
        cursor.execute(check_query, (username,))
        if cursor.fetchone():
            return False, "Tên đăng nhập đã tồn tại trên hệ thống. Vui lòng chọn tên khác."

        # Bước 4: Thêm dữ liệu tài khoản mới vào bảng 'nguoi_dung'
        insert_query = "INSERT INTO nguoi_dung (ten_dang_nhap, mat_khau, ho_ten) VALUES (?, ?, ?)"
        cursor.execute(insert_query, (username, password, fullname))
        
        # Bước 5: Lưu thay đổi (commit) xuống ổ đĩa cứng
        conn.commit()
        
        return True, "Đăng ký tài khoản mới thành công!"

    except sqlite3.Error as e:
        # Bắt lỗi ghi dữ liệu của SQLite
        return False, f"Lỗi cơ sở dữ liệu SQLite khi đăng ký: {e}"
    except Exception as e:
        # Bắt lỗi logic hệ thống
        return False, f"Lỗi hệ thống khi đăng ký: {e}"
    finally:
        # Bước 6: Đóng tài nguyên cơ sở dữ liệu
        if cursor:
            cursor.close()
        if conn:
            conn.close()
