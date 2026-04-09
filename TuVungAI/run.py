import subprocess
import sys
import time

def main():
    print("🚀 Đang khởi động Hệ thống...")
    
    # Đã sửa 'app' thành 'App' để khớp với thư mục của bạn
    print("⏳ Đang bật Backend (Cổng 8888)...")
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "App.main:app", "--reload", "--port", "8888"]
    )

    # Đợi 3 giây để Backend khởi động xong
    time.sleep(3)

    # Đã sửa 'frontend_app.py' thành 'frontend.py' để khớp với file của bạn
    print("🎨 Đang bật Giao diện người dùng...")
    frontend = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend.py"]
    )

    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\n🛑 Đang tắt toàn bộ hệ thống...")
        backend.terminate()
        frontend.terminate()
        print("✅ Đã tắt an toàn!")

if __name__ == "__main__":
    main()