import streamlit as st
import requests
import time
import random

# Thiết lập giao diện rộng (Wide) để tối đa không gian hiển thị
st.set_page_config(page_title="Sổ Tay Từ Vựng AI", page_icon="📖", layout="wide", initial_sidebar_state="expanded")
API_URL = "http://localhost:8888"

# ================= BỘ NHỚ TẠM (SESSION STATE) =================
if "token" not in st.session_state: st.session_state.token = None
if "user_email" not in st.session_state: st.session_state.user_email = "" # Lưu email để hiển thị
if "auth_tab" not in st.session_state: st.session_state.auth_tab = "Đăng nhập"
if "saved_words" not in st.session_state: st.session_state.saved_words = []

def fetch_notebook_data():
    """Hàm tải dữ liệu sổ tay ngầm từ Backend"""
    if st.session_state.token:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        try:
            res = requests.get(f"{API_URL}/api/vocab/saved", headers=headers)
            if res.status_code == 200: st.session_state.saved_words = res.json()
        except: st.session_state.saved_words = []

def main():
    if not st.session_state.token: 
        show_auth_page()
    else: 
        show_main_app()

# ================= TRANG ĐĂNG NHẬP / ĐĂNG KÝ =================
def show_auth_page():
    # Căn giữa Form đăng nhập cho đẹp
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center; color: #1E88E5;'>📖 Từ Vựng AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Hệ thống học từ vựng thông minh</p>", unsafe_allow_html=True)
        st.divider()

        st.session_state.auth_tab = st.radio("Lựa chọn:", ["Đăng nhập", "Đăng ký"], horizontal=True, index=0 if st.session_state.auth_tab == "Đăng nhập" else 1)

        if st.session_state.auth_tab == "Đăng nhập":
            with st.form("login_form"):
                email = st.text_input("📧 Địa chỉ Email")
                pwd = st.text_input("🔑 Mật khẩu", type="password")
                
                # Ấn nút hoặc Enter đều kích hoạt form này
                submitted = st.form_submit_button("🚀 ĐĂNG NHẬP", type="primary", use_container_width=True)
                
                if submitted:
                    if email and pwd:
                        with st.spinner("Đang kết nối..."):
                            res = requests.post(f"{API_URL}/api/auth/login", data={"username": email, "password": pwd})
                            if res.status_code == 200:
                                st.session_state.token = res.json()["access_token"]
                                st.session_state.user_email = email # Lưu lại email
                                fetch_notebook_data() 
                                st.success("✅ Đăng nhập thành công!")
                                time.sleep(0.5)
                                st.rerun()
                            else: st.error("❌ Sai email hoặc mật khẩu!")
                    else: st.warning("⚠️ Vui lòng nhập đủ thông tin.")

        elif st.session_state.auth_tab == "Đăng ký":
            with st.form("register_form"):
                reg_email = st.text_input("📧 Email mới")
                reg_pwd = st.text_input("🔑 Mật khẩu", type="password")
                reg_pwd_confirm = st.text_input("🔑 Nhập lại mật khẩu", type="password")
                submitted = st.form_submit_button("✨ TẠO TÀI KHOẢN", type="primary", use_container_width=True)
                
                if submitted:
                    if not reg_email or not reg_pwd: st.warning("⚠️ Vui lòng điền đầy đủ các ô!")
                    elif reg_pwd != reg_pwd_confirm: st.error("❌ Mật khẩu không khớp!")
                    else:
                        with st.spinner("Đang xử lý..."):
                            res = requests.post(f"{API_URL}/api/auth/register", json={"email": reg_email, "password": reg_pwd, "target_score": 500})
                            if res.status_code == 200:
                                st.success("🎉 Đăng ký thành công! Đang chuyển về Đăng nhập...")
                                time.sleep(2) 
                                st.session_state.auth_tab = "Đăng nhập"
                                st.rerun()
                            else: st.error("❌ Email này đã tồn tại!")

# ================= GIAO DIỆN CHÍNH (SAU KHI ĐĂNG NHẬP) =================
def show_main_app():
    # --- CẤU TRÚC SIDEBAR (MENU BÊN TRÁI) ---
    st.sidebar.markdown(f"### 👤 Thông tin tài khoản")
    st.sidebar.success(f"**Email:**\n{st.session_state.user_email}")
    st.sidebar.divider()
    
    st.sidebar.markdown("### 📌 Điều hướng")
    menu_selection = st.sidebar.radio("Chọn chức năng:", ["🔍 Tra Từ Mới", "📖 Sổ Tay & Ôn Tập"], label_visibility="collapsed")
    
    st.sidebar.divider()
    if st.sidebar.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state.token = None
        st.session_state.user_email = ""
        st.session_state.saved_words = []
        if "search_results" in st.session_state: del st.session_state.search_results
        st.rerun()

    # --- KHU VỰC MÀN HÌNH CHÍNH TỐI ĐA ---
    if menu_selection == "🔍 Tra Từ Mới":
        st.markdown("## 🔍 Khám Phá Từ Vựng Bằng AI")
        
        # DÙNG FORM ĐỂ HỖ TRỢ BẤM ENTER TRA TỪ NHANH
        with st.form("search_form"):
            col_input, col_btn = st.columns([5, 1])
            with col_input:
                word = st.text_input("Nhập từ tiếng Anh (VD: Apple, Persistent)...", label_visibility="collapsed", placeholder="Nhập từ và nhấn Enter...")
            with col_btn:
                submit_search = st.form_submit_button("🔍 Tra Cứu", type="primary", use_container_width=True)
                
        if submit_search:
            if word:
                with st.spinner("🤖 AI đang phân tích dữ liệu..."):
                    res = requests.get(f"{API_URL}/api/vocab/search?keyword={word.strip()}")
                    if res.status_code == 200: st.session_state.search_results = res.json()
                    else: st.error("❌ Lỗi khi tra từ!")
            else: st.warning("⚠️ Hãy nhập một từ để tra cứu nhé!")

        # Hiện kết quả
        if "search_results" in st.session_state:
            for v in st.session_state.search_results:
                with st.container(border=True):
                    col1, col2 = st.columns([1, 2.5]) # Mở rộng cột chữ to hơn
                    
                    with col1:
                        if v.get("image_url"): st.image(v["image_url"], use_container_width=True)
                    with col2:
                        st.markdown(f"<h2 style='color: #1E88E5;'>✨ {v['word'].capitalize()} <span style='font-size: 0.6em; color: gray;'>/{v.get('pronunciation', '')}/</span></h2>", unsafe_allow_html=True)
                        st.write(f"**Ý nghĩa & Cách dùng:** {v['meaning']}")
                        st.info(f"**Ví dụ:**\n{v['example_sentence']}")
                        
                        is_saved = any(sw['id'] == v['id'] for sw in st.session_state.saved_words)
                        if is_saved:
                            st.success("📌 Bạn đã lưu từ này trong sổ tay!")
                        else:
                            if st.button("⭐ Thêm vào Sổ tay", key=f"save_{v['id']}"):
                                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                                save_res = requests.post(f"{API_URL}/api/vocab/save/{v['id']}", headers=headers)
                                if save_res.status_code == 200:
                                    st.toast(f"🎉 Đã thêm '{v['word']}' vào sổ tay!")
                                    fetch_notebook_data() 
                                    time.sleep(0.5)
                                    st.rerun()
                                    
                # --- GIAO DIỆN CHATBOT TỐI ƯU CHO PHÍM ENTER & XÓA CHỮ ---
                chat_key = f"chat_{v['id']}"
                if chat_key not in st.session_state:
                    st.session_state[chat_key] = [{"role": "ai", "content": f"Chào bạn! Cần tôi giúp đặt thêm câu hay phân biệt từ '{v['word']}' với từ khác không?"}]
                
                # Tự động mở rộng phần chat nếu đã có tin nhắn
                is_expanded = len(st.session_state[chat_key]) > 1
                
                with st.expander(f"💬 Chat với Gia sư AI về từ '{v['word'].capitalize()}'", expanded=is_expanded):
                    # Hiển thị tin nhắn
                    for msg in st.session_state[chat_key]:
                        with st.chat_message("assistant" if msg["role"] == "ai" else "user"):
                            st.write(msg["content"])
                            
                    # FORM CHAT: Hỗ trợ Enter và tự động xóa (clear_on_submit=True)
                    with st.form(key=f"form_chat_{v['id']}", clear_on_submit=True):
                        col_c_in, col_c_btn = st.columns([5, 1])
                        with col_c_in:
                            user_chat = st.text_input("Nhắn cho AI...", label_visibility="collapsed", placeholder="Nhập câu hỏi và nhấn Enter...")
                        with col_c_btn:
                            send_chat = st.form_submit_button("Gửi 🚀", use_container_width=True)
                            
                        if send_chat and user_chat:
                            st.session_state[chat_key].append({"role": "user", "content": user_chat})
                            with st.spinner("AI đang gõ..."):
                                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                                payload = {
                                    "word": v['word'],
                                    "message": user_chat,
                                    "history": st.session_state[chat_key][:-1]
                                }
                                chat_res = requests.post(f"{API_URL}/api/vocab/chat", json=payload, headers=headers)
                                if chat_res.status_code == 200:
                                    ai_reply = chat_res.json().get("response")
                                    st.session_state[chat_key].append({"role": "ai", "content": ai_reply})
                                    st.rerun()

    # --- KHU VỰC SỔ TAY VÀ FLASHCARD ---
    elif menu_selection == "📖 Sổ Tay & Ôn Tập":
        st.markdown("## 📖 Quản Lý & Ôn Tập Sổ Tay")
        saved_words = st.session_state.saved_words
        
        if not saved_words: 
            st.info("Sổ tay của bạn đang trống. Hãy qua mục 'Tra Từ Mới' để lưu thêm từ nhé!")
        else:
            st.success(f"Thành tựu: Bạn đang sở hữu **{len(saved_words)}** từ vựng trong sổ tay. Cố lên nhé!")
            
            # Tối ưu lại tỷ lệ màn hình (List nhỏ lại, Flashcard to ra)
            col_list, col_quiz = st.columns([1, 2])
            
            with col_list:
                st.subheader("📋 Danh sách từ")
                for v in saved_words:
                    with st.expander(f"📌 {v['word'].capitalize()}"):
                        st.write(f"**Nghĩa:** {v['meaning']}")
            
            with col_quiz:
                st.subheader("🧠 Thử Thách Flashcard")
                if st.button("🎲 Bắt đầu rút thẻ ngẫu nhiên", use_container_width=True, type="primary"):
                    st.session_state.current_card = random.choice(saved_words)
                    st.session_state.show_answer = False
                
                if "current_card" in st.session_state:
                    card = st.session_state.current_card
                    
                    with st.container(border=True):
                        # Nếu có ảnh, cho hiện nhỏ xinh xắn trên thẻ
                        if card.get("image_url"):
                            st.image(card["image_url"], use_container_width=True)
                            
                        st.markdown(f"<h1 style='text-align: center; color: #E53935; font-size: 3em;'>{card['word'].upper()}</h1>", unsafe_allow_html=True)
                        st.divider()
                        
                        if not st.session_state.get("show_answer", False):
                            if st.button("👀 Lật thẻ xem đáp án", use_container_width=True):
                                st.session_state.show_answer = True
                                st.rerun()
                        else:
                            st.info(f"**Giải nghĩa:** {card['meaning']}\n\n**Phiên âm:** /{card.get('pronunciation', '')}/")
                            
                            col_b1, col_b2 = st.columns(2)
                            with col_b1:
                                if st.button("💡 Hỏi AI mẹo nhớ từ này", use_container_width=True):
                                    st.toast("Tính năng đang phân tích mẹo hay cho bạn...")
                                    # Bạn có thể nối API mẹo nhớ (get_review_tip) vào đây nếu đã cài
                            with col_b2:
                                if st.button("⏭️ Rút thẻ tiếp theo", type="primary", use_container_width=True):
                                    st.session_state.current_card = random.choice(saved_words)
                                    st.session_state.show_answer = False
                                    st.rerun()

if __name__ == "__main__":
    main()