# Search logic for the PDF RAG bot
import os
import numpy as np
from embed import model, embed_chunks

def search_chunks(query, chunks, top_k=5):
    query_embedding = model.encode([query], convert_to_tensor=False, normalize_embeddings=True)[0]
    similarities = [np.dot(query_embedding, chunk['embedding']) for chunk in chunks]
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    results = []
    for i in top_indices:
        result = chunks[i].copy()
        result['score'] = float(similarities[i])
        results.append(result)
    return results

if __name__ == "__main__":
    from extract import extract_all_pdfs, directory
    from chunk import chunk_all_pages
    from embed import embed_chunks

    # Extract and chunk the PDFs
    pages = extract_all_pdfs(directory)
    chunks = chunk_all_pages(pages)
    chunks = embed_chunks(chunks)

    # Example search query
    query = "What is the Bristol Local Plan Review about?"
    results = search_chunks(query, chunks, top_k=3)
    
    print(f"Top {len(results)} results for query: '{query}'")
    for i, result in enumerate(results):
        print(f"Result {i+1} — {result['filename']} p{result['page_number']} (score: {result['score']:.3f})")
        print(result['text'][:200])
        print("---")