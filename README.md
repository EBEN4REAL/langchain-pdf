

# 🧠 Chat with PDF – AI-powered Document Interaction

This project allows users to **upload PDFs and chat with them intelligently**, powered by a combination of **Flask (Python backend)**, **Svelte (TypeScript frontend)**, and vector databases like **Pinecone** and **ChromaDB** for document embeddings.
It integrates **Redis** and **Celery** for caching and background task management respectively.


## Project Walkthrogh

https://www.loom.com/share/a9fd6d9df06b4224bb415f0f6de117b8

---

## 🚀 Tech Stack

**Frontend**

* ⚡ Svelte + TypeScript
* TailwindCSS (for styling)

**Backend**

* 🐍 Flask (Python)
* Celery (background worker)
* Redis (task queue + cache)

**Vector Databases**

* 🪵 Pinecone
* 🧩 ChromaDB

**LLM Integration**

* OpenAI or compatible API for embeddings and conversational reasoning

---

## 🧩 Project Overview

* Upload a PDF document.
* Extract and embed its text using Pinecone or ChromaDB.
* Query or “chat” with the document using a conversational AI model.
* Background tasks and cache management are handled by Redis + Celery.
* View upload documents

---

## 🛠️ First Time Setup

### Using Pipenv

```bash
# Install dependencies
pipenv install

# Create and activate virtual environment
pipenv shell

# Initialize the database
flask --app app.web init-db
```

---

## ▶️ Running the App

The app relies on **three main services**:

1. Flask server
2. Celery worker
3. Redis

If you stop any of them, restart before continuing.

---

### 🧩 Start the Flask Server

```bash
pipenv shell
inv dev
```

---

### ⚙️ Start the Celery Worker

```bash
pipenv shell
inv devworker
```

---

### 🧠 Start Redis

```bash
redis-server
```

---

### 🔄 Reset the Database

```bash
pipenv shell
flask --app app.web init-db
```

---

## 🖥️ Frontend (Svelte + TypeScript)

The Svelte frontend runs independently and communicates with the Flask API.

```bash
cd frontend
npm install
npm run dev
```

Then open the app in your browser at [http://localhost:5173](http://localhost:5173).

---

## 📁 Project Structure

```
├── app/
│   ├── web/              # Flask web server
│   ├── workers/          # Celery background workers
│   ├── db/               # Database and vector store setup
│   ├── utils/            # Helper functions (PDF parsing, embeddings)
│   └── ...
├── frontend/             # Svelte + TypeScript client
├── Pipfile               # Python dependencies
├── tasks.py              # Celery tasks
└── README.md
```

---

## 🧪 Environment Variables

Before running, set up your `.env` file with the following keys:

```
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=sqlite:///instance/app.db
VECTOR_STORE=chroma  # or pinecone
```

---

## 🧰 Useful Commands

| Task                 | Command                       |
| -------------------- | ----------------------------- |
| Install deps         | `pipenv install`              |
| Activate environment | `pipenv shell`                |
| Run server           | `inv dev`                     |
| Run worker           | `inv devworker`               |
| Run frontend         | `npm run dev`                 |
| Reset DB             | `flask --app app.web init-db` |

---
