# Agent Education - Tro ly hoc tap AI voi RAG

Agent Education la ung dung tro ly hoc tap AI chay local cho nguoi dung tieng Viet.
Du an ket hop giao dien Tkinter, xu ly PDF, RAG (Retrieval-Augmented Generation), ChromaDB va Ollama de ho tro hoi dap dua tren tai lieu hoc tap.

## Mo ta ngan cho GitHub About

Ban co the copy 1 trong 3 dong sau vao phan About cua repository:

1. Tro ly hoc tap AI tieng Viet su dung Tkinter + Ollama + ChromaDB cho hoi dap theo file PDF.
2. Ung dung RAG chay local: upload PDF, dat cau hoi bang tieng Viet, va danh gia chat luong cau tra loi AI.
3. Agent Education: desktop AI tutor co dang nhap, nap tai lieu PDF, semantic chunking va tim kiem vector bang Chroma.

## Tinh nang chinh

- Xac thuc nguoi dung bang SQLite local (dang ky/dang nhap).
- Tai len file PDF va trich xuat van ban bang pdfplumber.
- Cat nho van ban theo ngu nghia (semantic chunking) de tang do chinh xac truy van.
- Tao embedding bang Ollama (nomic-embed-text) va luu vector vao ChromaDB.
- Tro ly chat uu tien su dung ngu canh tai lieu (RAG) truoc khi tra loi.
- Che do phan tich/tom tat noi dung tai lieu da tai len.
- 2 bo trinh chay test:
  - Test CMD cho kiem thu tu dong va phu hop CI/CD.
  - Test GUI de theo doi ket qua truc quan va do do khop ngu nghia.

## Cong nghe su dung

- Python 3.x
- Tkinter (desktop GUI)
- Ollama (LLM local + embedding)
- ChromaDB (vector database)
- pdfplumber (doc van ban tu PDF)
- SQLite (luu tai khoan local)

## Cau truc du an

```text
.
|- app.py                       # Ung dung giao dien chinh (dang nhap + chat + upload + phan tich)
|- chay_test_cmd.py             # Trinh chay test dong lenh
|- chay_test_gui.py             # Trinh chay test giao dien
|- backend/
|  |- Model_ai.py               # Quan ly model Ollama va goi chat
|  |- Rag.py                    # Pipeline RAG va ket noi ChromaDB
|  |- file_processor.py         # Trich xuat van ban tu PDF
|  |- baomat.py                 # Logic dang nhap/dang ky
|  |- ketnoi_data.py            # Khoi tao va ket noi SQLite
|- database/
|  |- agent_edu.db              # CSDL tai khoan local (tu dong tao)
|  |- chroma_db/                # Luu tru vector chinh
|  |- test_chroma_db/           # Luu tru vector phuc vu test
|- giai_thich_chi_tiet_tung_file/
|  |- README.md                 # Tai lieu giai thich chi tiet tung file ma nguon
```

## Yeu cau truoc khi chay

Can co:

- Python 3.10+ (khuyen nghi)
- Ollama da cai dat va dang chay local
- Da co hoac cho phep auto-pull cac model:
  - qwen2.5:3b
  - nomic-embed-text

## Cai dat thu vien

```bash
pip install pillow pdfplumber chromadb ollama
```

## Chay ung dung

```bash
python app.py
```

## Chay kiem thu

Test CMD:

```bash
python chay_test_cmd.py
```

Test GUI:

```bash
python chay_test_gui.py
```

Luu y:

- Neu Ollama chua bat, cac bai test RAG thuc te se bi skip va chi chay mock test.
- Test CMD tra ve exit code 1 neu co bai test that bai, phu hop tich hop CI/CD.

## Luong su dung co ban

1. Dang ky hoac dang nhap tai khoan.
2. Tai file PDF tai lieu hoc tap.
3. He thong trich xuat text, cat chunk theo ngu nghia, tao embedding va luu vao ChromaDB.
4. Dat cau hoi; tro ly truy xuat cac chunk lien quan va tra loi bang tieng Viet.
5. Co the yeu cau AI phan tich/tom tat tai lieu.

## Ghi chu bao mat

- Hien tai mat khau dang duoc luu dang plain text trong SQLite.
- Neu dua vao moi truong thuc te, nen bo sung hash mat khau (vi du bcrypt) va tang cuong kiem soat bao mat.

## Tai lieu bo sung

Xem giai thich chi tiet tung file tai:

- giai_thich_chi_tiet_tung_file/README.md
