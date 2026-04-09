import google.generativeai as genai
import json

# Thay API Key của bạn
GEMINI_API_KEY = "AIzaSyD4juWu_NQAmQArAkyCx6iQa5akzMaHuyQ" 
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def generate_vocab_with_ai(word: str):
    prompt = f"""
    Bạn là chuyên gia tiếng Anh. Hãy giải nghĩa từ "{word}".
    Trả về ĐÚNG MỘT định dạng JSON nguyên bản (không markdown):
    {{
        "word": "{word}",
        "meaning": "Nghĩa tiếng Việt. Ghi chú thêm: Từ này dùng trong ngữ cảnh nào thì hợp lý?",
        "pronunciation": "Phiên âm IPA",
        "example_sentence": "2 câu ví dụ tiếng Anh thực tế (kèm dịch nghĩa tiếng Việt)"
    }}
    """
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:-3].strip()
        elif result_text.startswith("```"):
            result_text = result_text[3:-3].strip()
        return json.loads(result_text)
    except Exception as e:
        print(f"Lỗi AI: {e}")
        return None

# --- HÀM MỚI: CHATBOT GIA SƯ ---
def chat_with_ai(word: str, user_message: str, history: list):
    system_prompt = f"Bạn là một gia sư tiếng Anh thân thiện. Bạn đang giúp học viên hiểu rõ hơn về từ '{word}'. Hãy trả lời ngắn gọn, dễ hiểu và đưa ra các ví dụ thực tế nếu học viên hỏi."
    
    # Ghép lịch sử chat vào để AI nhớ ngữ cảnh
    conversation = f"{system_prompt}\n\n"
    for msg in history:
        role_name = "Học viên" if msg["role"] == "user" else "Gia sư"
        conversation += f"{role_name}: {msg['content']}\n"
    
    conversation += f"Học viên: {user_message}\nGia sư:"
    
    try:
        response = model.generate_content(conversation)
        return response.text.strip()
    except Exception as e:
        print(f"Lỗi Chat AI: {e}")
        return "Xin lỗi, gia sư AI đang bận. Bạn vui lòng thử lại sau nhé!"