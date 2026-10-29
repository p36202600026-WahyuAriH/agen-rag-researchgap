# Agen RAG Research Gap v2 — Streamlit Compatibility Update (Windows)

Aplikasi RAG lokal untuk mengindeks artikel PDF, tanya jawab berbasis sumber, membuat matriks Research Gap ke Excel, dan memeriksa status komponen. Stack: Streamlit, Ollama, ChromaDB, LangChain, dan nomic-embed-text.

## Kebutuhan
- Windows 10/11
- Python 3.10 atau lebih baru (disarankan Python 3.12/3.13 yang kompatibel dengan dependensi)
- Ollama terpasang dan berjalan
- Ruang disk untuk model Ollama dan indeks Chroma

## Instalasi pertama kali (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
ollama pull nomic-embed-text
ollama pull mistral
```
Jika aktivasi diblokir:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```
Instal Ollama dari situs resminya: https://ollama.com/download/windows

## Menjalankan dashboard
```powershell
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```
Buka `http://localhost:8501`.

Alternatif: jalankan `run_app.bat` setelah instalasi selesai.

## Alur penggunaan
1. Buka tab **Artikel PDF** dan unggah PDF atau salin PDF ke folder `data`.
2. Klik **Bangun/perbarui indeks Chroma** untuk menyiapkan pencarian RAG.
3. Buka tab **Tanya RAG** untuk bertanya berdasarkan artikel yang sudah diindeks.
4. Klik **Analisis PDF ke Excel** untuk menghasilkan `research_gap_matrix.xlsx`.
5. Buka tab **Matriks Research Gap** untuk memeriksa dan mengunduh hasil.

## Perintah CLI
```powershell
python populate_database.py
python query_data.py "Apa metode penelitian yang digunakan dalam artikel?"
python research_gap_matrix.py
```
Gunakan `python populate_database.py --reset` hanya jika memang ingin membangun ulang indeks. Perintah tersebut dapat menghapus indeks Chroma yang lama.

## Pembaruan kompatibilitas
- Mengganti parameter Streamlit `use_container_width=True` menjadi `width="stretch"`.
- Mengganti `use_container_width=False` menjadi `width="content"` jika ditemukan.
- Memperbarui syarat dependensi menjadi `streamlit>=1.50.0`.
- Menghapus berkas cache `__pycache__` dari paket distribusi.

## Catatan penting
- Ollama harus aktif dan model yang dipakai harus sudah diunduh. Dashboard default menggunakan model `mistral`.
- Model embedding harus konsisten saat indexing dan query. Jika sebelumnya menggunakan embedding model lain, bangun ulang indeks dengan prosedur reset yang sesuai.
- PDF hasil scan yang tidak memiliki lapisan teks memerlukan OCR sebelum dianalisis.
- Deteksi duplikasi hanya memeriksa file PDF yang identik byte-per-byte, bukan artikel sama dengan format PDF berbeda.
- Kandidat research gap yang dihasilkan AI adalah hipotesis awal. Verifikasi DOI, metode, temuan, keterbatasan, dan halaman bukti terhadap artikel asli.
- Status dashboard adalah pemeriksaan file, bukan evaluasi ilmiah kualitas retrieval. Evaluasi penelitian memerlukan pertanyaan uji berlabel, ground truth, dan penilaian manusia.
