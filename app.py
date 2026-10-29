from pathlib import Path
import hashlib, subprocess, sys
import pandas as pd
import streamlit as st
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from get_embedding_function import get_embedding_function

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'; CHROMA=ROOT/'chroma'; MATRIX=ROOT/'research_gap_matrix.xlsx'
DATA.mkdir(exist_ok=True)
st.set_page_config(page_title='Agen RAG Research Gap', page_icon='📚', layout='wide')
st.title('📚 Agen RAG — Literature & Research Gap')
st.caption('Ollama + ChromaDB lokal. Verifikasi semua hasil AI terhadap artikel asli.')
with st.sidebar:
    st.header('Konfigurasi')
    llm_model=st.text_input('Model LLM','mistral')
    top_k=st.slider('Jumlah potongan konteks',1,10,5)
    st.info('Pastikan Ollama berjalan dan model sudah diunduh.')
tab1,tab2,tab3,tab4=st.tabs(['📄 Artikel PDF','🔎 Tanya RAG','📊 Matriks Research Gap','🧪 Status'])
with tab1:
    uploads=st.file_uploader('Unggah PDF artikel',type=['pdf'],accept_multiple_files=True)
    if st.button('Simpan PDF'):
        saved=0; duplicates=[]
        current={hashlib.sha256(p.read_bytes()).hexdigest():p.name for p in DATA.glob('*.pdf')}
        for item in uploads or []:
            content=item.getvalue(); digest=hashlib.sha256(content).hexdigest()
            if digest in current: duplicates.append(item.name); continue
            target=DATA/Path(item.name).name
            target.write_bytes(content); current[digest]=target.name; saved+=1
        st.success(f'{saved} PDF disimpan.')
        if duplicates: st.warning('File identik dilewati: '+', '.join(duplicates))
    pdfs=sorted(DATA.glob('*.pdf'))
    st.write(f'Jumlah PDF: **{len(pdfs)}**')
    if pdfs:
        st.dataframe(pd.DataFrame([{'Nama file':p.name,'Ukuran KB':round(p.stat().st_size/1024,1),'SHA-256':hashlib.sha256(p.read_bytes()).hexdigest()[:16]} for p in pdfs]),width="stretch")
    c1,c2=st.columns(2)
    with c1:
        if st.button('Bangun/perbarui indeks Chroma'):
            result=subprocess.run([sys.executable,str(ROOT/'populate_database.py')],cwd=ROOT,capture_output=True,text=True)
            st.code(result.stdout or '(tidak ada keluaran)')
            if result.returncode: st.error(result.stderr)
            else: st.success('Pengindeksan selesai.')
    with c2:
        if st.button('Analisis PDF ke Excel'):
            result=subprocess.run([sys.executable,str(ROOT/'research_gap_matrix.py')],cwd=ROOT,capture_output=True,text=True)
            st.code(result.stdout or '(tidak ada keluaran)')
            if result.returncode: st.error(result.stderr)
            else: st.success('Matriks selesai dibuat.')
with tab2:
    question=st.text_area('Pertanyaan','Apa metode, temuan, keterbatasan, dan peluang penelitian dari artikel?')
    if st.button('Cari jawaban',type='primary'):
        try:
            if not CHROMA.exists(): raise RuntimeError('Indeks belum ada. Bangun indeks di tab Artikel PDF.')
            db=Chroma(persist_directory=str(CHROMA),embedding_function=get_embedding_function())
            docs=db.similarity_search_with_score(question,k=top_k)
            if not docs: st.warning('Tidak ditemukan konteks yang relevan.')
            else:
                context='\n\n---\n\n'.join(f"Sumber: {d.metadata.get('source','?')} | halaman: {int(d.metadata.get('page',0))+1}\n{d.page_content}" for d,s in docs)
                prompt=f"Jawab bahasa Indonesia hanya berdasarkan konteks. Jika bukti tidak ada, katakan tidak ditemukan. Jangan mengarang. Sertakan sumber dan halaman.\n\nKONTEKS:\n{context}\n\nPERTANYAAN: {question}"
                answer=ChatOllama(model=llm_model,temperature=0).invoke(prompt).content
                st.subheader('Jawaban'); st.write(answer); st.subheader('Sumber yang diambil')
                for d,score in docs:
                    with st.expander(f"{d.metadata.get('source','?')} · halaman {int(d.metadata.get('page',0))+1} · distance {score:.4f}"): st.write(d.page_content)
        except Exception as exc: st.error(str(exc))
with tab3:
    if MATRIX.exists():
        df=pd.read_excel(MATRIX).fillna(''); st.metric('Artikel dalam matriks',len(df)); st.dataframe(df,width="stretch",height=500)
        st.download_button('Unduh Excel',MATRIX.read_bytes(),file_name=MATRIX.name,mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else: st.info('Matriks belum dibuat. Jalankan analisis PDF di tab Artikel PDF.')
with tab4:
    pdfs=list(DATA.glob('*.pdf'))
    checks=[{'Komponen':'Folder data','Status':'OK' if DATA.exists() else 'Belum ada','Detail':str(DATA)}, {'Komponen':'PDF','Status':'OK' if pdfs else 'Belum ada','Detail':f'{len(pdfs)} file'}, {'Komponen':'Chroma','Status':'OK' if CHROMA.exists() and any(CHROMA.iterdir()) else 'Belum dibuat','Detail':str(CHROMA)}, {'Komponen':'Matriks Excel','Status':'OK' if MATRIX.exists() else 'Belum dibuat','Detail':str(MATRIX)}]
    st.dataframe(pd.DataFrame(checks),width="stretch")
    st.warning('Ini pemeriksaan status file, bukan evaluasi ilmiah kualitas retrieval. Evaluasi tesis perlu pertanyaan berlabel dan penilaian manusia.')
st.divider(); st.caption('Kandidat Research Gap adalah hipotesis awal. Verifikasi DOI, metode, temuan, keterbatasan, dan nomor halaman dari artikel asli.')
