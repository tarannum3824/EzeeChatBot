# 🤖 EzeeChatBot

A RAG (Retrieval-Augmented Generation) chatbot API built with **FastAPI** and **Google Gemini AI**. Upload any text, webpage, or file (PDF/TXT/DOCX), and the bot answers questions based only on that knowledge — with full conversation history support.

---

## ✨ Features

- **Upload Knowledge** — Feed text, a URL, or upload a file (PDF/TXT/DOCX), and the bot creates a searchable vector store
- **Smart Chat** — Ask questions and get answers strictly from the uploaded content
- **Conversation History** — Server-side chat history maintained per bot, returned with every response
- **Hallucination Prevention** — Relevance scoring + strict system prompt ensures the bot never makes up answers
- **Bot Stats** — Track total messages, average latency, and unanswered questions per bot
- **RAG Pipeline** — Uses FAISS vector search + Gemini LLM for accurate, context-aware answers
- **Web Scraping** — Automatically extracts clean text content from URLs using BeautifulSoup

---

## 🏗️ Project Structure

```
EzeeChatBot/
├── app/
│   ├── api/
│   │   └── routes.py              # API endpoints (upload, upload-file, chat, stats)
│   ├── core/
│   │   └── config.py              # Environment config (API keys)
│   ├── models/
│   │   └── schema.py              # Pydantic request/response models
│   ├── services/
│   │   ├── embedding_service.py   # Google Gemini embedding model
│   │   ├── rag_service.py         # Chat logic with RAG + history + hallucination guard
│   │   ├── stats_service.py       # Bot usage statistics (persistent)
│   │   ├── upload_service.py      # Upload & processing pipeline with validation
│   │   └── vector_store_service.py# FAISS vector store (create/load)
│   ├── utils/
│   │   ├── chunking.py            # Semantic text chunking with LangChain
│   │   └── loader.py              # Text, URL & file content loader with cleaning
│   └── main.py                    # FastAPI app entry point
├── storage/
│   ├── bots/                      # FAISS vector stores per bot
│   └── stats.json                 # Bot usage statistics
├── .env                           # API keys (not committed)
├── .gitignore                     # Git ignore rules
├── requirements.txt               # Python dependencies
└── README.md
```

---

## 🛠️ Tech Stack

| Component       | Technology                          |
|-----------------|-------------------------------------|
| Framework       | FastAPI                             |
| LLM             | Google Gemini 2.5 Flash             |
| Embeddings      | Google Gemini Embedding 001         |
| Vector Store    | FAISS (Facebook AI Similarity Search)|
| Text Splitting  | LangChain RecursiveCharacterTextSplitter |
| Web Scraping    | BeautifulSoup4                      |
| PDF Parsing     | PyPDF2                              |
| DOCX Parsing    | python-docx                         |
| Server          | Uvicorn                             |

---

## 🧠 Design Decisions

### Chunking Strategy

We use **LangChain's `RecursiveCharacterTextSplitter`** with **semantic separators** — not a naive fixed-character split.

```python
SEPARATORS = ["\n\n", "\n", ". ", "? ", "! ", ", ", " "]
```

**Why this approach?**

| Decision | Reasoning |
|----------|-----------|
| **Paragraph-first splitting** (`\n\n`) | Preserves complete ideas and topic boundaries. A paragraph usually contains one coherent thought. |
| **Sentence-level fallback** (`. `, `? `, `! `) | If a paragraph exceeds 500 chars, it splits at sentence boundaries — never mid-sentence. |
| **500 char chunk size** | Balances context richness vs. embedding precision. Too large = diluted embeddings. Too small = lost context. |
| **100 char overlap** | Ensures continuity between chunks. If an answer spans two chunks, the overlap captures the bridge. |
| **Recursive approach** | Tries the most semantic separator first, falls back gracefully. This means chunks respect natural text structure. |

This ensures that when FAISS retrieves the top-3 chunks, each chunk contains a **complete, meaningful unit of information** rather than a randomly sliced fragment.

---

### Hallucination Prevention

The bot uses a **3-layer defense** against hallucination:

**Layer 1 — Relevance Score Filtering:**
```
FAISS returns similarity scores with each chunk.
Chunks with distance score > 1.2 (low relevance) are discarded.
If no chunk passes the threshold → bot refuses to answer.
```

**Layer 2 — Strict System Prompt:**
```
The LLM receives explicit instructions:
- "Answer ONLY using the provided context"
- "Do not guess, assume, or hallucinate any facts"
- "If context is insufficient, say you don't know"
```

**Layer 3 — Temperature 0:**
```
LLM temperature is set to 0 (deterministic output).
This eliminates creative/random responses and keeps
answers grounded in the retrieved context.
```

**Result:** When asked a question not in the uploaded content, the bot responds:
> *"I don't have enough information in the uploaded content to answer this question."*

---

### Error Handling

Every layer has proper error handling:

| Layer | Error | Response |
|-------|-------|----------|
| Upload | No text or URL provided | `400` — "Provide either 'text' or 'url'" |
| Upload | Empty content | `400` — "Uploaded content is empty" |
| Upload | URL fetch fails | `400` — "Failed to load content" |
| File Upload | Unsupported file type | `400` — "Only .pdf, .txt, .docx files are supported" |
| File Upload | Empty/unreadable file | `400` — "File content is empty or unreadable" |
| Chat | Invalid bot_id | `404` — "Bot not found" |
| Chat | Gemini API fails | `502` — "AI model request failed" |
| Stats | Corrupted stats.json | Auto-resets to `{}` |

---

## 🚀 How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/tarannum3824/EzeeChatBot.git
cd EzeeChatBot
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate it:

- **Windows (Git Bash):**
  ```bash
  source venv/Scripts/activate
  ```
- **Windows (CMD):**
  ```cmd
  venv\Scripts\activate
  ```
- **macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up API Key

Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your-gemini-api-key-here
```

### 5. Initialize Storage

```bash
mkdir storage\bots
echo {} > storage/stats.json
```

### 6. Start the Server

```bash
uvicorn app.main:app --reload
```

Server will run at: **http://127.0.0.1:8000**

---

## 📡 API Endpoints

### 1a. Upload Text/URL — `POST /upload`

Upload text or a URL to create a new chatbot knowledge base.

**Request (with text):**
```json
{
  "text": "Tarannum is an AI engineer working at NexaReach in Ahmedabad. She optimized AI costs by 55% using smart caching and model routing."
}
```

**Request (with URL):**
```json
{
  "url": "https://example.com/article"
}
```

**Response:**
```json
{
  "bot_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "chunks_created": 12
}
```

> ⚠️ Save the `bot_id` — you'll need it for chat and stats.

---

### 1b. Upload File — `POST /upload-file`

Upload a PDF, TXT, or DOCX file directly.

**How to test in Swagger UI:**
1. Open **http://127.0.0.1:8000/docs**
2. Click on `/upload-file` → **"Try it out"**
3. Click **"Choose File"** → select your PDF/TXT/DOCX
4. Click **"Execute"**

**How to test in Postman:**
1. Method: `POST`
2. URL: `http://127.0.0.1:8000/upload-file`
3. Body → **form-data**
4. Key: `file` (change type to **File** from the dropdown)
5. Value: Select your PDF/TXT/DOCX file

**How to test with curl:**
```bash
curl -X POST http://127.0.0.1:8000/upload-file \
  -F "file=@/path/to/document.pdf"
```

**Response:**
```json
{
  "bot_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "chunks_created": 24,
  "filename": "document.pdf"
}
```

**Supported file types:** `.pdf`, `.txt`, `.docx`

---

### 2. Chat with Bot — `POST /chat`

Ask questions based on the uploaded knowledge.

**Request:**
```json
{
  "bot_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_message": "Who is Tarannum?"
}
```

**Response:**
```json
{
  "response": "Tarannum is a junior AI engineer working at NexaReach, a fast-growing startup in Ahmedabad.",
  "conversation_history": [
    { "role": "user", "message": "Who is Tarannum?" },
    { "role": "bot", "message": "Tarannum is a junior AI engineer working at NexaReach, a fast-growing startup in Ahmedabad." }
  ]
}
```

**Follow-up question (history is maintained automatically):**
```json
{
  "bot_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_message": "What did she optimize?"
}
```

**Response:**
```json
{
  "response": "She optimized AI costs by 55% by using lightweight models for simple tasks, caching voice scripts, and adding observability.",
  "conversation_history": [
    { "role": "user", "message": "Who is Tarannum?" },
    { "role": "bot", "message": "Tarannum is a junior AI engineer working at NexaReach..." },
    { "role": "user", "message": "What did she optimize?" },
    { "role": "bot", "message": "She optimized AI costs by 55%..." }
  ]
}
```

**Hallucination test (question not in uploaded content):**
```json
{
  "bot_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_message": "What is the capital of France?"
}
```

**Response:**
```json
{
  "response": "I don't have enough information in the uploaded content to answer this question.",
  "conversation_history": [...]
}
```

---

### 3. Get Bot Stats — `GET /stats/{bot_id}`

View usage statistics for a specific bot.

**Request:**
```
GET http://127.0.0.1:8000/stats/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Response:**
```json
{
  "total_messages": 5,
  "avg_latency_ms": 1245.67,
  "unanswered": 1
}
```

---

## 🧪 How to Test (Step by Step)

You can test using **Postman**, **curl**, or the built-in **Swagger UI**.

### Option A: Swagger UI (Easiest)

1. Start the server: `uvicorn app.main:app --reload`
2. Open browser: **http://127.0.0.1:8000/docs**
3. You'll see all 4 endpoints — click any to expand and test

### Option B: Using curl

**Step 1 — Upload content:**
```bash
curl -X POST http://127.0.0.1:8000/upload \
  -H "Content-Type: application/json" \
  -d '{"text": "Tarannum is an AI engineer at NexaReach in Ahmedabad. She reduced AI costs by 55% using smart caching, lightweight models, and observability dashboards."}'
```

**Step 2 — Copy the `bot_id` from response, then chat:**
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"bot_id": "YOUR_BOT_ID_HERE", "user_message": "Who is Tarannum?"}'
```

**Step 3 — Test hallucination prevention (ask something NOT in the content):**
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"bot_id": "YOUR_BOT_ID_HERE", "user_message": "What is the capital of France?"}'
```

Expected: Bot should refuse to answer since this info is not in the uploaded content.

**Step 4 — Test follow-up (conversation history):**
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"bot_id": "YOUR_BOT_ID_HERE", "user_message": "What did she optimize?"}'
```

Expected: Bot uses conversation history to understand "she" refers to Tarannum.

**Step 5 — Upload a file:**
```bash
curl -X POST http://127.0.0.1:8000/upload-file \
  -F "file=@/path/to/document.pdf"
```

**Step 6 — Check stats:**
```bash
curl http://127.0.0.1:8000/stats/YOUR_BOT_ID_HERE
```

### Option C: Using Postman

1. **Upload Text:** POST `http://127.0.0.1:8000/upload` → Body → raw → JSON
2. **Upload File:** POST `http://127.0.0.1:8000/upload-file` → Body → form-data → Key: `file` (type: File)
3. **Chat:** POST `http://127.0.0.1:8000/chat` → Body → raw → JSON
4. **Stats:** GET `http://127.0.0.1:8000/stats/{bot_id}`

> 💡 For text/chat: set Body type to **raw** and format to **JSON**.
> 💡 For file upload: set Body type to **form-data** and key type to **File**.

---

## ⚙️ How It Works

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────┐     ┌───────────┐
│  Upload Text │────▶│ Semantic Chunking │────▶│ Generate Embeddings │────▶│ FAISS DB  │
│  URL or File │     │ (500 chars,      │     │ (Gemini Embedding)  │     │ (stored)  │
│              │     │  paragraph-first) │     │                     │     │           │
└─────────────┘     └──────────────────┘     └─────────────────────┘     └───────────┘

┌─────────────┐     ┌──────────────────┐     ┌─────────────────────┐     ┌───────────┐
│  User Query  │────▶│ FAISS Search     │────▶│ Build Prompt with   │────▶│  Gemini   │
│              │     │ + Relevance      │     │ Context + History   │     │  2.5 Flash│
│              │     │   Score Filter   │     │ + Anti-Hallucination│     │  (temp=0) │
└─────────────┘     └──────────────────┘     └─────────────────────┘     └───────────┘
```

### Pipeline Breakdown:

1. **Upload:**
   - Text/URL/File content is validated and cleaned
   - Split into semantic chunks (paragraph → sentence → word boundaries)
   - Each chunk is embedded using Gemini Embedding model
   - Embeddings stored in FAISS vector database on disk

2. **Chat:**
   - User query is embedded and searched against FAISS (top 3 results)
   - Results are filtered by relevance score (threshold: 1.2)
   - If no relevant chunks found → bot refuses to answer (anti-hallucination)
   - Relevant chunks + conversation history → strict prompt → Gemini generates answer at temperature 0
   - Answer + updated history returned to user

3. **Stats:**
   - Every chat logs latency, success/failure to `stats.json`
   - Unanswered questions tracked separately for quality monitoring

---

## 📝 Notes

- Conversation history is stored **in-memory** (resets on server restart)
- FAISS vector stores are saved to **disk** in `storage/bots/` (persist across restarts)
- The bot answers **only** from uploaded content — it won't make up answers
- Free tier Gemini API has rate limits — if you hit 429 errors, wait a minute or enable billing
- URL scraping removes script/style/nav/footer tags for cleaner text extraction

---

## 📄 License

MIT License — free to use, modify, and distribute.
