import os
from dotenv import load_dotenv
from anthropic import Anthropic
from search import search_chunks

load_dotenv()
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def build_prompt(query, retrieved_chunks):
    context = "\n\n".join([
        f"[Source: {c['filename']}, page {c['page_number']}]\n{c['text']}"
        for c in retrieved_chunks
    ])

    prompt = f"""Answer the following question using only the information in the context below. Do not use outside knowledge.

When you use information from the context, mention which source it came from (filename and page number).

If the context does not contain enough information to answer the question, respond exactly with: "I don't have enough information in the provided documents to answer this."

Context:
{context}

Question: {query}

Answer:"""
    return prompt

def ask_claude(query, chunks, top_k=5):
    retrieved_chunks = search_chunks(query, chunks, top_k=top_k)
    prompt = build_prompt(query, retrieved_chunks)

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text, retrieved_chunks

if __name__ == "__main__":
    from extract import extract_all_pdfs, directory
    from chunk import chunk_all_pages
    from embed import embed_chunks

    pages = extract_all_pdfs(directory)
    chunks = chunk_all_pages(pages)
    chunks = embed_chunks(chunks)

    query = "What is the Bristol Local Plan Review about?"
    answer, sources = ask_claude(query, chunks, top_k=3)

    print("Answer:", answer)
    print("\nSources used:")
    for s in sources:
        print(f"- {s['filename']}, page {s['page_number']} (score: {s['score']:.3f})")