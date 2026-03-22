# 🤖 EzeeChatBot

A RAG (Retrieval-Augmented Generation) chatbot API built with **FastAPI** and **Google Gemini AI**. Upload any text or webpage content, and the bot answers questions based only on that knowledge — with full conversation history support.

---

## ✨ Features

- **Upload Knowledge** — Feed text or a URL, and the bot creates a searchable vector store
- **Smart Chat** — Ask questions and get answers strictly from the uploaded content
- **Conversation History** — Server-side chat history maintained per bot, returned with every response
- **Bot Stats** — Track total messages, average latency, and unanswered questions per bot
- **RAG Pipeline** — Uses FAISS vector search + Gemini LLM for accurate, context-aware answers
- **Web Scraping** — Automatically extracts text content from URLs using BeautifulSoup

---

## 🏗️ Project Structure

```
EzeeChatBot/
├── app/
│   ├── api/
│   │   └── routes.py              # API endpoints (upload, chat, stats)
│   ├── core/
│   │   └── config.py              # Environment config (API keys)
│   ├── models/
│   │   └── schema.py              # Pydantic request models
│   ├── services/
│   │   ├── embedding_service.py   # Google Gemini embedding model
│   │   ├── rag_service.py         # Chat logic with RAG + history
│   │   ├── stats_service.py       # Bot usage statistics
│   │   ├── upload_service.py      # Upload & processing pipeline
│   │   └── vector_store_service.py# FAISS vector store (create/load)
│   ├── utils/
│   │   ├── chunking.py            # Text chunking with LangChain
│   │   └── loader.py              # Text & URL content loader
│   └── main.py                    # FastAPI app entry point
├── storage/
│   ├── bots/                      # FAISS vector stores per bot
│   └── stats.json                 # Bot usage statistics
├── .env                           # API keys (not committed)
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
| Server          | Uvicorn                             |

---

## 🚀 How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/EzeeChatBot.git
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

### 5. Initialize Stats File

```bash
echo {} > storage/stats.json
```

### 6. Start the Server

```bash
uvicorn app.main:app --reload
```

Server will run at: **http://127.0.0.1:8000**

---

## 📡 API Endpoints

### 1. Upload Knowledge — `POST /upload`

Upload text or a URL to create a new chatbot.

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
  "bot_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

> ⚠️ Save the `bot_id` — you'll need it for chat and stats.

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
  "unanswered": 0
}
```

---

## 🧪 How to Test (Step by Step)

You can test using **Postman**, **curl**, or the built-in **Swagger UI**.

### Option A: Swagger UI (Easiest)

1. Start the server: `uvicorn app.main:app --reload`
2. Open browser: **http://127.0.0.1:8000/docs**
3. You'll see all 3 endpoints — click any to expand and test

### Option B: Using curl

**Step 1 — Upload content:**
```bash
curl -X POST http://127.0.0.1:8000/upload \
  -H "Content-Type: application/json" \
  -d '{"text": "Tarannum is an AI engineer at NexaReach. She reduced AI costs by 55%."}'
```

**Step 2 — Copy the `bot_id` from response, then chat:**
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"bot_id": "YOUR_BOT_ID_HERE", "user_message": "Who is Tarannum?"}'
```

**Step 3 — Check stats:**
```bash
curl http://127.0.0.1:8000/stats/YOUR_BOT_ID_HERE
```

### Option C: Using Postman

1. **Upload:** POST `http://127.0.0.1:8000/upload` → Body → raw → JSON
2. **Chat:** POST `http://127.0.0.1:8000/chat` → Body → raw → JSON
3. **Stats:** GET `http://127.0.0.1:8000/stats/{bot_id}`

> 💡 Always set Body type to **raw** and format to **JSON** in Postman.

---

## ⚙️ How It Works

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌───────────┐
│  Upload Text │────▶│ Chunk Text   │────▶│ Generate Embeddings │──▶│ FAISS DB  │
│  or URL      │     │ (500 chars)  │     │ (Gemini Embedding)  │  │ (stored)  │
└─────────────┘     └──────────────┘     └─────────────────┘     └───────────┘

┌─────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌───────────┐
│  User Query  │────▶│ FAISS Search │────▶│ Build Prompt with │──▶│  Gemini   │
│              │     │ (top 3 docs) │     │ Context + History │  │  2.5 Flash│
└─────────────┘     └──────────────┘     └─────────────────┘     └───────────┘
```

1. **Upload:** Text is split into chunks → embedded using Gemini → stored in FAISS
2. **Chat:** Query searches FAISS for relevant chunks → builds prompt with context + conversation history → Gemini generates answer
3. **Stats:** Every chat logs latency and success/failure to `stats.json`

---

## 📝 Notes

- Conversation history is stored **in-memory** (resets on server restart)
- FAISS vector stores are saved to disk in `storage/bots/`
- The bot answers **only** from uploaded content — it won't make up answers
- Free tier Gemini API has rate limits — if you hit 429 errors, wait a minute or enable billing

---

## 📄 License

MIT License — free to use, modify, and distribute.
