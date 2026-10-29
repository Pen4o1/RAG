import logging
import os

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from query_data import query_rag

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rag")

app = FastAPI(title="RAG Query API", version="1.0.0")

cors_origins = os.getenv("CORS_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if cors_origins == "*" else [origin.strip() for origin in cors_origins.split(",") if origin.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    top_k: int = Field(5, ge=1, le=20)


class TableData(BaseModel):
    title: str = ""
    headers: list[str]
    rows: list[list[str]]


class Match(BaseModel):
    text: str
    source: str
    score: float | None = None
    chunk_index: int | None = None
    kind: str = "text"
    tables: list[TableData] = []


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    tables: list[TableData] = []
    matches: list[Match]


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = os.getenv("RAG_API_KEY")
    if not expected:
        return
    if x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(body: QueryRequest, _: None = Depends(require_api_key)):
    try:
        return query_rag(body.query, top_k=body.top_k)
    except Exception:
        logger.exception("RAG query failed")
        raise HTTPException(status_code=502, detail="Query failed")
