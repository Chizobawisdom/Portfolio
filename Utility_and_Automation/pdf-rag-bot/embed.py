# Embedding the chunks using a pre-trained model
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_chunks(chunks):
    texts = [chunk['text'] for chunk in chunks]
    embeddings = model.encode(texts, convert_to_tensor=False, normalize_embeddings=True)
    for i, chunk in enumerate(chunks):
        chunk['embedding'] = embeddings[i]
    return chunks

if __name__ == "__main__":
    # Quick sanity check with known similar/dissimilar sentences
    test_chunks = [{"text": "The cat sat on the mat."}, {"text": "A feline rested on the rug."}, {"text": "Quarterly revenue increased by 12%."}]
    result = embed_chunks(test_chunks)
    sim_similar = np.dot(result[0]['embedding'], result[1]['embedding'])
    sim_different = np.dot(result[0]['embedding'], result[2]['embedding'])
    print(f"Sanity check — similar: {sim_similar:.3f}, different: {sim_different:.3f}")

    # Real pipeline run
    from extract import extract_all_pdfs, directory
    from chunk import chunk_all_pages

    pages = extract_all_pdfs(directory)
    chunks = chunk_all_pages(pages)
    chunks = embed_chunks(chunks)
    print(f"Embedded {len(chunks)} chunks")