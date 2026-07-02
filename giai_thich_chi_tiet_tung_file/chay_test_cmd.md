# Giải thích chi tiết: chay_test_cmd.py

Tệp tin này là **phiên bản dòng lệnh (CMD/CLI Test Runner)** của bộ kiểm thử tự động, phục vụ trực tiếp cho mục đích tự động hóa lập trình.

## ⚙️ Cơ chế hoạt động:
1. **Chạy không cần giao diện:** Chạy hoàn toàn trên cửa sổ Terminal/Command Prompt bằng cách duyệt qua 12 bài test tương tự như bản GUI.
2. **Hỗ trợ màu sắc ANSI:** Sử dụng mã màu đặc biệt (`\033[92m` cho màu xanh lá, `\033[91m` cho màu đỏ) để tô màu kết quả in trực tiếp ra Terminal, giúp lập trình viên dễ dàng quan sát trạng thái test.
3. **Báo cáo tóm tắt:** In bảng tóm tắt chỉ số chất lượng AI (Thời gian thực thi, điểm trung bình, max, min) ngay dưới dòng lệnh khi chạy xong.
4. **Trả về Exit Code cho CI/CD:** 
   - Lệnh `sys.exit(0)` sẽ được gọi nếu tất cả bài test vượt qua (Passed).
   - Lệnh `sys.exit(1)` sẽ được gọi nếu có bất kỳ bài test nào bị lỗi hoặc thất bại.
   - Việc trả về mã thoát này là tiêu chuẩn bắt buộc để các công cụ tự động hóa như GitHub Actions hoặc Jenkins nhận biết bản cập nhật phần mềm có đạt chất lượng để phát hành hay không.
