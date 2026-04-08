from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from app import ai_engine, models, schemas, auth
from app.database import engine, get_db
from app.auth import get_current_user
import requests

# Khởi tạo database
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Vocabulary Project")

# API Key Pexels của bạn
PEXELS_API_KEY = "ZzK1RZfYVh0J18HYwDP4J9PGR2F4iOLcF7jNOrmNmzWBMSRfCaKRk6UQ"

# Cấu hình CORS - Quan trọng để Frontend gọi được API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, # Đổi thành False để tránh lỗi bảo mật khi dùng Token
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hàm tìm ảnh thật từ Pexels
def get_real_image(word: str):
    url = f"https://api.pexels.com/v1/search?query={word}&per_page=1"
    headers = {"Authorization": PEXELS_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("photos"):
                return data["photos"][0]["src"]["landscape"]
    except Exception as e:
        print(f"Lỗi Pexels cho từ '{word}':", e)
    return None

# --- CÁC API HỆ THỐNG ---

@app.get("/")
def read_root():
    return {"message": "Hệ thống Backend AI Vocabulary đã sẵn sàng!"}

# --- XÁC THỰC NGƯỜI DÙNG ---

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
        raise HTTPException(status_code=401, detail="Sai email hoặc mật khẩu")
    access_token = auth.create_access_token(data={"sub": user.email, "id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

# --- TỪ VỰNG & AI ---

@app.get("/api/vocab/search", response_model=list[schemas.VocabResponse])
def search_vocabulary(keyword: str = Query(...), db: Session = Depends(get_db)):
    search_term = f"%{keyword}%"
    results = db.query(models.Vocabulary).filter(models.Vocabulary.word.ilike(search_term)).limit(5).all()

    if results:
        for item in results:
            # Nếu từ đã có nhưng chưa được AI tối ưu hoặc chưa có ảnh thì cập nhật
            if not item.is_ai_enhanced or not item.image_url:
                enhanced_data = ai_engine.enhance_vocab_with_ai(item.word)
                if enhanced_data:
                    item.meaning = enhanced_data.get("meaning", item.meaning)
                    item.pronunciation = enhanced_data.get("pronunciation")
                    item.example_sentence = enhanced_data.get("example_sentence")
                    item.is_ai_enhanced = True
                if not item.image_url:
                    item.image_url = get_real_image(item.word)
                db.commit()
                db.refresh(item)
    else:
        # Nếu từ hoàn toàn mới, nhờ AI định nghĩa và tìm ảnh
        enhanced_data = ai_engine.enhance_vocab_with_ai(keyword)
        if enhanced_data:
            img_url = get_real_image(keyword)
            new_vocab = models.Vocabulary(
                word=keyword.lower(),
                meaning=enhanced_data.get("meaning", "Chưa xác định"),
                pronunciation=enhanced_data.get("pronunciation", ""),
                example_sentence=enhanced_data.get("example_sentence", ""),
                is_ai_enhanced=True, # Đánh dấu là đã qua xử lý AI
                image_url=img_url
            )
            db.add(new_vocab)
            db.commit()
            db.refresh(new_vocab)
            results = [new_vocab]
    return results

# --- QUẢN LÝ SỔ TAY ---

@app.post("/api/vocab/save/{vocab_id}")
def save_vocabulary(vocab_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    vocab = db.query(models.Vocabulary).filter(models.Vocabulary.id == vocab_id).first()
    if not vocab:
        raise HTTPException(status_code=404, detail="Không tìm thấy từ.")
    existing = db.query(models.SavedWord).filter(models.SavedWord.user_id == current_user.id, models.SavedWord.vocab_id == vocab_id).first()
    if existing:
        return {"message": "Đã lưu rồi!"}
    new_saved_word = models.SavedWord(user_id=current_user.id, vocab_id=vocab_id)
    db.add(new_saved_word)
    db.commit()
    return {"message": "Đã thêm thành công!"}

@app.get("/api/vocab/saved", response_model=list[schemas.VocabResponse])
def get_saved_vocabulary(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    saved_records = db.query(models.SavedWord).filter(models.SavedWord.user_id == current_user.id).all()
    return [record.vocab for record in saved_records]

@app.delete("/api/vocab/delete/{vocab_id}")
def delete_saved_word(vocab_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    saved_item = db.query(models.SavedWord).filter(
        models.SavedWord.user_id == current_user.id,
        models.SavedWord.vocab_id == vocab_id
    ).first()
    if not saved_item:
        raise HTTPException(status_code=404, detail="Không tìm thấy từ trong sổ tay.")
    db.delete(saved_item)
    db.commit()
    return {"message": "Đã xóa thành công khỏi sổ tay!"}

# --- TIỆN ÍCH ---

@app.get("/api/vocab/tts")
def get_tts(word: str):
    # Link âm thanh từ Google Translate (Clienttw-ob để tránh lỗi chặn)
    tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={word}&tl=en&client=tw-ob"
    return {"audio_url": tts_url}