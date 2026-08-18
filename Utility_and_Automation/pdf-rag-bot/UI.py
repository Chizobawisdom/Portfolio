import streamlit as st
from extract import extract_all_pdfs, directory
from chunk import chunk_all_pages
from embed import embed_chunks
from Rag_bot import ask_claude

st.title("PDF RAG Bot")

@st.cache_resource
def load_chunks():
    pages = extract_all_pdfs(directory)
    chunks = chunk_all_pages(pages)
    chunks = embed_chunks(chunks)
    return chunks

chunks = load_chunks()
st.success("PDFs loaded and processed successfully!")

query = st.text_input("Enter your question about the PDFs:")

if query:
    with st.spinner("Searching for answers..."):
        answer, sources = ask_claude(query, chunks, top_k=3)

    st.subheader("Answer:")
    st.write(answer)

    st.subheader("Sources used:")
    for s in sources:
        st.write(f"- {s['filename']}, page {s['page_number']} (score: {s['score']:.3f})")