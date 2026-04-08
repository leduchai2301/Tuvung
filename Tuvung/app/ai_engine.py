import google.generativeai as genai
import json

# Thay API Key của bạn vào đây
GEMINI_API_KEY = "AIzaSyA6FCwFPXlYYY7-lsPRgm9r83Q44eKrUNY"

genai.configure(api_key=GEMINI_API_KEY)

# Sử dụng model Gemini 1.5 Flash (nhanh, rẻ và cực thông minh)
model = genai.GenerativeModel('gemini-2.5-flash')


def enhance_vocab_with_ai(word: str):
    """
    Hàm này nhận vào một từ tiếng Anh, nhờ Gemini tra nghĩa, phiên âm và tạo ví dụ.
    Trall về một Dictionary (JSON) chuẩn.
    """
    prompt = f"""
    Bạn là một chuyên gia ngôn ngữ tiếng Anh. Hãy giải nghĩa từ "{word}".
    Trả về ĐÚNG MỘT định dạng JSON nguyên bản (không có markdown, không có ```json ở đầu/cuối), với cấu trúc sau:
    {{
        "meaning": "Nghĩa tiếng Việt ngắn gọn, dễ hiểu",
        "pronunciation": "Phiên âm quốc tế IPA",
        "example_sentence": "3 câu ví dụ tiếng Anh cấp độ TOEIC chứa từ này, ngăn cách nhau bằng dấu |"
    }}
    """

    try:
        print(f"🤖 Đang gọi AI xử lý từ: {word}...")
        response = model.generate_content(prompt)

        # Parse chuỗi JSON trả về từ AI thành Dictionary của Python
        result_text = response.text.strip()
        # Dọn dẹp nếu AI lỡ chèn thêm markdown
        if result_text.startswith("```json"):
            result_text = result_text[7:-3].strip()

        enhanced_data = json.loads(result_text)
        return enhanced_data

    except Exception as e:
        print(f"❌ Lỗi khi gọi AI: {e}")
        return None