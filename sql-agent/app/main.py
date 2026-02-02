"""FastAPI application for the SQL agent."""
import time

from langchain_core.messages import AIMessage

from logging_config import get_logger, setup_logging

setup_logging()

from sql_agent import agent, db

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logger = get_logger(__name__)

app = FastAPI(title="SQL Agent API", description="Natural language queries over SQLite")


class QueryRequest(BaseModel):
    """Request body for /query."""

    question: str


class QueryResponse(BaseModel):
    """Response body for /query."""

    answer: str


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/tables")
def list_tables():
    """List available database tables."""
    logger.info("GET /tables")
    try:
        tables = db.get_usable_table_names()
        logger.info("GET /tables - returned %d tables", len(tables))
        return {"tables": tables}
    except Exception as e:
        logger.exception("GET /tables failed: %s", e)
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    """Submit a natural language question and get an answer from the database."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="question must not be empty")

    logger.info('POST /query - question: "%s"', request.question[:100])
    start = time.perf_counter()
    try:
        state = agent.invoke(
            {"messages": [{"role": "user", "content": request.question}]},
        )
    except Exception as e:
        elapsed = time.perf_counter() - start
        logger.exception("POST /query failed after %.2fs: %s", elapsed, e)
        raise HTTPException(status_code=500, detail=str(e)) from e

    messages = state.get("messages", [])
    if not messages:
        logger.error("POST /query - agent returned no messages")
        raise HTTPException(status_code=500, detail="Agent returned no messages")

    last_message = messages[-1]
    if isinstance(last_message, AIMessage):
        answer = last_message.content if isinstance(last_message.content, str) else ""
    else:
        answer = getattr(last_message, "content", str(last_message))

    elapsed = time.perf_counter() - start
    logger.info("POST /query completed in %.2fs", elapsed)
    return QueryResponse(answer=answer or "No answer generated.")
