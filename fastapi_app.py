"""FastAPI server exposing grounded HR chat and retrieved policy documents."""

import os
import traceback

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator

from chat_with_hr_assistant import run_chat

app = FastAPI(title="Nexus HR Assist API", version="1.0.0")

_default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8501",
    "http://127.0.0.1:8501",
]
_extra = os.environ.get("CORS_ORIGINS", "")
origins = _default_origins + [o.strip() for o in _extra.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    query: str | None = Field(
        default=None,
        description="Single user question (used when messages is omitted)",
    )
    messages: list[ChatMessage] | None = Field(
        default=None,
        description="Full conversation (role/content); include prior turns so follow-ups resolve context",
    )

    @model_validator(mode="after")
    def require_query_or_messages(self) -> "ChatRequest":
        if self.messages and len(self.messages) > 0:
            return self
        if self.query is not None and self.query.strip():
            return self
        raise ValueError("Provide either a non-empty query or a non-empty messages list")


class DocumentChunk(BaseModel):
    id: str
    title: str | None = None
    content: str = ""
    filepath: str | None = None
    url: str | None = None


class ChatResponse(BaseModel):
    answer: str
    role: str = "assistant"
    documents: list[DocumentChunk]
    thoughts: list[dict] = Field(default_factory=list)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    try:
        if req.messages and len(req.messages) > 0:
            payload = run_chat(messages=[m.model_dump() for m in req.messages])
        else:
            payload = run_chat(query=req.query.strip())
        return ChatResponse(**payload)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e)) from e
