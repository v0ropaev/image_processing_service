from jwt import encode, decode, ExpiredSignatureError, PyJWTError
from os import getenv
from datetime import datetime, timedelta
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends, status
from app.db import get_session, User
from sqlalchemy.future import select
import bcrypt

SECRET_KEY = getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def register_user(email: str, password: str):
    async with get_session() as db:
        result = await db.execute(select(User).filter_by(email=email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        new_user = User(email=email, password=hashed_password)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        access_token = create_access_token(data={"email": email})
        return {"access_token": access_token, "token_type": "bearer"}


async def authenticate_user(email: str, password: str):
    async with get_session() as db:
        result = await db.execute(select(User).filter_by(email=email))
        user = result.scalar_one_or_none()
        if user and bcrypt.checkpw(password.encode(), user.password.encode()):
            access_token = create_access_token(data={"email": email})
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")


async def get_user_from_token(token: str = Depends(oauth2_scheme)) -> User:
    payload = decode_access_token(token)
    email = payload.get("email")
    async with get_session() as db:
        result = await db.execute(select(User).filter_by(email=email))
        user = result.scalar_one_or_none()
        if user:
            return user
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
