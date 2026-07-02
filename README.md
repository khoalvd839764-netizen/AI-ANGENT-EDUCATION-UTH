# Agent Education - Trợ lý học tập AI với RAG

Agent Education là ứng dụng trợ lý học tập AI chạy local cho người dùng tiếng Việt.
Dự án kết hợp giao diện Tkinter, xử lý PDF, RAG (Retrieval-Augmented Generation), ChromaDB và Ollama để hỗ trợ hỏi đáp dựa trên tài liệu học tập.

## Mô tả ngắn cho GitHub About

1. Trợ lý học tập AI tiếng Việt sử dụng Tkinter + Ollama + ChromaDB cho hỏi đáp theo file PDF.
2. Ứng dụng RAG chạy local: upload PDF, đặt câu hỏi bằng tiếng Việt, và đánh giá chất lượng câu trả lời AI.
3. Agent Education: desktop AI tutor có đăng nhập, nạp tài liệu PDF, semantic chunking và tìm kiếm vector bằng Chroma.

## Tính năng chính

- Xác thực người dùng bằng SQLite local (đăng ký/đăng nhập).
- Tải lên file PDF và trích xuất văn bản bằng pdfplumber.
- Cắt nhỏ văn bản theo ngữ nghĩa (semantic chunking) để tăng độ chính xác truy vấn.
- Tạo embedding bằng Ollama (nomic-embed-text) và lưu vector vào ChromaDB.
- Trợ lý chat ưu tiên sử dụng ngữ cảnh tài liệu (RAG) trước khi trả lời.
- Chế độ phân tích/tóm tắt nội dung tài liệu đã tải lên.
- 2 bộ trình chạy test:
  - Test CMD cho kiểm thử tự động và phù hợp CI/CD.
  - Test GUI để theo dõi kết quả trực quan và đo độ khớp ngữ nghĩa.

## Công nghệ sử dụng

- Python 3.x
- Tkinter (desktop GUI)
- Ollama (LLM local + embedding)
- ChromaDB (vector database)
- pdfplumber (đọc văn bản từ PDF)
- SQLite (lưu tài khoản local)

## Cấu trúc dự án

```text
.
|- app.py                       # Ứng dụng giao diện chính (đăng nhập + chat + upload + phân tích)
|- chay_test_cmd.py             # Trình chạy test dòng lệnh
|- chay_test_gui.py             # Trình chạy test giao diện
|- backend/
|  |- Model_ai.py               # Quản lý model Ollama và gọi chat
|  |- Rag.py                    # Pipeline RAG và kết nối ChromaDB
|  |- file_processor.py         # Trích xuất văn bản từ PDF
|  |- baomat.py                 # Logic đăng nhập/đăng ký
|  |- ketnoi_data.py            # Khởi tạo và kết nối SQLite
|- database/
|  |- agent_edu.db              # CSDL tài khoản local (tự động tạo)
|  |- chroma_db/                # Lưu trữ vector chính
|  |- test_chroma_db/           # Lưu trữ vector phục vụ test
|- giai_thich_chi_tiet_tung_file/
|  |- README.md                 # Tài liệu giải thích chi tiết từng file mã nguồn
```

## Yêu cầu trước khi chạy

Cần có:

- Python 3.10+ (khuyến nghị)
- Ollama đã cài đặt và đang chạy local
- Đã có hoặc cho phép auto-pull các model:
  - qwen2.5:3b
  - nomic-embed-text

## Cài đặt thư viện

```bash
pip install pillow pdfplumber chromadb ollama
```

## Chạy ứng dụng

```bash
python app.py
```

## Chạy kiểm thử

Test CMD:

```bash
python chay_test_cmd.py
```

Test GUI:

```bash
python chay_test_gui.py
```

Lưu ý:

- Nếu Ollama chưa bật, các bài test RAG thực tế sẽ bị skip và chỉ chạy mock test.
- Test CMD trả về exit code 1 nếu có bài test thất bại, phù hợp tích hợp CI/CD.

## Luồng sử dụng cơ bản

1. Đăng ký hoặc đăng nhập tài khoản.
2. Tải file PDF tài liệu học tập.
3. Hệ thống trích xuất text, cắt chunk theo ngữ nghĩa, tạo embedding và lưu vào ChromaDB.
4. Đặt câu hỏi; trợ lý truy xuất các chunk liên quan và trả lời bằng tiếng Việt.
5. Có thể yêu cầu AI phân tích/tóm tắt tài liệu.

## Ghi chú bảo mật

- Hiện tại mật khẩu đang được lưu dạng plain text trong SQLite.
- Nếu đưa vào môi trường thực tế, nên bổ sung hash mật khẩu (ví dụ bcrypt) và tăng cường kiểm soát bảo mật.

## Tài liệu bổ sung

Xem giải thích chi tiết từng file tại:

- giai_thich_chi_tiet_tung_file/README.md
