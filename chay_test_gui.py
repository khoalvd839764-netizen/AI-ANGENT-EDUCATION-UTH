# -*- coding: utf-8 -*-
# =========================================================================
# TÊN FILE: chay_test_gui.py
# CHỨC NĂNG CHÍNH: Trình chạy kiểm thử giao diện đồ họa (GUI Test Runner).
#                  Tự động kiểm tra độ ổn định và đo lường độ trùng khớp 
#                  ngữ nghĩa câu trả lời AI bằng Tkinter.
# =========================================================================

import tkinter as tk                 # Thư viện thiết kế giao diện đồ họa GUI chuẩn của Python
from tkinter import ttk, messagebox  # Các widget nâng cao và hộp thoại thông báo
import threading                    # Sử dụng đa tiến trình (threading) để tránh bị đơ giao diện khi AI đang chạy test
import os                           # Thao tác hệ thống tệp tin
import sys                          # Hệ thống nhập xuất chuẩn
import socket                       # Kiểm tra trạng thái kết nối cổng mạng cục bộ
from unittest.mock import patch, MagicMock  # Các công cụ giả lập kiểm thử offline
import ollama                       # Thư viện giao tiếp nhúng vector của AI cục bộ

# Cấu hình mã hóa đầu ra UTF-8 cho terminal để hiển thị tiếng Việt trên Windows console
if sys.stdout is not None:
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

# Đưa thư mục gốc dự án vào danh sách tìm kiếm hệ thống để import Model_AI
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.Model_ai import Model_AI

def is_ollama_running():
    """
    Kiểm tra dịch vụ Ollama có hoạt động cục bộ hay không.
    Thử nghiệm kết nối tới cổng mặc định 11434.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect(('localhost', 11434))
        s.close()
        return True
    except Exception:
        return False

def tinh_cosine_similarity(vec1, vec2):
    """
    Tính độ tương đồng Cosine giữa hai vector đặc trưng.
    Độ tương đồng dao động từ [-1, 1], trong đó giá trị càng gần 1 tức hai đoạn văn bản càng giống nhau về mặt ngữ nghĩa.
    """
    if not vec1 or not vec2:
        return 0.0
    dot_product = sum(x * y for x, y in zip(vec1, vec2))
    norm1 = sum(x * x for x in vec1) ** 0.5
    norm2 = sum(x * x for x in vec2) ** 0.5
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)

# =========================================================================
# LỚP GIAO DIỆN KIỂM THỬ ĐỒ HỌA (GUI TEST RUNNER)
# =========================================================================
class GUITestRunner:
    def __init__(self, root):
        self.root = root
        self.root.title("Agent Edu - Đánh Giá Độ Khớp Câu Trả Lời AI (Data Science Book)")
        self.root.geometry("980x750")
        self.root.configure(bg="#1e1e2e")  # Thiết lập màu nền tối hiện đại (Catppuccin Mocha Style)
        self.root.minsize(850, 600)

        # Cấu hình biến kiểm soát luồng chạy test
        self.dang_chay = False
        self.embed_model = "nomic-embed-text"  # Model nhúng vector tính độ khớp Cosine

        # Danh sách 12 test cases: 2 Mock và 10 RAG thực tế dựa trên sách Data Science bằng tiếng Việt
        self.test_cases = [
            {
                "id": 1,
                "name": "1. Kiểm thử Mock: Xử lý ngoại lệ (Exception)",
                "desc": "Mô phỏng lỗi kết nối Ollama để đảm bảo hệ thống không bị sập nguồn ứng dụng.",
                "context": "N/A",
                "question": "Chào bạn (khi mất kết nối)",
                "expected": "Trả về thông báo lỗi mặc định: 'Xin lỗi, tôi không thể xử lý yêu cầu này lúc này.'",
                "status": "WAITING", "actual": "", "percent": None
            },
            {
                "id": 2,
                "name": "2. Kiểm thử Mock: Truyền kèm Ngữ cảnh (Context)",
                "desc": "Mô phỏng gộp tài liệu RAG vào prompt để kiểm tra cấu trúc gửi đi.",
                "context": "Tài liệu này nói về Lập trình Python.",
                "question": "Python là gì?",
                "expected": "Prompt gửi lên AI phải chứa tiêu đề 'Ngữ cảnh tài liệu tham khảo:'.",
                "status": "WAITING", "actual": "", "percent": None
            },
            {
                "id": 3,
                "name": "3. Kiểm thử AI RAG: Câu 1 - Công cụ lập trình chính",
                "desc": "Đánh giá ngôn ngữ lập trình chính được cuốn sách sử dụng.",
                "context": "The book uses Python as a tool to implement and exploit some of the most common algorithms used in data science and data analytics today.",
                "question": "Ngôn ngữ lập trình nào được sử dụng làm công cụ chính trong sách này để triển khai các thuật toán khoa học dữ liệu?",
                "expected": "Ngôn ngữ lập trình Python được sử dụng làm công cụ chính trong sách này để triển khai và khai thác các thuật toán khoa học dữ liệu.",
                "status": "WAITING", "actual": "", "percent": None
            },
            {
                "id": 4,
                "name": "4. Kiểm thử AI RAG: Câu 2 - iPython/Jupyter Notebook",
                "desc": "Định nghĩa iPython/Jupyter Notebook theo tác giả.",
                "context": "iPython/Jupyter Notebook is a flexible web-based computational environment that combines code, text, mathematics and plots in a single document.",
                "question": "iPython hoặc Jupyter Notebook là gì theo cuốn sách?",
                "expected": "Jupyter Notebook/iPython là một môi trường tính toán linh hoạt trên nền web kết hợp mã nguồn, văn bản, toán học và biểu đồ trong cùng một tài liệu.",
                "status": "WAITING", "actual": "", "percent": None
            },
            {
                "id": 5,
                "name": "5. Kiểm thử AI RAG: Câu 3 - Phiên bản thư viện",
                "desc": "Kiểm tra phiên bản của Pandas và Scikit-learn đã được dùng để test.",
                "context": "The examples contained in this volume have been tested in Python 3.5... and packages used: Python-3.5.2, Pandas-0.19.1, NumPy-1.11.2, Scikit-learn-0.18, StatsModels-0.6.1",
                "question": "Liệt kê phiên bản các thư viện Pandas và Scikit-learn đã được sử dụng để kiểm thử các ví dụ trong sách.",
                "expected": "Các ví dụ được chạy kiểm thử với Pandas phiên bản 0.19.1 và Scikit-learn phiên bản 0.18.",
                "status": "WAITING", "actual": "", "percent": None
            },
            {
                "id": 6,
                "name": "6. Kiểm thử AI RAG: Câu 4 - Bản phân phối Python",
                "desc": "Xác định bản phân phối Python được tác giả khuyến nghị sử dụng.",
                "context": "In particular I have chosen to use the Anaconda Python distribution provided by Continuum Analytics as it offers installations in all of the three computer systems... and offers a rich ecosystem of libraries",
                "question": "Tác giả đã chọn bản phân phối Python nào cho cuốn sách này và bên nào cung cấp nó?",
                "expected": "Tác giả đã chọn bản phân phối Anaconda Python do Continuum Analytics cung cấp.",
                "status": "WAITING", "actual": "", "percent": None
            },
            {
                "id": 7,
                "name": "7. Kiểm thử AI RAG: Câu 5 - Quy trình Data Science",
                "desc": "Liệt kê các bước chính trong quy trình Data Science.",
                "context": "From Data to Insight: the Data Science Workflow: 1.4.1 Identify the Question, 1.4.2 Acquire Data, 1.4.3 Data Munging, 1.4.4 Modelling and Evaluation, 1.4.5 Representation and Interaction, 1.4.6 Data Science: an Iterative Process",
                "question": "Các bước chính trong quy trình khoa học dữ liệu (Data Science workflow) được mô tả trong Chương 1 là gì?",
                "expected": "Quy trình khoa học dữ liệu gồm các bước: Xác định câu hỏi, Thu thập dữ liệu, Làm sạch dữ liệu (Data Munging), Xây dựng mô hình & Đánh giá, Trực quan hóa & Tương tác.",
                "status": "WAITING", "actual": "", "percent": None
            },
            {
                "id": 8,
                "name": "8. Kiểm thử AI RAG: Câu 6 - Ưu điểm của Python",
                "desc": "Lý do Python được chọn làm công cụ chính trong khoa học dữ liệu.",
                "context": "Python is a popular and versatile scripting and object-oriented language, it is easy to use and has a large active community of developers and enthusiasts",
                "question": "Theo lời mở đầu, tại sao Python lại là một công cụ phù hợp cho khoa học dữ liệu?",
                "expected": "Python phù hợp vì nó là ngôn ngữ lập trình hướng đối tượng và kịch bản phổ biến, linh hoạt, dễ sử dụng và có cộng đồng lập trình viên năng động.",
                "status": "WAITING", "actual": "", "percent": None
            },
            {
                "id": 9,
                "name": "9. Kiểm thử AI RAG: Câu 7 - Mục tiêu cuốn sách",
                "desc": "Xác định mục tiêu cốt lõi của tác phẩm.",
                "context": "The main purpose of the book is to present the reader with some of the main concepts used in data science and analytics using tools developed in Python such as Scikit-learn, Pandas, Numpy and others.",
                "question": "Mục đích chính của cuốn sách Data Science and Analytics with Python là gì?",
                "expected": "Mục đích chính của cuốn sách là trình bày các khái niệm cốt lõi trong khoa học dữ liệu bằng cách sử dụng các công cụ Python như Scikit-learn, Pandas, và NumPy.",
                "status": "WAITING", "actual": "", "percent": None
            },
            {
                "id": 10,
                "name": "10. Kiểm thử AI RAG: Câu 8 - Đối tượng độc giả",
                "desc": "Đánh giá độc giả mà cuốn sách hướng tới.",
                "context": "The book is intended to be a companion to data analysts and budding data scientists that have some working experience with both programming and statistical modelling, but who have not necessarily delved into the wonders of data analytics and machine learning.",
                "question": "Độc giả mục tiêu của cuốn sách này là những ai?",
                "expected": "Độc giả mục tiêu là các nhà phân tích dữ liệu và nhà khoa học dữ liệu mới vào nghề đã có kinh nghiệm lập trình và mô hình hóa thống kê nhưng chưa nghiên cứu sâu về học máy.",
                "status": "WAITING", "actual": "", "percent": None
            },
            {
                "id": 11,
                "name": "11. Kiểm thử AI RAG: Câu 9 - Vai trò Gom cụm & Phân lớp",
                "desc": "Phân tích mối quan hệ giữa phân nhóm không giám sát và phân lớp giám sát.",
                "context": "In Chapter 5 we talk about clustering techniques, whereas Chapter 6 covers classification algorithms. These two chapters are central to the data science workflow: Clustering enables us to assign labels to our data in an unsupervised manner; in turn we can use these labels as targets in a classification algorithm.",
                "question": "Giải thích vai trò và mối quan hệ giữa Chương 5 (Phân cụm) và Chương 6 (Phân lớp) trong quy trình xử lý dữ liệu.",
                "expected": "Phân cụm (Chương 5) giúp gán nhãn cho dữ liệu chưa được gắn nhãn (không giám sát), sau đó các nhãn này được dùng làm mục tiêu đầu vào cho thuật toán phân lớp (Chương 6 - có giám sát).",
                "status": "WAITING", "actual": "", "percent": None
            },
            {
                "id": 12,
                "name": "12. Kiểm thử AI RAG: Câu 10 - Môi trường thử nghiệm",
                "desc": "Các hệ điều hành được dùng để kiểm thử mã nguồn ví dụ.",
                "context": "The examples contained in this volume have been tested in Python 3.5 under MacOS, Linux and Windows 7, and the code can be run with minimal changes in a Python 2 distribution.",
                "question": "Các ví dụ trong cuốn sách này đã được chạy kiểm thử trên các hệ điều hành và phiên bản Python nào?",
                "expected": "Các ví dụ đã được chạy kiểm thử trên Python 3.5 dưới các hệ điều hành MacOS, Linux và Windows 7.",
                "status": "WAITING", "actual": "", "percent": None
            }
        ]

        # Khởi tạo vẽ giao diện GUI
        self._tao_giao_dien()

    def _tao_giao_dien(self):
        """Thiết kế khung giao diện chính"""
        # ---------- TIÊU ĐỀ HỆ THỐNG ----------
        header_frame = tk.Frame(self.root, bg="#313244", height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        # Nhãn tiêu đề chính của GUI
        tk.Label(
            header_frame,
            text="🎓 Trình Đánh Giá Độ Khớp Câu Trả Lời AI (Data Science Book)",
            font=("Segoe UI", 15, "bold"),
            fg="#89b4fa", bg="#313244"
        ).pack(side="left", padx=20, pady=18)

        # Trạng thái kết nối dịch vụ AI cục bộ (Ollama)
        self.lbl_ollama_status = tk.Label(
            header_frame,
            text="Đang kiểm tra kết nối AI...",
            font=("Segoe UI", 10, "italic"),
            fg="#f9e2af", bg="#313244"
        )
        self.lbl_ollama_status.pack(side="right", padx=20, pady=22)
        # Thực hiện cập nhật trạng thái kết nối ban đầu
        self._cap_nhat_ollama_status()

        # ---------- PHẦN THÔNG TIN ĐIỀU KHIỂN & TỔNG KẾT ----------
        control_frame = tk.Frame(self.root, bg="#1e1e2e", height=60)
        control_frame.pack(fill="x", padx=15, pady=10)

        # Nút kích hoạt tiến trình test
        self.btn_start = tk.Button(
            control_frame,
            text="▶ Chạy 12 bài test đánh giá",
            font=("Segoe UI", 11, "bold"),
            fg="#1e1e2e", bg="#a6e3a1",
            activebackground="#94e2d5",
            cursor="hand2", relief="flat",
            padx=15, pady=6,
            command=self._bat_dau_kiem_thu
        )
        self.btn_start.pack(side="left", pady=10)

        # Nhãn tóm tắt kết quả theo thời gian thực
        self.lbl_summary = tk.Label(
            control_frame,
            text="Trạng thái: Sẵn sàng... | Đạt: 0/12",
            font=("Segoe UI", 11, "bold"),
            fg="#cdd6f4", bg="#1e1e2e"
        )
        self.lbl_summary.pack(side="right", pady=12)

        # ---------- KHU VỰC HIỂN THỊ DANH SÁCH BÀI TEST (Cuộn được) ----------
        main_frame = tk.Frame(self.root, bg="#1e1e2e")
        main_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Canvas và thanh cuộn dọc phục vụ hiển thị danh sách nhiều thẻ kiểm thử
        self.canvas = tk.Canvas(main_frame, bg="#1e1e2e", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        
        # Khung chứa các thẻ kiểm thử nằm lồng bên trong Canvas cuộn
        self.scrollable_frame = tk.Frame(self.canvas, bg="#1e1e2e")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Tự động thay đổi kích thước khung chứa cho vừa vặn chiều ngang của Canvas
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_frame, width=e.width))

        # Dictionary lưu liên kết các phần tử thẻ (Card UI)
        self.test_cards = {}
        # Vẽ cấu trúc các thẻ test
        self._ve_cac_the_kiem_thu()

    def _cap_nhat_ollama_status(self):
        """Cập nhật trạng thái hiển thị của cổng kết nối Ollama trên GUI"""
        if is_ollama_running():
            self.lbl_ollama_status.config(text="✅ Dịch vụ Ollama: Sẵn sàng (Port 11434)", fg="#a6e3a1")
        else:
            self.lbl_ollama_status.config(text="⚠️ Dịch vụ Ollama: Chưa bật (Bài test thực tế sẽ skip)", fg="#f9e2af")

    def _ve_cac_the_kiem_thu(self):
        """Vẽ lại toàn bộ giao diện danh sách thẻ bài test ban đầu"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.test_cards.clear()

        # Vẽ từng thẻ test case
        for test in self.test_cases:
            card = tk.Frame(
                self.scrollable_frame, 
                bg="#181825", 
                padx=15, pady=12,
                highlightbackground="#313244",
                highlightthickness=1
            )
            card.pack(fill="x", pady=5, padx=5)

            # Dòng đầu của thẻ (Tên test + nhãn Trạng thái)
            header_line = tk.Frame(card, bg="#181825")
            header_line.pack(fill="x")

            lbl_name = tk.Label(
                header_line,
                text=test["name"],
                font=("Segoe UI", 11, "bold"),
                fg="#cdd6f4", bg="#181825"
            )
            lbl_name.pack(side="left")

            status_text, status_color = self._get_status_style(test["status"], test.get("percent"))
            lbl_status = tk.Label(
                header_line,
                text=status_text,
                font=("Segoe UI", 10, "bold"),
                fg=status_color, bg="#313244",
                padx=8, pady=2
            )
            lbl_status.pack(side="right")

            # Nhãn mô tả kiểm thử
            lbl_desc = tk.Label(
                card,
                text=test["desc"],
                font=("Segoe UI", 9, "italic"),
                fg="#a6adc8", bg="#181825",
                anchor="w", justify="left"
            )
            lbl_desc.pack(fill="x", pady=(2, 6))

            # Dòng Ngữ cảnh tham khảo
            line_c = tk.Frame(card, bg="#181825")
            line_c.pack(fill="x", pady=1)
            tk.Label(line_c, text="📖 Ngữ cảnh:", font=("Segoe UI", 10, "bold"), fg="#cba6f7", bg="#181825").pack(side="left")
            tk.Label(line_c, text=test["context"], font=("Segoe UI", 10), fg="#a6adc8", bg="#181825", wraplength=700, justify="left").pack(side="left", padx=5)

            # Dòng Câu hỏi
            line_q = tk.Frame(card, bg="#181825")
            line_q.pack(fill="x", pady=1)
            tk.Label(line_q, text="❓ Câu hỏi:", font=("Segoe UI", 10, "bold"), fg="#89b4fa", bg="#181825").pack(side="left")
            tk.Label(line_q, text=test["question"], font=("Segoe UI", 10), fg="#cdd6f4", bg="#181825").pack(side="left", padx=5)

            # Dòng Đáp án mẫu kỳ vọng
            line_e = tk.Frame(card, bg="#181825")
            line_e.pack(fill="x", pady=1)
            tk.Label(line_e, text="🎯 Đáp án mẫu:", font=("Segoe UI", 10, "bold"), fg="#f9e2af", bg="#181825").pack(side="left")
            tk.Label(line_e, text=test["expected"], font=("Segoe UI", 10), fg="#cdd6f4", bg="#181825", wraplength=700, justify="left").pack(side="left", padx=5)

            # Khung chứa kết quả trả về thực tế từ AI
            actual_frame = tk.Frame(card, bg="#181825")
            
            lbl_actual_title = tk.Label(actual_frame, text="🤖 AI Trả lời thực tế:", font=("Segoe UI", 10, "bold"), fg="#a6e3a1", bg="#181825")
            lbl_actual_title.pack(side="left", anchor="nw")
            
            lbl_actual_content = tk.Label(
                actual_frame,
                text=test["actual"] if test["actual"] else "(Chưa chạy)",
                font=("Segoe UI", 10, "italic" if not test["actual"] else "normal"),
                fg="#a6adc8" if not test["actual"] else "#cdd6f4",
                bg="#11111b", padx=8, pady=6,
                wraplength=700, justify="left", anchor="w"
            )
            lbl_actual_content.pack(fill="x", expand=True, padx=5)
            
            # Lưu trữ tham chiếu các Widget để thay đổi giao diện động
            self.test_cards[test["id"]] = {
                "card": card,
                "status": lbl_status,
                "actual_frame": actual_frame,
                "actual_content": lbl_actual_content
            }

            actual_frame.pack(fill="x", pady=(6, 2))

    def _get_status_style(self, status, percent=None):
        """Thiết lập màu sắc và trạng thái hiển thị cho nhãn Test Status"""
        if status == "WAITING":
            return "⏳ ĐANG CHỜ", "#9399b2"
        elif status == "RUNNING":
            return "⚙️ ĐANG CHẠY", "#89b4fa"
        elif status == "PASSED":
            if percent is not None:
                return f"✓ ĐẠT (Khớp {percent:.1f}%)", "#a6e3a1"
            return "✓ ĐẠT KỲ VỌNG", "#a6e3a1"
        elif status == "FAILED":
            if percent is not None:
                return f"✗ THẤT BẠI (Khớp {percent:.1f}%)", "#f38ba8"
            return "✗ THẤT BẠI", "#f38ba8"
        elif status == "SKIPPED":
            return "⚠ BỎ QUA", "#f9e2af"
        return status, "#cdd6f4"

    def _cap_nhat_the_test(self, test_id, status, actual_reply="", percent=None, details=""):
        """Cập nhật giao diện của một thẻ kiểm thử cụ thể khi có kết quả"""
        # Cập nhật thông số trong dữ liệu nguồn
        for t in self.test_cases:
            if t["id"] == test_id:
                t["status"] = status
                t["actual"] = actual_reply
                t["percent"] = percent
                break

        # Cập nhật đồ họa Widget tương ứng
        card_refs = self.test_cards.get(test_id)
        if card_refs:
            status_text, status_color = self._get_status_style(status, percent)
            card_refs["status"].config(text=status_text, fg=status_color)
            
            if actual_reply:
                card_refs["actual_content"].config(
                    text=actual_reply, 
                    fg="#cdd6f4", 
                    font=("Segoe UI", 10)
                )
            else:
                card_refs["actual_content"].config(
                    text="(Đang xử lý...)", 
                    fg="#89b4fa",
                    font=("Segoe UI", 10, "italic")
                )
            
            # Cập nhật màu viền thẻ tương ứng để biểu thị nhanh kết quả (Xanh: Đạt, Đỏ: Thất bại)
            border_color = "#313244"
            if status == "PASSED":
                border_color = "#a6e3a1"
            elif status == "FAILED":
                border_color = "#f38ba8"
            elif status == "SKIPPED":
                border_color = "#f9e2af"
            elif status == "RUNNING":
                border_color = "#89b4fa"
                
            card_refs["card"].config(highlightbackground=border_color)

        self.root.update_idletasks()

    def _bat_dau_kiem_thu(self):
        """Kích hoạt tiến trình chạy test"""
        if self.dang_chay:
            return
        
        self.dang_chay = True
        self.btn_start.config(state="disabled", text="⏳ Đang test...", bg="#45475a")
        self._cap_nhat_ollama_status()

        # Đặt lại toàn bộ giao diện bài test về trạng thái chờ
        for test in self.test_cases:
            self._cap_nhat_the_test(test["id"], "WAITING", actual_reply="", percent=None)
        
        self.lbl_summary.config(text="Bắt đầu chạy...", fg="#89b4fa")

        # Khởi chạy một tiến trình con (Thread) riêng biệt để chạy AI, ngăn việc đơ ứng dụng Tkinter chính
        thread = threading.Thread(target=self._chay_tiến_trình_test_nền, daemon=True)
        thread.start()

    def _chay_tiến_trình_test_nền(self):
        """Luồng con xử lý kiểm thử tuần tự 12 trường hợp"""
        passed_count = 0
        total_count = len(self.test_cases)
        
        import time
        start_time = time.time()       # Ghi nhận thời gian bắt đầu test
        similarity_scores = []         # Lưu điểm số Cosine thu thập được từ các câu RAG thực tế

        try:
            # =================================================================
            # TEST CASE 1: Mock Exception (Offline)
            # =================================================================
            self.root.after(0, lambda: self._cap_nhat_the_test(1, "RUNNING"))
            status, reply, err = self._exec_test_exception()
            self.root.after(0, lambda: self._cap_nhat_the_test(1, status, reply, percent=None, details=err))
            if status == "PASSED": passed_count += 1
            self._update_progress_label(1, passed_count)

            # =================================================================
            # TEST CASE 2: Mock Context (Offline)
            # =================================================================
            self.root.after(0, lambda: self._cap_nhat_the_test(2, "RUNNING"))
            status, reply, err = self._exec_test_context()
            self.root.after(0, lambda: self._cap_nhat_the_test(2, status, reply, percent=None, details=err))
            if status == "PASSED": passed_count += 1
            self._update_progress_label(2, passed_count)

            # Kiểm tra trạng thái hoạt động của cổng Ollama trước khi kích hoạt 10 câu RAG thực tế
            ollama_ready = is_ollama_running()

            # =================================================================
            # TEST CASES 3 đến 12: 10 kịch bản AI RAG thực tế chấm điểm Cosine
            # =================================================================
            for idx in range(3, 13):
                test_id = idx
                case_id = idx - 2  # Chỉ số bài test thực tế từ 1 đến 10
                
                self.root.after(0, lambda t_id=test_id: self._cap_nhat_the_test(t_id, "RUNNING"))
                
                if not ollama_ready:
                    status, reply, percent, err = "SKIPPED", "Bỏ qua vì dịch vụ Ollama cục bộ chưa bật.", None, ""
                else:
                    status, reply, percent, err = self._exec_test_rag_real(case_id)
                    if percent is not None:
                        # Tích lũy điểm để tính toán chỉ số thống kê cuối cùng
                        similarity_scores.append(percent)
                    
                self.root.after(0, lambda t_id=test_id, st=status, rep=reply, pct=percent, dts=err: 
                                self._cap_nhat_the_test(t_id, st, rep, pct, dts))
                
                if status == "PASSED": 
                    passed_count += 1
                self._update_progress_label(test_id, passed_count)

            # Hoàn tất tiến trình chạy kiểm thử và gọi giao diện tổng hợp
            elapsed_time = time.time() - start_time
            self.root.after(0, lambda: self._hoan_thanh_tiến_trình_test(passed_count, total_count, elapsed_time, similarity_scores))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Lỗi kiểm thử", f"Có lỗi xảy ra: {e}"))
            self.root.after(0, lambda: self.btn_start.config(state="normal", text="▶ Chạy 12 bài test đánh giá", bg="#a6e3a1"))
            self.dang_chay = False

    def _update_progress_label(self, idx, passed):
        """Cập nhật tiến trình kiểm thử trên thanh trạng thái"""
        self.root.after(0, lambda: self.lbl_summary.config(
            text=f"Đang chạy bài test {idx}/12... | Đạt: {passed}/{idx}", 
            fg="#89b4fa"
        ))

    def _hoan_thanh_tiến_trình_test(self, passed, total, elapsed_time, similarity_scores):
        """Khóa tiến trình test, cập nhật trạng thái cuối cùng và hiển thị bảng thống kê"""
        self.dang_chay = False
        self.btn_start.config(state="normal", text="▶ Chạy 12 bài test đánh giá", bg="#a6e3a1")
        
        if passed == total:
            msg = f"Hoàn thành! 🎉 Đạt: {passed}/{total} (Tất cả bài test đều ĐẠT KỲ VỌNG!)"
            color = "#a6e3a1"
        else:
            msg = f"Hoàn thành! ⚠️ Đạt: {passed}/{total} (Có bài test Thất bại hoặc Bỏ qua)"
            color = "#f9e2af"
            
        self.lbl_summary.config(text=msg, fg=color)
        
        # Thiết lập nội dung thống kê chi tiết các chỉ số cuối cùng
        thong_ke = f"Đã hoàn thành đánh giá {total} bài test!\n\n"
        thong_ke += f"📊 THỐNG KÊ KẾT QUẢ CHẠY TEST:\n"
        thong_ke += f"- Số bài kiểm thử đạt (Passed): {passed}/{total}\n"
        thong_ke += f"- Số bài kiểm thử lỗi (Failed): {total - passed}\n"
        thong_ke += f"- Thời gian thực thi: {elapsed_time:.1f} giây\n\n"
        
        if similarity_scores:
            avg_sim = sum(similarity_scores) / len(similarity_scores)
            min_sim = min(similarity_scores)
            max_sim = max(similarity_scores)
            thong_ke += f"🤖 CHỈ SỐ ĐÁNH GIÁ CHẤT LƯỢNG AI (10 câu RAG):\n"
            thong_ke += f"- Độ khớp ngữ nghĩa trung bình: {avg_sim:.1f}%\n"
            thong_ke += f"- Độ khớp cao nhất: {max_sim:.1f}%\n"
            thong_ke += f"- Độ khớp thấp nhất: {min_sim:.1f}%"
        else:
            thong_ke += "🤖 CHỈ SỐ ĐÁNH GIÁ CHẤT LƯỢNG AI:\n- (Không có dữ liệu thực tế nào được chấm điểm do lỗi hoặc bỏ qua)"
            
        # Hiển thị hộp thông báo MessageBox
        messagebox.showinfo("Kết quả Đánh giá Kiểm thử", thong_ke)

    # =========================================================================
    # LOGIC CHẠY TỪNG TEST CASE CHUYÊN SÂU
    # =========================================================================

    def _exec_test_exception(self):
        """Kiểm thử mô phỏng ngoại lệ (Exception) offline"""
        try:
            # Patch các API gọi ngoài của Ollama
            with patch('backend.Model_ai.ollama.chat') as mock_chat, \
                 patch('backend.Model_ai.ollama.list') as mock_list:
                mock_model_1 = MagicMock()
                mock_model_1.model = "qwen2.5:3b"
                mock_model_2 = MagicMock()
                mock_model_2.model = "nomic-embed-text"
                mock_list.return_value.models = [mock_model_1, mock_model_2]
                mock_chat.side_effect = Exception("Ollama disconnected")
                
                ai = Model_AI(ai_model="qwen2.5:3b")
                reply = ai.ai_reply(prompt="Chào bạn")
                
                # Xác minh ứng dụng có bắt lỗi và đưa ra thông báo an toàn mặc định
                if reply == "Xin lỗi, tôi không thể xử lý yêu cầu này lúc này.":
                    return "PASSED", reply, ""
                else:
                    return "FAILED", reply, "AI không trả về thông báo lỗi mặc định."
        except Exception as e:
            return "FAILED", "", str(e)

    def _exec_test_context(self):
        """Kiểm thử mô phỏng định dạng Prompt gửi đi chứa ngữ cảnh RAG"""
        try:
            with patch('backend.Model_ai.ollama.chat') as mock_chat, \
                 patch('backend.Model_ai.ollama.list') as mock_list:
                mock_model_1 = MagicMock()
                mock_model_1.model = "qwen2.5:3b"
                mock_model_2 = MagicMock()
                mock_model_2.model = "nomic-embed-text"
                mock_list.return_value.models = [mock_model_1, mock_model_2]
                
                mock_response = MagicMock()
                mock_response.message.content = "Mocked: Nhận được ngữ cảnh."
                mock_chat.return_value = mock_response
                
                ai = Model_AI(ai_model="qwen2.5:3b")
                reply = ai.ai_reply(prompt="Python là gì?", context="Tài liệu nói về Python.")
                
                # Kiểm tra cấu trúc prompt gửi đi
                called_args = mock_chat.call_args[1]
                messages = called_args['messages']
                user_content = messages[1]['content']
                
                if "Ngữ cảnh tài liệu tham khảo:" in user_content:
                    return "PASSED", reply, ""
                else:
                    return "FAILED", reply, "Ngữ cảnh không được định dạng đúng trong Prompt gửi đi."
        except Exception as e:
            return "FAILED", "", str(e)

    def _exec_test_rag_real(self, case_id):
        """Chạy kiểm thử sinh câu hỏi RAG thực tế, đo Cosine Similarity"""
        try:
            # Lấy thông số từ danh sách test cases nguồn
            case = self.test_cases[case_id + 1] # Bỏ qua 2 Mock đầu tiên
            
            ai = Model_AI(ai_model="qwen2.5:3b")
            if not ai.status_ai:
                return "SKIPPED", "Mô hình AI chưa sẵn sàng.", None, ""

            # AI sinh câu trả lời tiếng Việt bình thường theo thiết kế gốc
            reply = ai.ai_reply(prompt=case["question"], context=case["context"])
            
            # Tạo vector nhúng cho câu trả lời thực tế và đáp án chuẩn để tính toán độ tương đồng
            res_actual = ollama.embeddings(model=self.embed_model, prompt=reply)
            res_expected = ollama.embeddings(model=self.embed_model, prompt=case["expected"])
            
            vec_actual = res_actual.get("embedding", [])
            vec_expected = res_expected.get("embedding", [])
            
            if not vec_actual or not vec_expected:
                return "FAILED", reply, 0.0, "Không thể tạo vector nhúng để tính độ khớp."

            # Tính điểm Cosine Similarity
            similarity = tinh_cosine_similarity(vec_actual, vec_expected)
            percent = similarity * 100
            
            # Ngưỡng chất lượng đánh giá: độ khớp ngữ nghĩa từ 75% trở lên là PASSED
            status = "PASSED" if similarity >= 0.75 else "FAILED"
            
            return status, reply, percent, ""
        except Exception as e:
            return "FAILED", "", 0.0, str(e)


if __name__ == "__main__":
    root = tk.Tk()
    app = GUITestRunner(root)
    root.mainloop()
