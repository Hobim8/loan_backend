from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi import Depends, HTTPException 
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "/auth/Login")


def create_access_token (data : dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


def get_current_user (token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )

    user_id = payload.get('user_id')

    get_user = db.query(User).filter(User.id == user_id).first()

    if not get_user:
        raise HTTPException(status_code=401, detail="Please login")
    
    return(get_user)
    






