from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext
from src.core.config import Config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expiry = datetime.utcnow() + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expiry})
    token = jwt.encode(to_encode, Config.JWT_SECRET_KEY, algorithm=Config.ALGORITHM)
    return token


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token, Config.JWT_SECRET_KEY, algorithms=[Config.ALGORITHM]
        )
        return payload.get("sub")
    except JWTError:
        return None
