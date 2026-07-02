# -*- coding: utf-8 -*-
# =========================================================================
# TÊN FILE: chay_test_cmd.py
# CHỨC NĂNG CHÍNH: Trình chạy kiểm thử giao diện dòng lệnh (CMD Test Runner).
#                  Tự động kiểm tra chất lượng AI, tính Cosine Similarity,
#                  xuất chỉ số thống kê và hỗ trợ Exit Code cho CI/CD.
# =========================================================================

import sys     # Quản lý luồng hệ thống và mã lỗi thoát (Exit Code)
import os      # Thao tác với thư mục và đường dẫn tệp tin
import time    # Đo lường thời gian chạy của bộ test
import socket  # Kiểm tra trạng thái cổng mạng của Ollama
from unittest.mock import patch, MagicMock  # Giả lập môi trường test offline
import ollama  # Kết nối tới mô hình nhúng và AI cục bộ

# Cấu hình UTF-8 cho stdout/stderr để tránh lỗi hiển thị tiếng Việt trên Windows Console
if sys.stdout is not None:
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

# Thêm thư mục hiện tại vào đường dẫn hệ thống để import được Model_AI từ backend
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.Model_ai import Model_AI

# Mã màu ANSI để trang trí kết quả in ra màn hình Terminal
GREEN = "\033[92m"   # Màu xanh lá (Test đạt)
RED = "\033[91m"     # Màu đỏ (Test lỗi/thất bại)
YELLOW = "\033[93m"  # Màu vàng (Bỏ qua/Cảnh báo)
CYAN = "\033[96m"    # Màu xanh lơ (Tiêu đề/Thông số)
BOLD = "\033[1m"     # Chữ in đậm
RESET = "\033[0m"    # Trở lại màu mặc định

# Kích hoạt chế độ hỗ trợ màu ANSI trên Windows Command Prompt / PowerShell
os.system('')

def is_ollama_running():
    """
    Kiểm tra xem dịch vụ Ollama cục bộ có đang chạy hay không.
    Kết nối thử tới cổng 11434 (cổng mặc định của Ollama).
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
    Tính toán độ tương tự Cosine (Cosine Similarity) giữa 2 Vector số thực.
    Độ tương đồng nằm trong khoảng [-1.0, 1.0], nhân với 100 thành phần trăm.
    """
    if not vec1 or not vec2:
        return 0.0
    dot_product = sum(x * y for x, y in zip(vec1, vec2))
    norm1 = sum(x * x for x in vec1) ** 0.5
    norm2 = sum(x * x for x in vec2) ** 0.5
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)

# Khai báo bộ dữ liệu 12 test cases (2 Mock, 10 RAG tiếng Việt dựa trên sách Data Science)
test_cases = [
    {
        "id": 1,
        "name": "Kiểm thử Mock: Xử lý ngoại lệ (Exception)",
        "context": "N/A",
        "question": "Chào bạn (khi mất kết nối)",
        "expected": "Trả về thông báo lỗi mặc định: 'Xin lỗi, tôi không thể xử lý yêu cầu này lúc này.'",
        "type": "mock_exception"
    },
    {
        "id": 2,
        "name": "Kiểm thử Mock: Truyền kèm Ngữ cảnh (Context)",
        "context": "Tài liệu này nói về Lập trình Python.",
        "question": "Python là gì?",
        "expected": "Prompt gửi lên AI phải chứa tiêu đề 'Ngữ cảnh tài liệu tham khảo:'.",
        "type": "mock_context"
    },
    {
        "id": 3,
        "name": "Kiểm thử AI RAG: Câu 1 - Công cụ lập trình chính",
        "context": "The book uses Python as a tool to implement and exploit some of the most common algorithms used in data science and data analytics today.",
        "question": "Ngôn ngữ lập trình nào được sử dụng làm công cụ chính trong sách này để triển khai các thuật toán khoa học dữ liệu?",
        "expected": "Ngôn ngữ lập trình Python được sử dụng làm công cụ chính trong sách này để triển khai và khai thác các thuật toán khoa học dữ liệu.",
        "type": "rag"
    },
    {
        "id": 4,
        "name": "Kiểm thử AI RAG: Câu 2 - iPython/Jupyter Notebook",
        "context": "iPython/Jupyter Notebook is a flexible web-based computational environment that combines code, text, mathematics and plots in a single document.",
        "question": "iPython hoặc Jupyter Notebook là gì theo cuốn sách?",
        "expected": "Jupyter Notebook/iPython là một môi trường tính toán linh hoạt trên nền web kết hợp mã nguồn, văn bản, toán học và biểu đồ trong cùng một tài liệu.",
        "type": "rag"
    },
    {
        "id": 5,
        "name": "Kiểm thử AI RAG: Câu 3 - Phiên bản thư viện",
        "context": "The examples contained in this volume have been tested in Python 3.5... and packages used: Python-3.5.2, Pandas-0.19.1, NumPy-1.11.2, Scikit-learn-0.18, StatsModels-0.6.1",
        "question": "Liệt kê phiên bản các thư viện Pandas và Scikit-learn đã được sử dụng để kiểm thử các ví dụ trong sách.",
        "expected": "Các ví dụ được chạy kiểm thử với Pandas phiên bản 0.19.1 và Scikit-learn phiên bản 0.18.",
        "type": "rag"
    },
    {
        "id": 6,
        "name": "Kiểm thử AI RAG: Câu 4 - Bản phân phối Python",
        "context": "In particular I have chosen to use the Anaconda Python distribution provided by Continuum Analytics as it offers installations in all of the three computer systems... and offers a rich ecosystem of libraries",
        "question": "Tác giả đã chọn bản phân phối Python nào cho cuốn sách này và bên nào cung cấp nó?",
        "expected": "Tác giả đã chọn bản phân phối Anaconda Python do Continuum Analytics cung cấp.",
        "type": "rag"
    },
    {
        "id": 7,
        "name": "Kiểm thử AI RAG: Câu 5 - Quy trình Data Science",
        "context": "From Data to Insight: the Data Science Workflow: 1.4.1 Identify the Question, 1.4.2 Acquire Data, 1.4.3 Data Munging, 1.4.4 Modelling and Evaluation, 1.4.5 Representation and Interaction, 1.4.6 Data Science: an Iterative Process",
        "question": "Các bước chính trong quy trình khoa học dữ liệu (Data Science workflow) được mô tả trong Chương 1 là gì?",
        "expected": "Quy trình khoa học dữ liệu gồm các bước: Xác định câu hỏi, Thu thập dữ liệu, Làm sạch dữ liệu (Data Munging), Xây dựng mô hình & Đánh giá, Trực quan hóa & Tương tác.",
        "type": "rag"
    },
    {
        "id": 8,
        "name": "Kiểm thử AI RAG: Câu 6 - Ưu điểm của Python",
        "context": "Python is a popular and versatile scripting and object-oriented language, it is easy to use and has a large active community of developers and enthusiasts",
        "question": "Theo lời mở đầu, tại sao Python lại là một công cụ phù hợp cho khoa học dữ liệu?",
        "expected": "Python phù hợp vì nó là ngôn ngữ lập trình hướng đối tượng và kịch bản phổ biến, linh hoạt, dễ sử dụng và có cộng đồng lập trình viên năng động.",
        "type": "rag"
    },
    {
        "id": 9,
        "name": "Kiểm thử AI RAG: Câu 7 - Mục tiêu cuốn sách",
        "context": "The main purpose of the book is to present the reader with some of the main concepts used in data science and analytics using tools developed in Python such as Scikit-learn, Pandas, Numpy and others.",
        "question": "Mục đích chính của cuốn sách Data Science and Analytics with Python là gì?",
        "expected": "Mục đích chính của cuốn sách là trình bày các khái niệm cốt lõi trong khoa học dữ liệu bằng cách sử dụng các công cụ Python như Scikit-learn, Pandas, và NumPy.",
        "type": "rag"
    },
    {
        "id": 10,
        "name": "Kiểm thử AI RAG: Câu 8 - Đối tượng độc giả",
        "context": "The book is intended to be a companion to data analysts and budding data scientists that have some working experience with both programming and statistical modelling, but who have not necessarily delved into the wonders of data analytics and machine learning.",
        "question": "Độc giả mục tiêu của cuốn sách này là những ai?",
        "expected": "Độc giả mục tiêu là các nhà phân tích dữ liệu và nhà khoa học dữ liệu mới vào nghề đã có kinh nghiệm lập trình và mô hình hóa thống kê nhưng chưa nghiên cứu sâu về học máy.",
        "type": "rag"
    },
    {
        "id": 11,
        "name": "Kiểm thử AI RAG: Câu 9 - Vai trò Gom cụm & Phân lớp",
        "context": "In Chapter 5 we talk about clustering techniques, whereas Chapter 6 covers classification algorithms. These two chapters are central to the data science workflow: Clustering enables us to assign labels to our data in an unsupervised manner; in turn we can use these labels as targets in a classification algorithm.",
        "question": "Giải thích vai trò và mối quan hệ giữa Chương 5 (Phân cụm) và Chương 6 (Phân lớp) trong quy trình xử lý dữ liệu.",
        "expected": "Phân cụm (Chương 5) giúp gán nhãn cho dữ liệu chưa được gắn nhãn (không giám sát), sau đó các nhãn này được dùng làm mục tiêu đầu vào cho thuật toán phân lớp (Chương 6 - có giám sát).",
        "type": "rag"
    },
    {
        "id": 12,
        "name": "Kiểm thử AI RAG: Câu 10 - Môi trường thử nghiệm",
        "context": "The examples contained in this volume have been tested in Python 3.5 under MacOS, Linux and Windows 7, and the code can be run with minimal changes in a Python 2 distribution.",
        "question": "Các ví dụ trong cuốn sách này đã được chạy kiểm thử trên các hệ điều hành và phiên bản Python nào?",
        "expected": "Các ví dụ đã được chạy kiểm thử trên Python 3.5 dưới các hệ điều hành MacOS, Linux và Windows 7.",
        "type": "rag"
    }
]

def exec_mock_exception():
    """
    Thực thi bài test mô phỏng lỗi sập nguồn AI (Test Case 1).
    Bắt buộc phải chạy thành công offline hoàn toàn.
    """
    # Patch (giả lập) lệnh chat và danh sách mô hình của Ollama
    with patch('backend.Model_ai.ollama.chat') as mock_chat, \
         patch('backend.Model_ai.ollama.list') as mock_list:
        mock_model_1 = MagicMock()
        mock_model_1.model = "qwen2.5:3b"
        mock_model_2 = MagicMock()
        mock_model_2.model = "nomic-embed-text"
        mock_list.return_value.models = [mock_model_1, mock_model_2]
        
        # Bắt Ollama.chat ném ra lỗi kết nối
        mock_chat.side_effect = Exception("Ollama disconnected")
        
        ai = Model_AI(ai_model="qwen2.5:3b")
        reply = ai.ai_reply(prompt="Chào bạn")
        
        # Nếu AI trả về đúng câu phản hồi lỗi mặc định
        if reply == "Xin lỗi, tôi không thể xử lý yêu cầu này lúc này.":
            return "PASSED", reply, None
        return "FAILED", reply, "AI không trả về thông báo lỗi mặc định."

def exec_mock_context():
    """
    Thực thi bài test mô phỏng gửi kèm ngữ cảnh vào prompt gửi đi (Test Case 2).
    """
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
        
        # Lấy tham số thực tế gửi vào hàm chat
        called_args = mock_chat.call_args[1]
        messages = called_args['messages']
        user_content = messages[1]['content']
        
        # Kiểm tra xem có cấu trúc định dạng ngữ cảnh của dự án học tập hay không
        if "Ngữ cảnh tài liệu tham khảo:" in user_content:
            return "PASSED", reply, None
        return "FAILED", reply, "Ngữ cảnh không được định dạng đúng trong Prompt."

def exec_rag_real(case, embed_model="nomic-embed-text"):
    """
    Thực thi kiểm thử RAG ngoài đời thực (Test Cases 3-12).
    Gửi câu hỏi kèm tài liệu tham khảo gốc ➔ Nhận câu trả lời ➔ Đo độ tương đồng ngữ nghĩa.
    """
    ai = Model_AI(ai_model="qwen2.5:3b")
    if not ai.status_ai:
        return "FAILED", "Mô hình AI chưa sẵn sàng.", 0.0

    # AI trả lời tự động bằng tiếng Việt dựa theo cài đặt gốc của hệ thống
    reply = ai.ai_reply(prompt=case["question"], context=case["context"])
    
    # Sinh vector nhúng cho câu trả lời của AI và câu mẫu kỳ vọng
    res_actual = ollama.embeddings(model=embed_model, prompt=reply)
    res_expected = ollama.embeddings(model=embed_model, prompt=case["expected"])
    
    vec_actual = res_actual.get("embedding", [])
    vec_expected = res_expected.get("embedding", [])
    
    if not vec_actual or not vec_expected:
         return "FAILED", reply, 0.0
         
    # Tính điểm số Cosine
    similarity = tinh_cosine_similarity(vec_actual, vec_expected)
    percent = similarity * 100
    
    # Tiêu chuẩn thông qua bài test chất lượng AI: Độ trùng khớp ngữ nghĩa từ 75% trở lên
    status = "PASSED" if similarity >= 0.75 else "FAILED"
    return status, reply, percent

def main():
    print(f"\n{BOLD}{CYAN}============================================================={RESET}")
    print(f"{BOLD}{CYAN}🎓 KHỞI CHẠY HỆ THỐNG KIỂM THỬ TỰ ĐỘNG AGENT EDU (CMD VERSION){RESET}")
    print(f"{BOLD}{CYAN}============================================================={RESET}\n")

    # Kiểm tra cổng mạng Ollama
    ollama_ready = is_ollama_running()
    if ollama_ready:
        print(f"📡 Trạng thái dịch vụ AI: {GREEN}OLLAMA ĐANG CHẠY (Sẵn sàng cho RAG Real tests){RESET}")
    else:
        print(f"📡 Trạng thái dịch vụ AI: {YELLOW}OLLAMA CHƯA BẬT (10 RAG tests thực tế sẽ tự động BỎ QUA){RESET}")

    passed_count = 0
    failed_count = 0
    skipped_count = 0
    similarity_scores = []
    
    # Ghi nhận thời điểm bắt đầu test
    start_time = time.time()

    # Duyệt và chạy qua 12 kịch bản
    for t in test_cases:
        print("-" * 70)
        print(f"{BOLD}Bài test #{t['id']}: {t['name']}{RESET}")
        print(f"  - Câu hỏi: {t['question']}")
        print(f"  - Đáp án mẫu: {t['expected']}")
        
        status, reply, score = "SKIPPED", "", None
        
        try:
            if t["type"] == "mock_exception":
                status, reply, _ = exec_mock_exception()
            elif t["type"] == "mock_context":
                status, reply, _ = exec_mock_context()
            elif t["type"] == "rag":
                if ollama_ready:
                    status, reply, score = exec_rag_real(t)
                    if score is not None:
                        similarity_scores.append(score)
                else:
                    status = "SKIPPED"
                    reply = "Bỏ qua vì dịch vụ Ollama cục bộ ngoại tuyến."
        except Exception as e:
            status = "FAILED"
            reply = f"Lỗi thực thi: {e}"

        # Xác định chuỗi trạng thái in ra màn hình
        if status == "PASSED":
            passed_count += 1
            status_str = f"{GREEN}{BOLD}PASSED{RESET}"
            if score is not None:
                status_str += f" (Khớp {score:.1f}%)"
        elif status == "FAILED":
            failed_count += 1
            status_str = f"{RED}{BOLD}FAILED{RESET}"
            if score is not None:
                status_str += f" (Khớp {score:.1f}%)"
        else:
            skipped_count += 1
            status_str = f"{YELLOW}{BOLD}SKIPPED{RESET}"

        print(f"  - AI trả lời: {reply}")
        print(f"  - Trạng thái: {status_str}")

    elapsed_time = time.time() - start_time
    total = len(test_cases)

    # In kết quả tổng kết trực quan
    print(f"\n{BOLD}{CYAN}============================================================={RESET}")
    print(f"{BOLD}{CYAN}📊 BẢNG TỔNG HỢP CHỈ SỐ KIỂM THỬ CUỐI CÙNG (SUMMARY METRICS){RESET}")
    print(f"{BOLD}{CYAN}============================================================={RESET}")
    print(f"- Tổng số bài test đã chạy: {total}")
    print(f"- Thành công (Passed)     : {GREEN}{passed_count}/{total}{RESET}")
    print(f"- Thất bại (Failed)       : {RED}{failed_count}/{total}{RESET}")
    print(f"- Bỏ qua (Skipped)        : {YELLOW}{skipped_count}/{total}{RESET}")
    print(f"- Thời gian thực hiện     : {elapsed_time:.1f} giây")
    
    # In chỉ số tương đồng ngữ nghĩa của AI
    if similarity_scores:
        avg_sim = sum(similarity_scores) / len(similarity_scores)
        min_sim = min(similarity_scores)
        max_sim = max(similarity_scores)
        print(f"\n{BOLD}🤖 CHỈ SỐ CHẤT LƯỢNG NGỮ NGHĨA AI (10 RAG):{RESET}")
        print(f"  + Độ khớp trung bình   : {GREEN}{avg_sim:.1f}%{RESET}")
        print(f"  + Độ khớp cao nhất     : {GREEN}{max_sim:.1f}%{RESET}")
        print(f"  + Độ khớp thấp nhất    : {YELLOW if min_sim >= 75 else RED}{min_sim:.1f}%{RESET}")
    else:
        print(f"\n{BOLD}🤖 CHỈ SỐ CHẤT LƯỢNG NGỮ NGHĨA AI:{RESET}")
        print("  (Không có dữ liệu thực tế nào được chấm điểm do lỗi hoặc skip)")
        
    print(f"{BOLD}{CYAN}============================================================={RESET}\n")

    # Trả về mã lỗi cho CI/CD pipeline
    if failed_count > 0:
        sys.exit(1)  # Thoát với mã lỗi 1 để báo hệ thống CI/CD ngừng tích hợp
    sys.exit(0)      # Thoát với mã lỗi 0 báo hiệu tất cả bài test đều thông qua hoàn hảo

if __name__ == "__main__":
    main()
