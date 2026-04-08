from datetime import datetime, timedelta
from jose import jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

SECRET_KEY = "TRUONG_IT_SECRET_KEY_DO_AN_CUOI_KI"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Hàm băm mật khẩu trực tiếp bằng bcrypt (Mới, thay thế passlib)
def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_bytes.decode('utf-8')

# Hàm kiểm tra mật khẩu có khớp không
def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password=plain_bytes, hashed_password=hashed_bytes)

# Hàm tạo JWT Token (Giữ nguyên)
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Cài đặt scheme để FastAPI biết chỗ mà người dùng điền Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực danh tính (Token không hợp lệ hoặc đã hết hạn)",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Giải mã token bằng SECRET_KEY và ALGORITHM đã định nghĩa ở trên cùng file
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Tìm user trong Database dựa vào email lấy được từ Token
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception

    return user