''' Chunking logic for splitting extracted text into manageable pieces '''
import os
from typing import List, Dict


def chunk_txt(text, chunk_size=700, overlap=100) -> List[str]:
    if overlap >= chunk_size:
                raise ValueError("overlap must be smaller than chunk_size")
    chunks = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def chunk_all_pages(pages) -> List[Dict]:
    all_chunks = []
    for page in pages:
        text = page['text']
        chunks = chunk_txt(text)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                'chunk_id': f"{page['filename']}_p{page['page_number']}_c{i+1}",
                'filename': page['filename'],
                'page_number': page['page_number'],
                'chunk_number': i + 1,
                'text': chunk
            })
    return all_chunks

if __name__ == "__main__":
    from extract import extract_all_pdfs, directory
    pages = extract_all_pdfs(directory)
    chunks = chunk_all_pages(pages)
    print(f"Total chunks: {len(chunks)}")
    print(chunks[0])
    print(chunks[1]['text'][:100])  