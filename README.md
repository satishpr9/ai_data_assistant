<<<<<<< HEAD
=======
# ai_data_assistant(ON GOING PROJECT)
>>>>>>> 6779815cba2606c454a62ab484feb50aa79ff1e6
🧠 AI Data Assistant

An intelligent FastAPI-based backend for conversational analytics over documents and databases.
Supports RAG (Retrieval-Augmented Generation), streaming responses, chart queries, aggregation queries, and conversation history with authentication.
🚀 Features

✅ JWT Authentication (Register / Login / Me)

✅ Conversation Management

✅ Message History Storage

✅ Streaming AI Responses (SSE)

✅ RAG-based Q&A

✅ PDF Upload & Ingestion

✅ MySQL Data Ingestion

✅ Chart Query Detection & Handling

✅ Aggregation Queries

✅ SQLite / MySQL Support

✅ CORS Enabled for Frontend

✅ Secure User-Scoped Conversations

🏗️ Tech Stack

FastAPI

SQLAlchemy ORM

SQLite / MySQL

JWT Authentication

StreamingResponse (SSE)

Python 3.10+

Vector Search / RAG Pipeline

LLM Integration



⚙️ Setup Instructions
1️⃣ Clone Repository
git clone https://github.com/your-username/ai-data-assistant.git
cd ai-data-assistant

2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate     # Linux / Mac
venv\Scripts\activate        # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Environment Variables

Create a .env file:

DATABASE_URL=sqlite:///./ai_assistant.db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

5️⃣ Run the Server
uvicorn app.main:app --reload


Server runs at:

http://localhost:8000


Swagger UI:

http://localhost:8000/docs

🔐 Authentication Flow

Register → /auth/register

Login → /auth/login

Receive JWT token

Pass token in headers:

Authorization: Bearer <token>

💬 Conversations API
➤ Create Conversation
POST /conversations

➤ Get Conversations
GET /conversations

➤ Get Conversation with Messages
GET /conversations/{conversation_id}

➤ Delete Conversation
DELETE /conversations/{conversation_id}

🤖 Ask Questions (Streaming)
POST /ask/stream?conversation_id=1


Uses Server-Sent Events for token streaming.

📊 Query Modes

The assistant auto-detects:

Mode	Description
rag	Document QA
chart	Chart data generation
aggregation	SQL / analytics queries
📄 Upload PDF
POST /upload


Uploads and ingests PDF for RAG.

🗄️ Ingest MySQL
POST /ingest/mysql


Loads business data into analytics engine.

🧪 Health Check
GET /health

🛑 Common Pitfalls
❗ Reserved SQLAlchemy Names

Do NOT use metadata as a column name.
Use meta instead.

❗ Always Convert ORM → Dict in Responses

Never return raw SQLAlchemy objects to FastAPI.

🎨 AI Data Assistant — Frontend

A modern web interface for the AI Data Assistant platform.
This frontend connects to the FastAPI backend to provide:

Conversational analytics

Streaming AI responses

Chart visualizations

Conversation history

Authentication

PDF uploads

Data ingestion controls

Built for speed, clarity, and real-time interaction.

🚀 Features

✅ User Authentication (JWT)

✅ Conversation Sidebar

✅ Live Streaming Responses (SSE)

✅ Chart Rendering

✅ Aggregation Results

✅ Conversation History

✅ PDF Upload UI

✅ MySQL Ingestion Trigger

✅ Responsive Layout

✅ CORS-enabled API Calls

🏗️ Tech Stack

React + Vite

TypeScript / JavaScript

Axios / Fetch

Tailwind CSS

Chart.js / Recharts / ECharts

Server-Sent Events (SSE)

JWT Auth

React Router
⚙️ Setup Instructions
1️⃣ Clone Repository

2️⃣ Install Dependencies
npm install
# or
yarn install

3️⃣ Environment Variables

Create a .env file:

VITE_API_BASE_URL=http://localhost:8000

4️⃣ Run Development Server
npm run dev


Frontend runs at:

http://localhost:5173

🔌 Backend Connection

Make sure backend is running:

http://localhost:8000


CORS must allow:

http://localhost:5173

🔐 Authentication

After login/register, JWT is stored in:

localStorage OR

memory state (recommended)

Every API call includes:

Authorization: Bearer <token>

💬 Chat Flow

User enters question

Frontend calls /ask/stream

SSE stream displays tokens live

Final message saved in history

Sidebar refreshes conversation list

📊 Chart Rendering

When backend returns:

{
  "mode": "chart",
  "chart": {...}
}


Frontend renders using chart library.

📄 Upload PDF

Endpoint:

POST /upload


Used for RAG ingestion.

🧪 Health Check
GET /health

🛑 Common Issues
❗ CORS Error

Ensure backend CORS includes:

http://localhost:5173

❗ SSE Not Streaming

Use fetch EventSource

Disable proxy buffering

Check reverse proxy config (Nginx)

❗ 401 Unauthorized

Token expired

Missing Authorization header

User logged out

