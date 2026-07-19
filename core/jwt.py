from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/Login")


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        get_user = db.query(User).filter(User.id == user_id).first()

        if not get_user:
            raise HTTPException(
                status_code=404, detail="We could not find your account."
            )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Your session has expired. Please sign in again.",
        )

    return get_user


def get_current_staff_user(current_user: User = Depends(get_current_user)) -> User:
    """Require an authenticated user with is_staff=True (monitoring / admin)."""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to view this area. Please contact your administrator.",
        )
    return current_user
