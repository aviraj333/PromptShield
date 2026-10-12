
from uuid import uuid4
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.detector import inspect_prompt


app = FastAPI(
    title="PromptShield API",
    version="1.0.0",
    description="Prompt injection screening prototype",
)


# Allow our local React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# Define the data accepted by the screening API
class ScreenRequest(BaseModel):
    source: Literal[
        "user",
        "retrieved_document",
        "tool_output",
    ]
    content: str = Field(min_length=1, max_length=5000)
    request_id: str = Field(
        default_factory=lambda: str(uuid4())
    )
    policy_id: str = "default"
    context: dict = Field(default_factory=dict)


# Health check
@app.get("/api/v1/health")
def health():
    return {
        "status": "ok",
        "mode": "local",
        "ai_status": "rules_only",
    }


# Prompt screening endpoint
@app.post("/api/v1/screen")
def screen_prompt(request: ScreenRequest):
    if request.policy_id != "default":
        raise HTTPException(
            status_code=400,
            detail="Unknown policy_id",
        )

    result = inspect_prompt(
        request.content,
        request.source,
    )

    return {
        "request_id": request.request_id,
        **result,
        "policy_version": "1.0",
        "ai_status": "rules_only",
    }
