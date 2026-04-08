from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    target_score = Column(Integer, default=500)

    # Mối quan hệ: Một User có thể lưu nhiều từ
    saved_words = relationship("SavedWord", back_populates="user")


class Vocabulary(Base):
    __tablename__ = "vocabularies"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, index=True)
    meaning = Column(String)
    pronunciation = Column(String)
    example_sentence = Column(String)
    is_ai_enhanced = Column(Boolean, default=False)

    # Cột ảnh chúng ta vừa thêm để lấy ảnh từ Pexels
    image_url = Column(String, nullable=True)


class SavedWord(Base):
    __tablename__ = "saved_words"

    id = Column(Integer, primary_key=True, index=True)

    # ĐÂY LÀ 2 DÒNG QUAN TRỌNG NHẤT VỪA BỊ LỖI
    user_id = Column(Integer, ForeignKey("users.id"))
    vocab_id = Column(Integer, ForeignKey("vocabularies.id"))

    # Thiết lập mối quan hệ
    user = relationship("User", back_populates="saved_words")
    vocab = relationship("Vocabulary")