import sqlite3
import json
from pathlib import Path

# Trỏ thẳng vào file test.db bạn vừa copy bằng tay
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "data" / "test.db"


def extract_vocab():
    if not DB_PATH.exists():
        print(f"❌ Lỗi: Không tìm thấy file {DB_PATH}")
        return

    print("⏳ Đang tiến hành đọc file test.db...")
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        cursor.execute("SELECT flds FROM notes")
        rows = cursor.fetchall()

        vocab_list = []
        for row in rows:
            fields = row[0].split('\x1f')
            if len(fields) >= 2:
                word = fields[0].strip()
                meaning = fields[1].strip()
                if word and meaning:
                    vocab_list.append({"word": word, "meaning": meaning})

        print(f"🎉 Đã trích xuất thành công {len(vocab_list)} từ vựng!")

        output_file = BASE_DIR / "data" / "vocab_raw.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(vocab_list, f, ensure_ascii=False, indent=4)

        print(f"📁 Đã lưu vào:\n{output_file}")

    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    extract_vocab()