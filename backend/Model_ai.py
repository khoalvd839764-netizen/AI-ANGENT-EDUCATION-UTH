# -*- coding: utf-8 -*-
# =========================================================================
# THƯ MỤC: backend
# TÊN FILE: Model_ai.py
# CHỨC NĂNG CHÍNH: Khởi tạo, kiểm tra các model AI và giao tiếp với Ollama.
# =========================================================================

import sys      # Thư viện hệ thống giúp thiết lập luồng xuất nhập dữ liệu
import io       # Thư viện quản lý luồng dữ liệu I/O
import ollama   # Thư viện Python chính thức của Ollama để giao tiếp với AI cục bộ
import time     # Thư viện thời gian

# Cấu hình mã hóa UTF-8 cho dòng xuất chuẩn stdout và báo lỗi stderr trên hệ điều hành Windows
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

class Model_AI:
    """
    Lớp Model_AI chịu trách nhiệm kiểm tra sự tồn tại của mô hình AI,
    tự động tải mô hình nếu chưa có sẵn, và gọi mô hình để trả lời câu hỏi.
    """
    def __init__(self, ai_model="qwen2.5:3b"):
        # Lưu tên mô hình ngôn ngữ lớn (LLM) sẽ sử dụng
        self.ai_model = ai_model       
        # Trạng thái sẵn sàng kết nối của AI
        self.status_ai = False
        
        print(f"Đang kết nối tới mô hình AI '{self.ai_model}' và mô hình nhúng 'nomic-embed-text'...")

        try:
            # Kiểm tra và tự động tải mô hình Chat LLM
            chat_ok = self.check_and_pull_model(self.ai_model)
            # Kiểm tra và tự động tải mô hình Nhúng văn bản (Embedding)
            embed_ok = self.check_and_pull_model("nomic-embed-text")
            
            # Nếu cả 2 mô hình đều sẵn sàng hoạt động
            if chat_ok and embed_ok:
                self.status_ai = True
                print("Kết nối thành công với tất cả các mô hình AI cần thiết.")
            else:
                self.status_ai = False
                print("Kết nối thất bại do không thể chuẩn bị đầy đủ mô hình.")
        except Exception as e:
            print("Không thể kết nối với Ollama. Vui lòng kiểm tra ứng dụng Ollama đã chạy chưa.", e)
            self.status_ai = False

    def check_and_pull_model(self, model_name):
        """
        Nhiệm vụ: Kiểm tra xem mô hình chỉ định đã được cài đặt trong Ollama hay chưa.
                  Nếu chưa, tiến hành tải về (pull) từ thư viện Ollama.
        """
        try:
            # Lấy danh sách các mô hình hiện có trong thư viện Ollama cục bộ
            check_model = ollama.list()
            # Trích xuất tên của tất cả các mô hình đang có sẵn
            models = [m.model for m in check_model.models]
            
            # Kiểm tra xem mô hình cần thiết đã tồn tại trong danh sách chưa
            if model_name in models or any(model_name in m for m in models):
                print(f"[Ollama] Model '{model_name}' đã sẵn sàng.")
                return True
            else:
                # Nếu chưa có sẵn, tự động gọi lệnh pull để tải mô hình về máy
                print(f"[Ollama] Model '{model_name}' chưa có sẵn. Đang tiến hành tải về (pull)...")
                ollama.pull(model_name)
                print(f"[Ollama] Tải thành công model '{model_name}'.")
                return True
        except Exception as e:
            # Ghi nhận lỗi khi không kết nối được tới dịch vụ Ollama cục bộ
            print(f"[Ollama Error] Lỗi khi kiểm tra hoặc tải model '{model_name}': {e}")
            return False

    def ai_reply(self, prompt, context=""):
        """
        Nhiệm vụ: Gửi câu hỏi và ngữ cảnh (nếu có) sang mô hình LLM và lấy câu trả lời.
        
        Tham số:
            prompt (str): Câu hỏi của người dùng.
            context (str): Đoạn ngữ cảnh trích xuất từ tài liệu (RAG).
            
        Trả về:
            str: Câu trả lời văn bản được sinh ra bởi AI.
        """
        # Định nghĩa Prompt hệ thống (System Prompt) điều phối hành vi của AI trợ lý ảo
        prompt_system = (
            "Bạn là một Trợ lý Ôn tập & Học tập AI chuyên nghiệp. "
            "Nhiệm vụ hàng đầu của bạn là sử dụng thông tin trong ngữ cảnh tài liệu được cung cấp dưới đây để trả lời câu hỏi. "
            "Hãy trả lời bám sát tài liệu một cách chính xác, trung thực và có cấu trúc rõ ràng bằng tiếng Việt. "
            "Nếu ngữ cảnh tài liệu không có thông tin hoặc không đủ để trả lời câu hỏi, bạn phải nói rõ: "
            "'Tài liệu không đề cập đến thông tin này. Dưới đây là câu trả lời dựa trên kiến thức chung của tôi:' "
            "sau đó mới trả lời dựa trên kiến thức chung của bạn."
        )

        # Cấu hình danh sách tin nhắn gửi sang Ollama Chat
        messages = [
            {"role": "system", "content": prompt_system}  # Thiết lập luật ứng xử hệ thống
        ]
        
        # Nếu có truyền ngữ cảnh văn bản (RAG context) từ cơ sở dữ liệu
        if context:
            # Ghép ngữ cảnh và câu hỏi vào tin nhắn người dùng
            messages.append({"role": "user", "content": f"Ngữ cảnh tài liệu tham khảo:\n{context}\n\nCâu hỏi: {prompt}"})
        else:
            # Nếu không có ngữ cảnh (chat thông thường), gửi trực tiếp câu hỏi
            messages.append({"role": "user", "content": prompt})

        # Gửi gói tin nhắn tới Ollama để xử lý
        try:
            reply = ollama.chat(
                model=self.ai_model,
                messages=messages,
                options={
                    "temperature": 0.2,  # Nhiệt độ thấp (0.2) giúp AI trả lời bám sát thực tế tài liệu, tránh bốc phét/sáng tạo quá đà
                    "top_p": 0.7        # Giới hạn phân phối từ ngữ để kiểm soát độ tập trung của câu trả lời
                }
            )
            # Trả về nội dung văn bản của câu trả lời từ AI
            return reply.message.content
        except Exception as e:
            # Xử lý ngoại lệ trong trường hợp kết nối bị ngắt đột ngột khi AI đang suy nghĩ
            print("AI không thể trả lời, vui lòng kiểm tra dịch vụ Ollama", e)
            return "Xin lỗi, tôi không thể xử lý yêu cầu này lúc này."
