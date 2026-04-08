import json
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models

# Đảm bảo các bảng đã được tạo
models.Base.metadata.create_all(bind=engine)


def seed_data():
    db: Session = SessionLocal()
    json_path = "data/vocab_raw.json"

    if not os.path.exists(json_path):
        print("❌ Không tìm thấy file vocab_raw.json!")
        return

    print("⏳ Đang đọc file JSON...")
    with open(json_path, "r", encoding="utf-8") as f:
        vocab_list = json.load(f)

    print(f"⏳ Đang chuẩn bị nạp {len(vocab_list)} từ vựng vào Database chính...")

    # Kiểm tra xem DB đã có dữ liệu chưa để tránh bị nạp trùng (duplicate)
    existing_count = db.query(models.Vocabulary).count()
    if existing_count > 0:
        print(f"⚠️ Database đã có sẵn {existing_count} từ vựng. Đang nạp thêm (nếu có)...")

    # Lặp qua danh sách và thêm vào Database
    added_count = 0
    for item in vocab_list:
        # Tách lấy từ tiếng Anh và nghĩa tiếng Việt
        word_text = item.get("word", "").strip()
        meaning_text = item.get("meaning", "").strip()

        # Bỏ qua nếu từ hoặc nghĩa bị trống
        if not word_text or not meaning_text:
            continue

        # Lưu vào bảng Vocabulary
        new_vocab = models.Vocabulary(
            word=word_text,
            meaning=meaning_text,
            is_ai_enhanced=False  # Mặc định là False, sau này AI sẽ xử lý sau
        )
        db.add(new_vocab)
        added_count += 1

        # Cứ mỗi 500 từ thì lưu (commit) một lần cho máy đỡ bị treo
        if added_count % 500 == 0:
            db.commit()
            print(f"  -> Đã lưu {added_count} từ...")

    # Lưu những từ còn sót lại cuối cùng
    db.commit()
    db.close()

    print(f"🎉 HOÀN TẤT! Đã nạp thành công {added_count} từ vựng vào Database của Web!")


if __name__ == "__main__":
    seed_data()