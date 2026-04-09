from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas, auth, ai_engine, database
from fastapi.security import OAuth2PasswordRequestForm
import requests

app = FastAPI()
models.Base.metadata.create_all(bind=database.engine)

PEXELS_API_KEY = "ZzK1RZfYVh0J18HYwDP4J9PGR2F4iOLcF7jNOrmNmzWBMSRfCaKRk6UQ"

def get_real_image(word: str):
    url = f"https://api.pexels.com/v1/search?query={word}&per_page=1"
    headers = {"Authorization": PEXELS_API_KEY}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200 and res.json().get("photos"):
            return res.json()["photos"][0]["src"]["landscape"]
    except:
        pass
    return None

@app.post("/api/auth/register")
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email đã tồn tại")
    hashed_pwd = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_pwd, target_score=user.target_score)
    db.add(new_user)
    db.commit()
    return {"message": "Đăng ký thành công"}

@app.post("/api/auth/login")
def login(db: Session = Depends(database.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Sai email hoặc mật khẩu")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/vocab/search")
def search_vocab(keyword: str, db: Session = Depends(database.get_db)):
    # Tìm chính xác 100% trong DB trước để lấy tốc độ siêu nhanh
    existing_word = db.query(models.Vocabulary).filter(models.Vocabulary.word.ilike(keyword)).first()
    if existing_word:
        if not existing_word.image_url:
            existing_word.image_url = get_real_image(existing_word.word)
            db.commit()
        return [existing_word]
    
    # Nếu chưa có, nhờ AI tạo mới
    ai_data = ai_engine.generate_vocab_with_ai(keyword)
    if not ai_data:
        raise HTTPException(status_code=500, detail="AI đang bận hoặc lỗi mạng!")
        
    new_v = models.Vocabulary(
        word=ai_data.get("word", keyword).lower(),
        meaning=ai_data.get("meaning", ""),
        pronunciation=ai_data.get("pronunciation", ""),
        example_sentence=ai_data.get("example_sentence", ""),
        image_url=get_real_image(keyword)
    )
    db.add(new_v)
    db.commit()
    db.refresh(new_v)
    return [new_v]

@app.post("/api/vocab/save/{vocab_id}")
def save_vocab(vocab_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    existing = db.query(models.SavedWord).filter(models.SavedWord.user_id == current_user.id, models.SavedWord.vocab_id == vocab_id).first()
    if existing:
        return {"message": "Đã lưu"}
    new_saved = models.SavedWord(user_id=current_user.id, vocab_id=vocab_id)
    db.add(new_saved)
    db.commit()
    return {"message": "Thành công"}

@app.get("/api/vocab/saved")
def get_saved(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    saved_records = db.query(models.SavedWord).filter(models.SavedWord.user_id == current_user.id).all()
    return [{"id": r.vocab.id, "word": r.vocab.word, "meaning": r.vocab.meaning} for r in saved_records]

# --- API MỚI CHO CHATBOT ---
@app.post("/api/vocab/chat")
def chat_vocab(req: schemas.ChatRequest, current_user: models.User = Depends(auth.get_current_user)):
    ai_response = ai_engine.chat_with_ai(
        req.word, 
        req.message, 
        [{"role": m.role, "content": m.content} for m in req.history]
    )
    return {"response": ai_response}