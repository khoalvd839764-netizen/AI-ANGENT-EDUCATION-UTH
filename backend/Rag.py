# -*- coding: utf-8 -*-
# =========================================================================
# THƯ MỤC: backend
# TÊN FILE: Rag.py
# CHỨC NĂNG CHÍNH: Quản lý RAG (Retrieval-Augmented Generation) thông qua ChromaDB.
#                  Thực hiện đọc tài liệu, Semantic Chunking, lưu vector và truy vấn.
# =========================================================================

import os      # Thư viện hệ thống làm việc với đường dẫn
import sys     # Thư viện hệ thống cấu hình I/O
import io      # Quản lý luồng xuất nhập
import chromadb  # Thư viện Cơ sở dữ liệu Vector cục bộ để lưu và tìm kiếm embeddings
import ollama   # Thư viện kết nối dịch vụ AI cục bộ để tạo embeddings
from backend.file_processor import FileProcessor  # Import lớp đọc PDF
from backend.Model_ai import Model_AI              # Import lớp giao tiếp AI chat

# Cấu hình luồng xuất chuẩn stdout và stderr hỗ trợ tiếng Việt UTF-8 trên Windows
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

class RagChroma:
    """
    Lớp RagChroma đóng vai trò quản trị toàn bộ vòng đời của RAG:
    1. Đọc văn bản thô từ PDF.
    2. Cắt nhỏ theo ngữ nghĩa câu/đoạn (Semantic Chunking).
    3. Nhúng (embed) các đoạn văn bản thành Vector số thực.
    4. Quản lý lưu trữ trong ChromaDB cục bộ.
    5. Thực hiện truy vấn và cung cấp ngữ cảnh khớp nhất cho AI khi có câu hỏi.
    """
    def __init__(self, ai_model="qwen2.5:3b"):
        # Khởi tạo đối tượng xử lý file PDF
        self.processor = FileProcessor()
        # Khởi tạo mô hình AI chat
        self.ai = Model_AI(ai_model)
        self.model_name = ai_model
        
        # Mô hình nhúng vector chuyên dụng của Ollama để biến chữ thành vector số thực
        self.embed_model = "nomic-embed-text"
        
        # Xác định thư mục lưu trữ database của ChromaDB
        # Đường dẫn: thư mục gốc dự án / database / chroma_db
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        chroma_path = os.path.join(base_dir, "database", "chroma_db")
        
        # Khởi tạo ChromaDB Client bền vững (lưu dữ liệu trực tiếp xuống ổ đĩa)
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        
        # Lấy hoặc tự động tạo Collection (bảng lưu trữ) tên là "tai_lieu_on_tap"
        self.collection = self.chroma_client.get_or_create_collection(name="tai_lieu_on_tap")

    def _get_embedding(self, text):
        """
        Nhiệm vụ: Gửi một chuỗi ký tự sang Ollama để lấy về Vector biểu diễn ngữ nghĩa.
        
        Tham số:
            text (str): Đoạn văn bản cần nhúng.
            
        Trả về:
            list[float]: Một mảng số thực đại diện cho Vector nhúng (768 chiều).
        """
        try:
            # Gọi thư viện Ollama sinh vector nhúng
            response = ollama.embeddings(model=self.embed_model, prompt=text)
            return response["embedding"]
        except Exception as e:
            print("[Embedding Error] Lỗi khi tạo vector nhúng:", e)
            return []

    def _cat_nho_van_ban(self, text, max_chunk_size=600, min_chunk_size=100):
        """
        Kỹ thuật Semantic Chunking — Cắt nhỏ văn bản tự động theo ranh giới ngữ nghĩa.
        
        Nguyên lý: Thay vì cắt đứt một câu ở giữa chừng dựa trên giới hạn số ký tự,
        hệ thống sẽ ưu tiên ngắt theo thứ tự tự nhiên:
            1. Đoạn văn (ký tự xuống dòng kép \n\n) - Mức ưu tiên 1.
            2. Dấu câu (dấu chấm, chấm hỏi, chấm than, dấu hai chấm) - Mức ưu tiên 2.
            3. Dấu khoảng trắng giữa các từ - Mức ưu tiên 3 (dự phòng khi câu quá dài).
            
        Tham số:
            max_chunk_size (int): Kích thước ký tự tối đa cho 1 chunk (mặc định 600).
            min_chunk_size (int): Kích thước tối thiểu. Chunk nhỏ hơn sẽ được gộp vào chunk trước đó.
            
        Trả về:
            list[str]: Danh sách các đoạn văn bản (chunks) chất lượng cao.
        """
        chunks = []
        current_chunk = ""

        # Hàm bổ trợ: kiểm tra độ dài để lưu chunk hoặc gộp vào chunk liền trước
        def append_or_merge_chunk(chunk_text, separator=" "):
            if not chunk_text.strip():
                return
            if len(chunk_text.strip()) >= min_chunk_size:
                chunks.append(chunk_text.strip())
            else:
                if chunks:
                    # Gộp vào chunk liền trước nếu chunk hiện tại quá ngắn để bảo đảm đủ thông tin ngữ nghĩa
                    chunks[-1] += separator + chunk_text.strip()
                else:
                    chunks.append(chunk_text.strip())

        # Tách văn bản thành các đoạn văn thô dựa trên ký tự xuống dòng kép
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        for paragraph in paragraphs:
            # Nếu đoạn văn vượt quá giới hạn tối đa
            if len(paragraph) > max_chunk_size:
                sentences = []
                temp = ""
                # Duyệt qua từng ký tự trong đoạn văn để tách câu
                for char in paragraph:
                    temp += char
                    # Phát hiện dấu câu kết thúc và độ dài tạm thời lớn hơn 20 ký tự
                    if char in (".", "!", "?", ":") and len(temp) > 20:
                        sentences.append(temp.strip())
                        temp = ""
                if temp.strip():
                    sentences.append(temp.strip())

                for sentence in sentences:
                    # Nếu một câu đơn vẫn dài quá giới hạn tối đa
                    if len(sentence) > max_chunk_size:
                        # Tiến hành tách theo khoảng trắng từ
                        words = sentence.split(" ")
                        for word in words:
                            if len(current_chunk) + len(word) + 1 <= max_chunk_size:
                                current_chunk += (" " if current_chunk else "") + word
                            else:
                                append_or_merge_chunk(current_chunk, separator=" ")
                                current_chunk = word
                    else:
                        # Gộp câu vào chunk hiện tại nếu không vượt quá kích thước tối đa
                        if len(current_chunk) + len(sentence) + 1 <= max_chunk_size:
                            current_chunk += (" " if current_chunk else "") + sentence
                        else:
                            append_or_merge_chunk(current_chunk, separator=" ")
                            current_chunk = sentence
            else:
                # Nếu đoạn văn ngắn, cố gắng gộp vào chunk đang xây dựng
                if len(current_chunk) + len(paragraph) + 2 <= max_chunk_size:
                    current_chunk += ("\n\n" if current_chunk else "") + paragraph
                else:
                    append_or_merge_chunk(current_chunk, separator="\n\n")
                    current_chunk = paragraph

        # Lưu lại phần văn bản cuối cùng còn sót lại
        if current_chunk.strip():
            append_or_merge_chunk(current_chunk, separator="\n\n")

        return chunks

    def add_document_to_db(self, filepath):
        """
        Nhiệm vụ: Quy trình nạp tài liệu PDF vào CSDL Vector ChromaDB.
                  Đọc PDF -> Cắt nhỏ Semantic -> Embedding tạo Vector -> Lưu trữ.
        """
        # Bước 1: Trích xuất toàn bộ văn bản từ file PDF
        text = self.processor.chuyen_file_pdf_to_text(filepath)
        if not text:
            print("[RAG] Không đọc được nội dung hoặc file rỗng.")
            return False
            
        print(f"[RAG] Đang cắt nhỏ tài liệu theo ngữ nghĩa (Semantic Chunking)...")
        # Bước 2: Gọi phương thức cắt văn bản chất lượng cao
        chunks = self._cat_nho_van_ban(text, max_chunk_size=600, min_chunk_size=100)
        print(f"[RAG] Đã chia tài liệu thành {len(chunks)} đoạn nhỏ.")
        
        # ===== [DEBUG] In thông tin chunk ra console phục vụ kiểm chứng =====
        print("\n" + "="*60)
        print(f"[DEBUG CHUNK] DANH SÁCH {len(chunks)} CHUNK SAU KHI CẮT:")
        print("="*60)
        for idx, chunk in enumerate(chunks):
            print(f"\n[CHUNK #{idx+1}] ({len(chunk)} ký tự)")
            print("-" * 40)
            print(chunk)
            print("-" * 40)
        print("="*60 + "\n")
        # ===== END DEBUG =====
        
        # Khởi tạo các danh sách gom dữ liệu gửi sang ChromaDB
        documents = []
        embeddings = []
        metadatas = []
        ids = []
        
        filename = os.path.basename(filepath)
        
        print(f"[RAG] Đang tạo Vector nhúng (Embedding) cho {len(chunks)} chunks...")
        # Bước 3: Duyệt qua từng chunk để nhúng vector
        for i, chunk in enumerate(chunks):
            vector = self._get_embedding(chunk)
            if vector:
                documents.append(chunk)
                embeddings.append(vector)
                metadatas.append({"source": filename})         # Lưu nguồn gốc tài liệu
                ids.append(f"{filename}_chunk_{i}")            # Mã định danh duy nhất cho chunk
                
        # Bước 4: Lưu toàn bộ dữ liệu vào ChromaDB Collection
        if documents:
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            print(f"[RAG] Đã lưu thành công {len(documents)} vectors vào ChromaDB!")
            return True
        return False

    def ask_with_rag(self, question, filename=None, n_results=5):
        """
        Nhiệm vụ: Truy xuất tri thức tài liệu (Retrieval) và tạo câu trả lời (Generation).
                  Hóa vector câu hỏi ➔ Tìm các đoạn tương đồng trong DB ➔ Gộp làm Context ➔ AI trả lời.
        """
        # Đảm bảo hệ thống AI cục bộ đã được kết nối
        if not self.ai.status_ai:
            return "Hệ thống AI chưa sẵn sàng."
            
        # Bước 1: Biến câu hỏi hiện tại thành vector số thực
        query_vector = self._get_embedding(question)
        if not query_vector:
            return "Không thể tạo vector cho câu hỏi."
            
        print(f"[RAG] Đang truy vấn tìm kiếm các đoạn khớp nhất (File lọc: {filename if filename else 'Tất cả'})...")
        
        # Cấu hình bộ lọc theo tài liệu cụ thể nếu học viên chọn một file
        where_filter = {"source": filename} if filename else None
        
        # Bước 2: Thực hiện truy vấn trong ChromaDB
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=n_results,  # Lấy ra tối đa n_results đoạn tương quan nhất
            where=where_filter
        )
        
        # Lấy danh sách tài liệu tương đồng và khoảng cách L2 tương ứng
        matched_docs = results.get("documents", [[]])[0]
        matched_distances = results.get("distances", [[]])[0]
        
        # Bước 3: Đóng gói ngữ cảnh
        if not matched_docs:
            print("[RAG] Không tìm thấy ngữ cảnh phù hợp. AI sẽ trả lời bằng tri thức mặc định.")
            context = ""
        else:
            print(f"[RAG] Đã tìm thấy {len(matched_docs)} đoạn tài liệu tương đồng.")
            
            # ===== [DEBUG] In thông tin khoảng cách L2 của các đoạn trích =====
            print("\n" + "="*60)
            print(f"[DEBUG QUERY] CÁC CHUNK TRUY XUẤT ĐƯỢC:")
            print(f"  > Câu hỏi: '{question}'")
            print("="*60)
            for idx, (doc, dist) in enumerate(zip(matched_docs, matched_distances)):
                print(f"\n[KẾT QUẢ #{idx+1}] Khoảng cách L2: {dist:.4f}")
                print(f"  (Gợi ý: Khoảng cách < 1.0 cực kỳ khớp | 1.0 - 1.5: Khá khớp | > 1.5: Ít khớp)")
                print("-" * 40)
                print(doc)
                print("-" * 40)
            print("="*60 + "\n")
            # ===== END DEBUG =====
            
            # Ghép các khối văn bản tìm thấy bằng vạch phân tách ngang
            context = "\n---\n".join(matched_docs)
            
        # Bước 4: Chuyển toàn bộ ngữ cảnh + câu hỏi sang AI Chatbot sinh câu trả lời tiếng Việt
        print("[RAG] Đang gửi toàn bộ Context và Prompt sang AI...")
        reply = self.ai.ai_reply(prompt=question, context=context)
        return reply
