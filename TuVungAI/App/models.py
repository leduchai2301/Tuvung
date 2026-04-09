from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    target_score = Column(Integer, default=500)

class Vocabulary(Base):
    __tablename__ = "vocabularies"
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, index=True)
    meaning = Column(String)
    pronunciation = Column(String)
    example_sentence = Column(String)
    image_url = Column(String, nullable=True)

class SavedWord(Base):
    __tablename__ = "saved_words"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vocab_id = Column(Integer, ForeignKey("vocabularies.id"))
    
    # DÒNG QUAN TRỌNG NHẤT VỪA ĐƯỢC THÊM VÀO:
    # Báo cho Database biết cách kết nối Sổ tay với Từ vựng
    vocab = relationship("Vocabulary")