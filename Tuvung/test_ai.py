from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app import ai_engine
from app import models, schemas, auth
from app.database import engine, get_db
from app.auth import get_current_user

# Lệnh này sẽ tự động tạo file vocab_app.db và các bảng nếu chưa có
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Vocabulary Project")

@app.get("/")
def read_root():
    return {"message": "Hệ thống Backend đã hoạt động thành công!"}

@app.post("/api/auth/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email này đã được đăng ký")
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password, target_score=user.target_score)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/auth/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sai email hoặc mật khẩu", headers={"WWW-Authenticate": "Bearer"})
    access_token = auth.create_access_token(data={"sub": user.email, "id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

# ==========================================
# 3. API TÌM KIẾM TỪ VỰNG (CÓ TÍCH HỢP AI)
# ==========================================
@app.get("/api/vocab/search", response_model=list[schemas.VocabResponse])
def search_vocabulary(keyword: str = Query(..., min_length=1, description="Nhập từ khóa tiếng Anh cần tìm"), db: Session = Depends(get_db)):
    search_term = f"%{keyword}%"
    results = db.query(models.Vocabulary).filter(models.Vocabulary.word.ilike(search_term)).limit(5).all()
    for item in results:
        if not item.is_ai_enhanced:
            enhanced_data = ai_engine.enhance_vocab_with_ai(item.word)
            if enhanced_data:
                item.meaning = enhanced_data.get("meaning", item.meaning)
                item.pronunciation = enhanced_data.get("pronunciation")
                item.example_sentence = enhanced_data.get("example_sentence")
                item.is_ai_enhanced = True
                db.commit()
                db.refresh(item)
    return results

# ==========================================
# 4. API LƯU TỪ VỰNG VÀO SỔ TAY (Cần Đăng Nhập)
# ==========================================
@app.post("/api/vocab/save/{vocab_id}")
def save_vocabulary(vocab_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    vocab = db.query(models.Vocabulary).filter(models.Vocabulary.id == vocab_id).first()
    if not vocab:
        raise HTTPException(status_code=404, detail="Không tìm thấy từ vựng này.")
    existing_saved = db.query(models.SavedWord).filter(models.SavedWord.user_id == current_user.id, models.SavedWord.vocab_id == vocab_id).first()
    if existing_saved:
        return {"message": "Bạn đã lưu từ này trong sổ tay rồi!"}
    new_saved_word = models.SavedWord(user_id=current_user.id, vocab_id=vocab_id)
    db.add(new_saved_word)
    db.commit()
    return {"message": f"Đã thêm thành công từ '{vocab.word}' vào sổ tay của {current_user.email}!"}

# ==========================================
# 5. API XEM DANH SÁCH TỪ ĐÃ LƯU TRONG SỔ TAY
# ==========================================
@app.get("/api/vocab/saved", response_model=list[schemas.VocabResponse])
def get_saved_vocabulary(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    saved_records = db.query(models.SavedWord).filter(models.SavedWord.user_id == current_user.id).all()
    saved_vocabs = [record.vocab for record in saved_records]
    return saved_vocabs