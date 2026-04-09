from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    target_score: int = 500

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    class Config: from_attributes = True

class VocabResponse(BaseModel):
    id: int
    word: str
    meaning: str
    pronunciation: Optional[str]
    example_sentence: Optional[str]
    image_url: Optional[str]
    class Config: from_attributes = True

# --- THÊM CẤU TRÚC CHO CHATBOT ---
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    word: str
    message: str
    history: List[ChatMessage] = []