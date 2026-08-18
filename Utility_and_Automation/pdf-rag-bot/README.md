# PDF RAG Bot

A retrieval-augmented generation (RAG) chatbot that answers questions about a folder of PDF documents, built from scratch in raw Python (no LangChain/LlamaIndex) to understand the full RAG pipeline end to end.

Ask a question in the Streamlit UI, and the bot retrieves the most relevant passages from your PDFs, sends them to Claude as grounding context, and returns an answer with citations back to the source file and page.

## How it works

```
PDFs (data/) 
   │
   ▼
extract.py    → pulls text from every page, tracks filename + page number
   │
   ▼
chunk.py      → splits page text into overlapping ~700-char chunks
   │
   ▼
embed.py      → turns each chunk into a 384-dim vector (sentence-transformers, local, offline)
   │
   ▼
search.py     → embeds the user's question, ranks all chunks by cosine similarity
   │
   ▼
Rag_bot.py    → builds a grounded prompt from the top chunks, asks Claude, returns answer + sources
   │
   ▼
UI.py         → Streamlit interface tying it all together
```

The bot is instructed to answer **only** from the retrieved context and to say so explicitly if the answer isn't in the documents — it won't quietly fall back on general knowledge.

## Tech stack

- **PDF parsing:** [pypdf](https://pypdf.readthedocs.io/)
- **Embeddings:** [sentence-transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`), run locally, no API key or cost
- **Vector search:** plain NumPy cosine similarity (no external vector database — small enough dataset that a linear scan is fast and fully transparent)
- **Generation:** [Anthropic Claude API](https://www.anthropic.com/api)
- **UI:** [Streamlit](https://streamlit.io/)

## Project structure

```
pdf-rag-bot/
├── data/           # PDFs to index go here
├── extract.py      # PDF → page-level text
├── chunk.py        # page text → overlapping chunks
├── embed.py        # chunks → embeddings
├── search.py       # cosine similarity search
├── Rag_bot.py       # prompt construction + Claude API call
├── UI.py           # Streamlit app
├── requirements.txt
└── .env            # holds ANTHROPIC_API_KEY (not committed)
```

## Setup

1. Clone the repo and navigate to this folder:
   ```bash
   cd Utility_and_Automation/pdf-rag-bot
   ```

2. Create and activate a virtual environment (Python 3.9–3.11 recommended for broad PyTorch wheel compatibility):
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Add your Anthropic API key. Create a `.env` file in this folder:
   ```
   ANTHROPIC_API_KEY=your-key-here
   ```

5. Drop your PDFs into `data/`.

## Usage

```bash
streamlit run UI.py
```

This opens a browser tab where you can type a question and get an answer grounded in your PDFs, along with the source file, page number, and similarity score for each retrieved passage.

You can also run any stage independently for debugging — e.g. `python search.py` runs extraction, chunking, embedding, and a sample search, printing the top matches to the terminal.

## Design notes

- **Page-level tracking:** every chunk keeps its source filename and page number, so answers can cite exactly where information came from.
- **Overlapping chunks:** a 100-character overlap between consecutive chunks prevents ideas from being cut in half at a chunk boundary.
- **Normalized embeddings:** vectors are L2-normalized at embedding time, so cosine similarity reduces to a simple dot product — faster to compute across thousands of chunks.
- **No vector database:** at this dataset size (a few thousand chunks), a linear NumPy scan is fast enough and keeps the retrieval logic fully visible rather than hidden inside a library.

## Known limitations / possible next steps

- Embeddings are recomputed from scratch on every app restart — no persistence to disk yet.
- No similarity-score threshold — the bot always returns its top-k matches even if none are genuinely relevant (Claude's grounding instructions catch most of this, but a threshold would save API calls on clearly irrelevant questions).
- Scanned/image-only PDFs won't extract any text (no OCR step).
