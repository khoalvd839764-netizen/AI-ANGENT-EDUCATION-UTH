# -*- coding: utf-8 -*-
# =========================================================================
# FILE: app.py
# NHIỆM VỤ: Giao diện người dùng chính (Main UI) của hệ thống Agent Education.
#           Quản lý luồng Đăng nhập, Đăng ký, tải lên PDF và tương tác hỏi đáp AI.
# THƯ VIỆN GIAO DIỆN: Tkinter (Tích hợp sẵn trong Python).
# =========================================================================

import tkinter as tk                       # Thư viện Tkinter dùng làm giao diện đồ họa gốc
from tkinter import filedialog, scrolledtext, messagebox  # Hộp thoại tệp tin, khung hiển thị cuộn tin nhắn và thông báo
import threading                          # Đa luồng: Chạy các tác vụ nặng (nạp file, hỏi AI) dưới nền để tránh đơ giao diện
import os                                 # Thao tác thư mục và đường dẫn
import sys                                # Quản lý luồng hệ thống
import io                                 # Thao tác luồng dữ liệu I/O

# Thiết lập mã hóa đầu ra chuẩn UTF-8 cho dòng xuất màn hình CMD để hiển thị tiếng Việt chính xác trên Windows
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

# Thư viện gối hỗ trợ tải, căn chỉnh và hiển thị hình ảnh (Logo) trong Tkinter
from PIL import Image, ImageTk

# Đưa thư mục gốc của dự án vào sys.path để có thể import các module bên trong thư mục backend
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.Rag import RagChroma                        # Nạp lớp quản trị vector database RAG
from backend.baomat import kiem_tra_dang_nhap, dang_ky_tai_khoan  # Nạp các hàm bảo mật xác thực tài khoản

# =========================================================================
# LỚP GIAO DIỆN ỨNG DỤNG CHÍNH (MAIN APPLICATION CLASS)
# =========================================================================
class AgentEduApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agent Education - Trợ Lý Học Tập AI")
        self.root.geometry("900x650")
        self.root.configure(bg="#1e1e2e")  # Thiết lập tông màu nền tối sang trọng
        self.root.minsize(800, 600)        # Ràng buộc kích thước cửa sổ tối thiểu để tránh vỡ giao diện

        # Biến trạng thái nội bộ của phiên chạy ứng dụng
        self.file_da_upload = None  # Đường dẫn tuyệt đối của tệp PDF học tập đã nạp thành công
        self.dang_xu_ly = False     # Cờ trạng thái: Đặt thành True khi AI đang suy nghĩ để vô hiệu hóa nút bấm tránh gửi trùng

        # Quản trị thông tin phiên đăng nhập của học viên
        self.da_dang_nhap = False
        self.username_dang_nhap = None
        self.fullname_dang_nhap = None

        self.status_label = None          # Nhãn hiển thị kết nối AI trên Header
        self._tao_giao_dien_dang_nhap()   # Hiển thị biểu mẫu Đăng nhập/Đăng ký trước khi vào màn hình chính

    # =========================================================================
    # VẼ GIAO DIỆN CHATBOT CHÍNH (MAIN INTERFACE)
    # =========================================================================
    def _tao_giao_dien(self):
        """Vẽ toàn bộ giao diện làm việc chính sau khi học viên đăng nhập thành công"""

        # ---------- THANH TIÊU ĐỀ (Header) ----------
        header = tk.Frame(self.root, bg="#313244", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Nhãn chào mừng học viên kèm họ tên lấy từ Database
        tk.Label(
            header,
            text=f"🎓 Agent Education (Welcome, {self.fullname_dang_nhap})",
            font=("Segoe UI", 18, "bold"),
            fg="#cdd6f4", bg="#313244"
        ).pack(side="left", padx=15, pady=10)

        # Nhãn hiển thị trạng thái của kết nối AI (Nằm góc phải Header)
        self.status_label = tk.Label(
            header,
            text="⏳ Đang kết nối AI...",
            font=("Segoe UI", 10),
            fg="#f9e2af", bg="#313244"
        )
        self.status_label.pack(side="right", padx=15, pady=10)

        # ---------- KHU VỰC CHÍNH (Main Content Area) ----------
        main_frame = tk.Frame(self.root, bg="#1e1e2e")
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # ====== CỘT TRÁI: Khu vực Quản lý Tệp tải lên ======
        left_panel = tk.Frame(main_frame, bg="#181825", width=280)
        left_panel.pack(side="left", fill="y", padx=(0, 5))
        left_panel.pack_propagate(False)

        tk.Label(
            left_panel,
            text="📂 Tài Liệu Học Tập",
            font=("Segoe UI", 12, "bold"),
            fg="#cdd6f4", bg="#181825"
        ).pack(pady=(15, 10))

        # Nút chọn tải lên tài liệu PDF mới
        self.btn_upload = tk.Button(
            left_panel,
            text="📎 Upload File PDF",
            font=("Segoe UI", 11),
            fg="#1e1e2e", bg="#a6e3a1",
            activebackground="#94e2d5",
            cursor="hand2", relief="flat",
            padx=15, pady=8,
            command=self._xu_ly_upload_file
        )
        self.btn_upload.pack(pady=10, padx=15, fill="x")

        # Nhãn hiển thị tên file PDF hiện đang được chọn
        self.label_file = tk.Label(
            left_panel,
            text="Chưa có file nào được tải lên.",
            font=("Segoe UI", 9),
            fg="#6c7086", bg="#181825",
            wraplength=250
        )
        self.label_file.pack(pady=(0, 10), padx=10)

        # Nút yêu cầu AI tự động tóm tắt toàn bộ file
        self.btn_analyze = tk.Button(
            left_panel,
            text="🔍 Phân Tích Tài Liệu",
            font=("Segoe UI", 11),
            fg="#1e1e2e", bg="#89b4fa",
            activebackground="#74c7ec",
            cursor="hand2", relief="flat",
            padx=15, pady=8,
            state="disabled",  # Chỉ kích hoạt nút này sau khi đã nạp và lưu thành công Vector tài liệu
            command=self._xu_ly_phan_tich
        )
        self.btn_analyze.pack(pady=5, padx=15, fill="x")

        # ====== CỘT PHẢI: Khung Trò chuyện Chatbot AI ======
        right_panel = tk.Frame(main_frame, bg="#1e1e2e")
        right_panel.pack(side="right", fill="both", expand=True)

        tk.Label(
            right_panel,
            text="💬 Trò chuyện với AI",
            font=("Segoe UI", 12, "bold"),
            fg="#cdd6f4", bg="#1e1e2e", anchor="w"
        ).pack(fill="x", pady=(5, 5))

        # Khung văn bản cuộn chứa các đoạn hội thoại chat
        self.chat_display = scrolledtext.ScrolledText(
            right_panel,
            wrap="word",
            font=("Segoe UI", 11),
            bg="#11111b", fg="#cdd6f4",
            insertbackground="#cdd6f4",
            selectbackground="#45475a",
            relief="flat",
            padx=10, pady=10,
            state="disabled"  # Khóa trạng thái để người dùng không gõ đè văn bản chat trực tiếp
        )
        self.chat_display.pack(fill="both", expand=True, pady=(0, 5))

        # Định dạng màu sắc nhãn tin nhắn (User: Xanh lá, AI: Xanh lơ, Hệ thống: Vàng cam)
        self.chat_display.tag_config("user_tag", foreground="#a6e3a1", font=("Segoe UI", 11, "bold"))
        self.chat_display.tag_config("ai_tag", foreground="#89b4fa", font=("Segoe UI", 11, "bold"))
        self.chat_display.tag_config("system_tag", foreground="#f9e2af", font=("Segoe UI", 10, "italic"))

        # Khung nhập câu hỏi và nút gửi nằm dưới cùng cột phải
        input_frame = tk.Frame(right_panel, bg="#1e1e2e")
        input_frame.pack(fill="x")

        self.chat_input = tk.Entry(
            input_frame,
            font=("Segoe UI", 12),
            bg="#313244", fg="#cdd6f4",
            insertbackground="#cdd6f4",
            relief="flat"
        )
        self.chat_input.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 5))
        # Liên kết phím Enter của bàn phím kích hoạt gửi tin nhắn nhanh
        self.chat_input.bind("<Return>", self._xu_ly_gui_tin_nhan)

        self.btn_send = tk.Button(
            input_frame,
            text="Gửi ➤",
            font=("Segoe UI", 11, "bold"),
            fg="#1e1e2e", bg="#a6e3a1",
            activebackground="#94e2d5",
            cursor="hand2", relief="flat",
            padx=15, pady=6,
            command=lambda: self._xu_ly_gui_tin_nhan(None)
        )
        self.btn_send.pack(side="right")

    # =========================================================================
    # KHỞI TẠO BACKEND TRÊN THREAD PHỤ (BACKGROUND THREAD)
    # =========================================================================
    def _khoi_tao_backend(self):
        """Khởi tạo đối tượng RAG và kết nối AI dưới luồng phụ, tránh treo cứng GUI"""
        def _chay_nen():
            try:
                # Tạo đối tượng quản trị RAG Chroma
                self.rag = RagChroma()
                
                # Cập nhật kết quả lên giao diện chính
                # Sử dụng root.after để điều phối cập nhật luồng chính từ luồng phụ an toàn
                if self.rag.ai.status_ai:
                    self.root.after(0, lambda: self.status_label.config(
                        text="✅ AI đã sẵn sàng", fg="#a6e3a1"
                    ))
                    self.root.after(0, lambda: self._them_tin_nhan(
                        "Hệ thống", "Chào mừng bạn đến với Agent Education! 🎓\n"
                        "AI đã sẵn sàng. Bạn có thể:\n"
                        "• Upload file PDF để trợ lý ảo học tài liệu mới.\n"
                        "• Nhập câu hỏi trực tiếp để trò chuyện hoặc phân tích tài liệu.\n",
                        "system_tag"
                    ))
                else:
                    self.root.after(0, lambda: self.status_label.config(
                        text="❌ AI chưa sẵn sàng", fg="#f38ba8"
                    ))
                    self.root.after(0, lambda: self._them_tin_nhan(
                        "Hệ thống", "Không thể kết nối với Ollama. Vui lòng bật ứng dụng Ollama và thử lại.",
                        "system_tag"
                    ))
            except Exception as e:
                self.rag = None
                self.root.after(0, lambda: self.status_label.config(
                    text="❌ Lỗi khởi tạo", fg="#f38ba8"
                ))
                err_msg = str(e)
                self.root.after(0, lambda: self._them_tin_nhan(
                    "Hệ thống", f"Lỗi kết nối hoặc khởi tạo hệ thống AI: {err_msg}", "system_tag"
                ))

        # Khởi chạy tiểu trình
        thread = threading.Thread(target=_chay_nen, daemon=True)
        thread.start()

    # =========================================================================
    # XỬ LÝ CÁC SỰ KIỆN CỦA HỆ THỐNG
    # =========================================================================
    def _them_tin_nhan(self, nguoi_gui, noi_dung, tag):
        """
        Phương thức hỗ trợ chèn thêm dòng tin nhắn mới vào khung chat hiển thị.
        """
        self.chat_display.config(state="normal")  # Tạm thời mở khóa để ghi chữ
        self.chat_display.insert("end", f"\n[{nguoi_gui}]:\n", tag)
        self.chat_display.insert("end", f"{noi_dung}\n")
        self.chat_display.config(state="disabled")  # Khóa lại giao diện tránh người dùng can thiệp
        self.chat_display.see("end")  # Tự động cuộn thanh cuốn xuống dòng dưới cùng

    def _xu_ly_upload_file(self):
        """Kích hoạt hộp thoại chọn file PDF từ máy tính và lưu trữ vào Vector DB RAG"""
        filepath = filedialog.askopenfilename(
            title="Chọn file PDF tài liệu",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if not filepath:
            return  # Trở ra nếu học viên bấm Cancel tắt bảng chọn

        self.file_da_upload = filepath
        filename = os.path.basename(filepath)
        self.label_file.config(text=f"📄 {filename}", fg="#a6e3a1")
        
        # Tạm thời khóa các nút chức năng để tránh xung đột luồng khi đang ghi file
        self.btn_upload.config(state="disabled")
        self.btn_analyze.config(state="disabled")

        self._them_tin_nhan("Hệ thống", f"Đã chọn tài liệu: {filename}", "system_tag")
        self._them_tin_nhan("Hệ thống", "Đang phân tích, cắt nhỏ văn bản và tạo Vector nhúng để nạp vào ChromaDB...", "system_tag")

        # Tiến hành trích xuất chữ và nhúng vector dưới luồng nền
        def _nap_file():
            try:
                ket_qua = self.rag.add_document_to_db(filepath)
                if ket_qua:
                    self.root.after(0, lambda: self._them_tin_nhan(
                        "Hệ thống",
                        f"✅ Đã nạp thành công tài liệu '{filename}' vào Vector Database!\n"
                        "Bây giờ bạn có thể nhập câu hỏi để tìm kiếm thông tin trên cuốn sách này.",
                        "system_tag"
                    ))
                    # Mở lại nút Phân tích và tải lên
                    self.root.after(0, lambda: self.btn_analyze.config(state="normal"))
                    self.root.after(0, lambda: self.btn_upload.config(state="normal"))
                else:
                    self.root.after(0, lambda: self._them_tin_nhan(
                        "Hệ thống",
                        "⚠️ Nạp tài liệu thất bại. Tệp tin có thể rỗng hoặc là tài liệu scan dạng hình ảnh không có văn bản dạng số.",
                        "system_tag"
                    ))
                    self.root.after(0, lambda: self.btn_upload.config(state="normal"))
            except Exception as e:
                err_msg = str(e)
                self.root.after(0, lambda: self._them_tin_nhan(
                    "Hệ thống", f"❌ Gặp lỗi trong quá trình nạp tệp: {err_msg}", "system_tag"
                ))
                self.root.after(0, lambda: self.btn_upload.config(state="normal"))

        thread = threading.Thread(target=_nap_file, daemon=True)
        thread.start()

    def _xu_ly_gui_tin_nhan(self, event):
        """Xử lý sự kiện học viên nhập câu hỏi, trích xuất RAG và gọi AI phản hồi"""
        cau_hoi = self.chat_input.get().strip()
        if not cau_hoi or self.dang_xu_ly:
            return

        if not hasattr(self, 'rag') or self.rag is None:
            self._them_tin_nhan("Hệ thống", "Hệ thống AI chưa sẵn sàng khởi tạo, vui lòng đợi giây lát...", "system_tag")
            return

        # Hiển thị câu hỏi của học viên lên màn hình và làm trống ô nhập
        self._them_tin_nhan("Bạn", cau_hoi, "user_tag")
        self.chat_input.delete(0, "end")

        # Thiết lập cờ bận xử lý và đổi nút Gửi thành ký hiệu chờ
        self.dang_xu_ly = True
        self.btn_send.config(state="disabled", text="⏳...")

        # Chạy tác vụ gọi AI dưới nền
        def _hoi_ai():
            try:
                # Nếu đã tải tài liệu, tiến hành truy xuất RAG
                if self.file_da_upload:
                    filename = os.path.basename(self.file_da_upload)
                    tra_loi = self.rag.ask_with_rag(cau_hoi, filename=filename)
                else:
                    # Nếu chưa nạp tệp, AI trả lời bằng kiến thức nền
                    tra_loi = self.rag.ai.ai_reply(prompt=cau_hoi, context="")

                self.root.after(0, lambda: self._them_tin_nhan("AI", tra_loi, "ai_tag"))
            except Exception as e:
                err_msg = str(e)
                self.root.after(0, lambda: self._them_tin_nhan(
                    "Hệ thống", f"❌ Lỗi phản hồi AI: {err_msg}", "system_tag"
                ))
            finally:
                self.dang_xu_ly = False
                self.root.after(0, lambda: self.btn_send.config(state="normal", text="Gửi ➤"))

        thread = threading.Thread(target=_hoi_ai, daemon=True)
        thread.start()

    def _xu_ly_phan_tich(self):
        """Xử lý tác vụ tự động phân tích và tóm tắt nhanh tài liệu PDF hiện tại"""
        if not self.file_da_upload or self.dang_xu_ly:
            return

        self._them_tin_nhan("Bạn", "Hãy phân tích và tóm tắt nội dung tài liệu.", "user_tag")
        self.dang_xu_ly = True
        self.btn_analyze.config(state="disabled")

        def _phan_tich():
            try:
                prompt = (
                    "Hãy tóm tắt và phân tích nội dung chính của tài liệu này. "
                    "Đưa ra các ý cốt lõi dưới dạng gạch đầu dòng rõ ràng, dễ hiểu."
                )
                filename = os.path.basename(self.file_da_upload)
                tra_loi = self.rag.ask_with_rag(prompt, filename=filename)
                self.root.after(0, lambda: self._them_tin_nhan("AI", tra_loi, "ai_tag"))
            except Exception as e:
                err_msg = str(e)
                self.root.after(0, lambda: self._them_tin_nhan(
                    "Hệ thống", f"❌ Lỗi khi phân tích tài liệu: {err_msg}", "system_tag"
                ))
            finally:
                self.dang_xu_ly = False
                self.root.after(0, lambda: self.btn_analyze.config(state="normal"))

        thread = threading.Thread(target=_phan_tich, daemon=True)
        thread.start()

    # =========================================================================
    # GIAO DIỆN & XỬ LÝ ĐĂNG NHẬP / ĐĂNG KÝ HỌC VIÊN
    # =========================================================================
    def _tao_giao_dien_dang_nhap(self):
        """Khởi tạo màn hình đăng nhập"""
        self.login_frame = tk.Frame(self.root, bg="#1e1e2e")
        self.login_frame.pack(fill="both", expand=True)

        # Thiết lập khung thẻ (Login Card) căn giữa màn hình
        self.card_frame = tk.Frame(
            self.login_frame, 
            bg="#181825", 
            padx=45, 
            pady=45, 
            highlightbackground="#45475a", 
            highlightthickness=1
        )
        self.card_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Vẽ form đăng nhập
        self._hien_thi_form_dang_nhap()

    def _hien_thi_form_dang_nhap(self):
        """Vẽ biểu mẫu nhập thông tin đăng nhập"""
        # Giải phóng các phần tử đồ họa đang vẽ trên Card để đổi biểu mẫu
        for widget in self.card_frame.winfo_children():
            widget.destroy()

        # Thử tải hình ảnh Logo của trường UTH từ thư mục access
        logo_loaded = False
        try:
            goc_dir = os.path.dirname(os.path.abspath(__file__))
            duong_dan_logo = os.path.join(goc_dir, "access", "logo_uth.png")
            if os.path.exists(duong_dan_logo):
                img = Image.open(duong_dan_logo)
                w_new = 280
                h_new = int(img.height * (w_new / img.width))
                img = img.resize((w_new, h_new), Image.Resampling.LANCZOS)
                
                # Lưu giữ biến tham chiếu ảnh để tránh rác hệ thống xóa mất dữ liệu ảnh
                self.logo_image = ImageTk.PhotoImage(img)
                lbl_logo = tk.Label(self.card_frame, image=self.logo_image, bg="#181825")
                lbl_logo.pack(pady=(0, 15))
                logo_loaded = True
        except Exception as e:
            print(f"Không thể tải ảnh logo UTH: {e}")

        # Tiêu đề Form
        title_text = "Đăng Nhập Agent Edu" if logo_loaded else "🎓 Đăng Nhập Agent Edu"
        tk.Label(
            self.card_frame,
            text=title_text,
            font=("Segoe UI", 16, "bold"),
            fg="#cdd6f4", bg="#181825"
        ).pack(pady=(0, 15))

        # Tên tài khoản
        tk.Label(
            self.card_frame,
            text="Tên đăng nhập:",
            font=("Segoe UI", 10),
            fg="#a6adc8", bg="#181825", anchor="w"
        ).pack(fill="x", pady=(10, 2))
        
        self.entry_username = tk.Entry(
            self.card_frame,
            font=("Segoe UI", 11),
            bg="#313244", fg="#cdd6f4",
            insertbackground="#cdd6f4",
            relief="flat", width=30
        )
        self.entry_username.pack(ipady=6, pady=(0, 10))
        self.entry_username.focus()  # Tự động nhảy con trỏ chuột vào ô đăng nhập

        # Mật khẩu
        tk.Label(
            self.card_frame,
            text="Mật khẩu:",
            font=("Segoe UI", 10),
            fg="#a6adc8", bg="#181825", anchor="w"
        ).pack(fill="x", pady=(5, 2))
        
        self.entry_password = tk.Entry(
            self.card_frame,
            font=("Segoe UI", 11),
            bg="#313244", fg="#cdd6f4",
            insertbackground="#cdd6f4",
            show="*", relief="flat", width=30
        )
        self.entry_password.pack(ipady=6, pady=(0, 10))
        # Liên kết nút Enter tiến hành đăng nhập trực tiếp
        self.entry_password.bind("<Return>", lambda e: self._thuc_hien_dang_nhap())

        # Nhãn báo trạng thái lỗi
        self.lbl_login_status = tk.Label(
            self.card_frame,
            text="",
            font=("Segoe UI", 10),
            fg="#f38ba8", bg="#181825",
            wraplength=280
        )
        self.lbl_login_status.pack(pady=5)

        # Nút bấm Xác nhận Đăng nhập
        btn_login = tk.Button(
            self.card_frame,
            text="Đăng Nhập",
            font=("Segoe UI", 11, "bold"),
            fg="#1e1e2e", bg="#a6e3a1",
            activebackground="#94e2d5",
            cursor="hand2", relief="flat",
            command=self._thuc_hien_dang_nhap,
            pady=6
        )
        btn_login.pack(fill="x", pady=10)

        # Nút chuyển đổi giao diện sang đăng ký tài khoản mới
        btn_go_to_reg = tk.Button(
            self.card_frame,
            text="Chưa có tài khoản? Đăng ký ngay",
            font=("Segoe UI", 9, "underline"),
            fg="#89b4fa", bg="#181825",
            activebackground="#181825",
            activeforeground="#b4befe",
            cursor="hand2", relief="flat",
            command=self._hien_thi_form_dang_ky,
            bd=0
        )
        btn_go_to_reg.pack(pady=5)

    def _hien_thi_form_dang_ky(self):
        """Vẽ biểu mẫu đăng ký tài khoản học viên mới"""
        # Giải phóng giao diện đăng nhập trên thẻ Card
        for widget in self.card_frame.winfo_children():
            widget.destroy()

        logo_loaded = False
        try:
            goc_dir = os.path.dirname(os.path.abspath(__file__))
            duong_dan_logo = os.path.join(goc_dir, "access", "logo_uth.png")
            if os.path.exists(duong_dan_logo):
                img = Image.open(duong_dan_logo)
                w_new = 280
                h_new = int(img.height * (w_new / img.width))
                img = img.resize((w_new, h_new), Image.Resampling.LANCZOS)
                
                self.logo_image = ImageTk.PhotoImage(img)
                lbl_logo = tk.Label(self.card_frame, image=self.logo_image, bg="#181825")
                lbl_logo.pack(pady=(0, 10))
                logo_loaded = True
        except Exception as e:
            print(f"Lỗi tải logo UTH đăng ký: {e}")

        # Tiêu đề Form
        title_text = "Đăng Ký Agent Edu" if logo_loaded else "🎓 Đăng Ký Agent Edu"
        tk.Label(
            self.card_frame,
            text=title_text,
            font=("Segoe UI", 16, "bold"),
            fg="#cdd6f4", bg="#181825"
        ).pack(pady=(0, 10))

        # Ô nhập Họ và Tên
        tk.Label(
            self.card_frame,
            text="Họ và tên:",
            font=("Segoe UI", 10),
            fg="#a6adc8", bg="#181825", anchor="w"
        ).pack(fill="x", pady=(5, 2))
        
        self.entry_fullname = tk.Entry(
            self.card_frame,
            font=("Segoe UI", 11),
            bg="#313244", fg="#cdd6f4",
            insertbackground="#cdd6f4",
            relief="flat", width=30
        )
        self.entry_fullname.pack(ipady=6, pady=(0, 5))
        self.entry_fullname.focus()

        # Ô nhập Tên đăng nhập
        tk.Label(
            self.card_frame,
            text="Tên đăng nhập (ít nhất 3 ký tự):",
            font=("Segoe UI", 10),
            fg="#a6adc8", bg="#181825", anchor="w"
        ).pack(fill="x", pady=(5, 2))
        
        self.entry_reg_username = tk.Entry(
            self.card_frame,
            font=("Segoe UI", 11),
            bg="#313244", fg="#cdd6f4",
            insertbackground="#cdd6f4",
            relief="flat", width=30
        )
        self.entry_reg_username.pack(ipady=6, pady=(0, 5))

        # Ô nhập Mật khẩu
        tk.Label(
            self.card_frame,
            text="Mật khẩu (ít nhất 6 ký tự):",
            font=("Segoe UI", 10),
            fg="#a6adc8", bg="#181825", anchor="w"
        ).pack(fill="x", pady=(5, 2))
        
        self.entry_reg_password = tk.Entry(
            self.card_frame,
            font=("Segoe UI", 11),
            bg="#313244", fg="#cdd6f4",
            insertbackground="#cdd6f4",
            show="*", relief="flat", width=30
        )
        self.entry_reg_password.pack(ipady=6, pady=(0, 5))

        # Ô xác nhận mật khẩu
        tk.Label(
            self.card_frame,
            text="Xác nhận mật khẩu:",
            font=("Segoe UI", 10),
            fg="#a6adc8", bg="#181825", anchor="w"
        ).pack(fill="x", pady=(5, 2))
        
        self.entry_reg_confirm_password = tk.Entry(
            self.card_frame,
            font=("Segoe UI", 11),
            bg="#313244", fg="#cdd6f4",
            insertbackground="#cdd6f4",
            show="*", relief="flat", width=30
        )
        self.entry_reg_confirm_password.pack(ipady=6, pady=(0, 5))
        # Liên kết phím Enter kích hoạt Đăng ký
        self.entry_reg_confirm_password.bind("<Return>", lambda e: self._thuc_hien_dang_ky())

        # Nhãn hiển thị trạng thái của biểu mẫu Đăng ký
        self.lbl_reg_status = tk.Label(
            self.card_frame,
            text="",
            font=("Segoe UI", 10),
            fg="#f38ba8", bg="#181825",
            wraplength=280
        )
        self.lbl_reg_status.pack(pady=5)

        # Nút Đăng ký tài khoản
        btn_register = tk.Button(
            self.card_frame,
            text="Đăng Ký",
            font=("Segoe UI", 11, "bold"),
            fg="#1e1e2e", bg="#a6e3a1",
            activebackground="#94e2d5",
            cursor="hand2", relief="flat",
            command=self._thuc_hien_dang_ky,
            pady=6
        )
        btn_register.pack(fill="x", pady=5)

        # Nút quay về đăng nhập
        btn_back = tk.Button(
            self.card_frame,
            text="← Đã có tài khoản? Đăng nhập",
            font=("Segoe UI", 9, "underline"),
            fg="#89b4fa", bg="#181825",
            activebackground="#181825",
            activeforeground="#b4befe",
            cursor="hand2", relief="flat",
            command=self._hien_thi_form_dang_nhap,
            bd=0
        )
        btn_back.pack(pady=5)

    def _thuc_hien_dang_nhap(self):
        """Logic kiểm thử thông tin đăng nhập từ cơ sở dữ liệu"""
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not username or not password:
            self.lbl_login_status.config(text="⚠️ Vui lòng nhập đầy đủ Tài khoản & Mật khẩu!", fg="#f9e2af")
            return

        # Gọi hàm kiểm tra dữ liệu từ file baomat.py kết nối SQLite
        success, msg, fullname = kiem_tra_dang_nhap(username, password)
        
        if success:
            self.da_dang_nhap = True
            self.username_dang_nhap = username
            self.fullname_dang_nhap = fullname
            
            # Giải phóng màn hình đăng nhập
            self.login_frame.destroy()
            
            # Khởi tạo giao diện chính và kết nối trợ lý AI
            self._tao_giao_dien()
            self._khoi_tao_backend()
        else:
            self.lbl_login_status.config(text=f"❌ {msg}", fg="#f38ba8")

    def _thuc_hien_dang_ky(self):
        """Logic chèn thông tin tài khoản mới vào cơ sở dữ liệu"""
        fullname = self.entry_fullname.get().strip()
        username = self.entry_reg_username.get().strip()
        password = self.entry_reg_password.get().strip()
        confirm_password = self.entry_reg_confirm_password.get().strip()

        # Kiểm chứng điều kiện cơ bản
        if not fullname or not username or not password or not confirm_password:
            self.lbl_reg_status.config(text="⚠️ Vui lòng nhập đầy đủ các trường thông tin!", fg="#f9e2af")
            return

        if password != confirm_password:
            self.lbl_reg_status.config(text="❌ Mật khẩu xác nhận không khớp!", fg="#f38ba8")
            return

        # Gọi hàm xử lý lưu SQLite ở backend
        success, msg = dang_ky_tai_khoan(username, password, fullname)

        if success:
            self.lbl_reg_status.config(text=f"✅ {msg}", fg="#a6e3a1")
            
            # Chờ 1.5 giây để học viên đọc thông báo đăng ký thành công rồi tự động chuyển lại form đăng nhập
            def quay_lai_dang_nhap():
                self._hien_thi_form_dang_nhap()
                self.entry_username.insert(0, username)
                self.entry_password.focus()
            
            self.root.after(1500, quay_lai_dang_nhap)
        else:
            self.lbl_reg_status.config(text=f"❌ {msg}", fg="#f38ba8")


# =========================================================================
# KHỞI CHẠY HỆ THỐNG
# =========================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = AgentEduApp(root)
    root.mainloop()
