# 🤖 AI Data Assistant

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-6.0%2B-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.4%2B-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

An intelligent **RAG (Retrieval-Augmented Generation)** Data Assistant that allows users to chat with their data. It supports file ingestion, SQL database connections, and generates visual charts and aggregations on the fly.

---

## ✨ Features

- **📚 Multi-Format Ingestion**: Upload and chat with PDF, TXT, MD, DOCX, CSV, and JSON files.
- **💬 Streaming & RAG**: Real-time streaming responses powered by LangChain and OpenAI.
- **📊 Business Intelligence**: Connects to SQL databases to answer business queries and generate charts.
- **🔐 Secure Authentication**: JWT-based user authentication and role-based access control.
- **💾 Conversation History**: Persists chat history for seamless follow-up questions.
- **🕸️ Modern UI**: A clean, responsive React frontend styled with Tailwind CSS.

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: SQLite (SQLAlchemy ORM)
- **AI/ML**: LangChain, OpenAI API
- **Auth**: Passlib (Bcrypt), PyJWT

### Frontend
- **Framework**: React (Vite)
- **Styling**: Tailwind CSS
- **Visualization**: Chart.js / Recharts
- **Icons**: Lucide React

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- OpenAI API Key

### 1️⃣ Backend Setup

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd ai_data_assistant
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**:
   Create a `.env` file in the root directory and add your keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   SECRET_KEY=your_jwt_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. **Run the server**:
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.
   Swagger Documentation: `http://localhost:8000/docs`.

### 2️⃣ Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd rag-ui
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run the development server**:
   ```bash
   npm run dev
   ```
   The app will run at `http://localhost:5173`.

---

## � Project Structure

```bash
ai_data_assistant/
├── app/                  # Backend Application
│   ├── main.py           # API Entry Point
│   ├── auth.py           # Authentication Logic
│   ├── database.py       # Database Config
│   ├── rag.py            # RAG Implementation
│   ├── vectorstore.py    # Vector Database Logic
│   └── ...
├── rag-ui/               # Frontend Application
│   ├── src/              # React Source Code
│   ├── package.json      # Frontend Dependencies
│   └── ...
├── data/                 # Data Storage (Uploads/DB)
├── requirements.txt      # Python Dependencies
└── README.md             # Project Documentation
```

## 📝 License

This project is licensed under the MIT License.
