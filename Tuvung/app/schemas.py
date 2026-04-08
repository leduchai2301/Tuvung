from pydantic import BaseModel, EmailStr
from typing import Optional


# --- Schemas cho User ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    target_score: int = 650


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    target_score: int

    class Config:
        from_attributes = True

    # --- Schemas cho Vocabulary ---


class VocabBase(BaseModel):
    word: str
    meaning: str
    pronunciation: Optional[str] = None
    example_sentence: Optional[str] = None


from typing import Optional  # Thêm dòng này ở đầu file nếu chưa có


class VocabResponse(BaseModel):
    id: int
    word: str
    meaning: str
    pronunciation: Optional[str] = None
    example_sentence: Optional[str] = None
    is_ai_enhanced: bool

    # --- DÒNG MỚI CẦN THÊM VÀO ĐÂY ---
    image_url: Optional[str] = None

    class Config:
        from_attributes = True