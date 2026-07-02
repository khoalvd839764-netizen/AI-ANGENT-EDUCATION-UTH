# -*- coding: utf-8 -*-
# =========================================================================
# THƯ MỤC: backend
# TÊN FILE: file_processor.py
# CHỨC NĂNG CHÍNH: Đọc và trích xuất toàn bộ văn bản từ tệp PDF.
# =========================================================================

import pdfplumber  # Thư viện dùng để đọc file PDF có chứa text layer (kỹ thuật số)
import os          # Thư viện hệ thống giúp làm việc với tệp tin và đường dẫn

class FileProcessor:
    """
    Lớp FileProcessor đóng vai trò như một công cụ tiện ích (utility class).
    Lớp này dùng để chuyển đổi các tệp tin PDF do học viên tải lên thành văn bản thô (plain text).
    """
    def __init__(self):
        # Hàm khởi tạo lớp, hiện tại không cần cấu hình tham số đặc biệt nào.
        pass

    def chuyen_file_pdf_to_text(self, filepath):
        """
        Nhiệm vụ: Nhận đường dẫn của tệp tin, kiểm tra định dạng và trích xuất chữ.
        
        Tham số:
            filepath (str): Đường dẫn tuyệt đối hoặc tương đối của tệp PDF cần đọc.
            
        Trả về:
            str: Toàn bộ nội dung văn bản của tệp PDF dưới dạng một chuỗi chuỗi ký tự (string).
                 Trả về chuỗi rỗng nếu có lỗi hoặc file không phải là PDF.
        """
        # Bước 1: Trích xuất phần mở rộng (đuôi file) và chuyển thành chữ thường để kiểm tra
        name, file_type = os.path.splitext(filepath.lower())
        
        # Bước 2: Kiểm tra nếu định dạng tệp tải lên không phải là .pdf
        if file_type != ".pdf":
            print(f"[FileProcessor] Lỗi: Định dạng file '{file_type}' không được hỗ trợ. Chỉ chấp nhận file .pdf")
            return ""
            
        # Bước 3: Đọc file PDF và xử lý lỗi bằng khối try-except để tránh làm crash (sập) hệ thống
        try:
            full_text = ""  # Biến tích lũy chứa toàn bộ văn bản của tất cả các trang
            
            # Mở tệp PDF bằng thư viện pdfplumber
            with pdfplumber.open(filepath) as pdf:
                # Duyệt qua từng trang của tài liệu PDF theo thứ tự
                for page in pdf.pages:
                    # Trích xuất văn bản thô từ trang hiện tại
                    extracted_text = page.extract_text()
                    
                    # Nếu trang hiện tại có văn bản (không phải trang trắng hoặc ảnh scan hoàn toàn)
                    if extracted_text:
                        # Cộng dồn văn bản của trang hiện tại kèm ký tự xuống dòng (\n) để ngăn cách các trang
                        full_text += extracted_text + "\n"
                        
            # Bước 4: Trả về chuỗi văn bản đã tổng hợp hoàn tất
            return full_text
            
        except Exception as e:
            # Ghi nhận lỗi ra màn hình console để phục vụ debug khi có lỗi xảy ra (lỗi quyền đọc file, file hỏng,...)
            print(f"[FileProcessor] Lỗi đọc file PDF '{filepath}':", e)
            return ""  # Trả về chuỗi rỗng để báo hiệu quá trình đọc thất bại