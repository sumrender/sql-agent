# LangChain SQL Agent (MSSQL + Ollama or Gemini)

A SQL agent that answers natural language questions about an MSSQL database using LangChain agents. You can use **Ollama** (e.g. `ministral-3:3b`) running locally or **Google Gemini** (e.g. `gemini-2.0-flash`). Use it via **LangGraph Studio** (interactive chat with memory).

## Prerequisites

- Python 3.10+
- **Ollama:** [Ollama](https://ollama.com/) installed and running locally with the `ministral-3b:3b` model, or **Gemini:** a [Google API key](https://aistudio.google.com/apikey) for the Gemini API
- Access to an MSSQL database

### Installing Ollama and the ministral-3b model

1. Install Ollama from [ollama.com](https://ollama.com/) or via Homebrew on macOS:

   ```bash
   brew install ollama
   ```

2. Start the Ollama service:

   ```bash
   ollama serve
   ```

3. Pull the `ministral-3b:3b` model:

   ```bash
   ollama pull ministral-3b:3b
   ```

4. Verify the model is available:

   ```bash
   ollama list
   ```

## Setup

### 1. Create and activate virtual environment

```bash
python3.11 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Copy the example env file and set your MSSQL and LLM settings:

```bash
cp .env.example .env
```

Edit `.env`:

- **LLM:** Set `LLM_PROVIDER=ollama` (default) or `LLM_PROVIDER=gemini`. Set `LLM_MODEL` (e.g. `ministral-3b:3b` for Ollama, `gemini-2.0-flash` for Gemini). For Gemini, set `GOOGLE_API_KEY` or `GEMINI_API_KEY`.
- **MSSQL:** Set `MSSQL_SERVER`, `MSSQL_DATABASE`, `MSSQL_USER`, `MSSQL_PASSWORD`.
- **Ollama (if using):** Set `OLLAMA_BASE_URL` (default `http://localhost:11434`).

## Usage

### Option 1: LangGraph Studio (chat interface with memory)

Start the Studio dev server:

```bash
langgraph dev
```

Add `--no-browser` to skip opening the browser automatically: `langgraph dev --no-browser`.

Open the Studio UI in your browser (or use the chatbot UI at the link below). You can ask questions in natural language, for example:

- "Tell me the schema of the database"
- "Show me the invoices for the 5 top customers"
- "What tables are available?"

Conversation history is kept so you can ask follow-up questions.

## Security

- Use a **read-only** database user when possible.
- The agent is instructed not to run DML (INSERT, UPDATE, DELETE, DROP).
- Keep `.env` out of version control; only commit `.env.example`.

## Project layout

```
├── venv/
├── .env                 # Your credentials (do not commit)
├── .env.example
├── requirements.txt
├── langgraph.json       # LangGraph Studio config
├── config.py            # Single source of truth for all config and URLs
├── llm.py               # LLM factory (Ollama or Gemini)
├── sql_agent.py         # SQL agent
└── README.md
```

UI FOR CHATBOT
```
https://agentchat.vercel.app/
```