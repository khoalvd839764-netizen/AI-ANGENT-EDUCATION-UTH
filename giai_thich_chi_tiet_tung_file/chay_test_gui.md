# Giải thích chi tiết: chay_test_gui.py

Tệp tin này đóng vai trò là **Trình kiểm thử tự động có giao diện đồ họa (GUI Test Runner)** dùng để chạy thử nghiệm và kiểm chứng chất lượng câu trả lời của AI.

## ⚙️ Cơ chế hoạt động:
1. **Thiết kế giao diện tối (Dark Mode):** Xây dựng một cửa sổ Tkinter hiển thị danh sách 12 thẻ (Cards) đại diện cho 12 bài test.
2. **2 bài test Mock đầu tiên (Offline):** Hệ thống giả lập các tình huống mất kết nối Ollama (Câu 1) và định dạng prompt (Câu 2) bằng cách dùng thư viện `unittest.mock`. Điều này giúp kiểm tra tính an toàn của code mà không phụ thuộc vào AI chạy cục bộ.
3. **10 bài test RAG thực tế:** Hệ thống gửi lần lượt 10 câu hỏi tiếng Việt dựa trên sách dữ liệu gốc, nhận câu trả lời thực tế từ mô hình AI `qwen2.5:3b`.
4. **Đo đạc độ tương đồng ngữ nghĩa:**
   - Hệ thống gọi mô hình nhúng `nomic-embed-text` để biến câu trả lời của AI và đáp án mẫu thành 2 vector đặc trưng.
   - Tính góc Cosine giữa 2 vector đó để ra phần trăm trùng khớp ngữ nghĩa.
   - Nếu độ khớp >= 75%, thẻ bài test chuyển màu xanh lá cây báo **ĐẠT (PASSED)**. Ngược lại chuyển màu đỏ báo **THẤT BẠI (FAILED)**.
5. **Hiển thị bảng thống kê cuối cùng:** Kết thúc tiến trình kiểm thử, hệ thống đo lường tổng thời gian chạy thực tế và tính toán điểm tương đồng trung bình, điểm cao nhất, điểm thấp nhất rồi hiển thị dạng hộp thoại thông báo Pop-up để lập trình viên tham khảo chất lượng AI.
