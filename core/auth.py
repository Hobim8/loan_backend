from fastapi import APIRouter, status
from db.session import Session, engine
from schemas.user import UserCreate
from db.models import UserCreate
from fastapi import HTTPException

auth_router = APIRouter(
    prefix = '/auth',
    tags=['auth']
)

Session = Session(bind=engine)

@auth_router.post('/Signup')
async def Signup (user:UserCreate):
    db_email = Session.query(UserCreate).filter(UserCreate.email == user.email).first()

    if db_email is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="User already exists"
        )


    db_username = Session.query(UserCreate).filter(UserCreate.username == user.username).first()
    
    if db_username is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="User already exists"
        )


