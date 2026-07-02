# -*- coding: utf-8 -*-
# =========================================================================
# THƯ MỤC: backend
# TÊN FILE: ketnoi_data.py
# CHỨC NĂNG CHÍNH: Quản lý khởi tạo, tạo bảng và cấu trúc kết nối SQLite.
# =========================================================================

import sqlite3  # Thư viện SQLite tích hợp sẵn trong Python
import os       # Thư viện hệ thống thao tác với file
import sys      # Thư viện hệ thống quản lý I/O

# Cấu hình UTF-8 cho stdout/stderr để tránh lỗi hiển thị tiếng Việt trên Windows CMD
if sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if sys.stderr is not None:
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Xác định đường dẫn thư mục gốc và file SQLite db cục bộ
# Lấy đường dẫn của thư mục gốc dự án (thư mục cha của thư mục chứa file này)
THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Cơ sở dữ liệu SQLite được lưu trữ tại: thư mục gốc / database / agent_edu.db
DUONG_DAN_DB = os.path.join(THU_MUC_GOC, "database", "agent_edu.db")

def khoi_tao_database_neu_chua_co():
    """
    Tự động kiểm tra và khởi tạo cấu trúc cơ sở dữ liệu SQLite:
    - Tạo thư mục 'database' chứa tệp tin SQLite nếu chưa tồn tại.
    - Tạo bảng 'nguoi_dung' dùng để quản lý tài khoản đăng nhập.
    - Chèn tài khoản quản trị mặc định ('admin' mật khẩu '123456') nếu bảng trống.
    """
    # Bước 1: Tạo thư mục 'database' nếu nó chưa tồn tại trên đĩa cứng
    os.makedirs(os.path.dirname(DUONG_DAN_DB), exist_ok=True)
    
    conn = None
    cursor = None
    try:
        # Bước 2: Tạo kết nối tới file database SQLite (nếu chưa có file, sqlite3 tự tạo file trống)
        conn = sqlite3.connect(DUONG_DAN_DB)
        cursor = conn.cursor()
        
        # Bước 3: Tạo bảng lưu trữ thông tin học viên 'nguoi_dung'
        # Trong SQLite: 
        # - INTEGER PRIMARY KEY AUTOINCREMENT tự động tăng chỉ mục ID.
        # - Kiểu dữ liệu TEXT dùng thay thế cho VARCHAR.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nguoi_dung (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ten_dang_nhap TEXT NOT NULL UNIQUE,
                mat_khau TEXT NOT NULL,
                ho_ten TEXT NOT NULL,
                ngay_tao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Bước 4: Kiểm tra và nạp tài khoản admin mặc định
        cursor.execute("SELECT id FROM nguoi_dung WHERE ten_dang_nhap = 'admin'")
        if not cursor.fetchone():
            # Nếu chưa có tài khoản admin, chèn tài khoản mặc định
            cursor.execute("""
                INSERT INTO nguoi_dung (ten_dang_nhap, mat_khau, ho_ten)
                VALUES ('admin', '123456', 'Quản trị viên Agent Edu')
            """)
            conn.commit()  # Lưu thay đổi xuống đĩa
            print("[Database] Đã khởi tạo cơ sở dữ liệu SQLite và tài khoản admin mặc định.")
            
    except Exception as e:
        print(f"[Database Error] Lỗi tự động khởi tạo database SQLite: {e}")
    finally:
        # Bước 5: Giải phóng tài nguyên con trỏ và kết nối cơ sở dữ liệu
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_connection():
    """
    Hàm kết xuất đối tượng kết nối SQLite.
    
    Trả về:
        sqlite3.Connection: Đối tượng kết nối trực tiếp đến cơ sở dữ liệu agent_edu.db.
    """
    # Gọi hàm tự khởi tạo cấu trúc dữ liệu trước để tránh lỗi thiếu bảng khi đọc/ghi
    khoi_tao_database_neu_chua_co()
    
    # Kết nối trực tiếp tới tệp tin cơ sở dữ liệu SQLite cục bộ
    return sqlite3.connect(DUONG_DAN_DB)
