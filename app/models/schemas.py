from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any, Dict

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.2
    max_tokens: Optional[int] = 512
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str = "stop"

class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Usage
