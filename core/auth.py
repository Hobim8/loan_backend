from fastapi import APIRouter, status, HTTPException, Depends
from db.session import engine, get_db
from schemas.user import UserCreate as UserCreateSchema 
from schemas.user import UserLogin
from db.models import UserCreate as UserModel  
from sqlalchemy.orm import Session 
from core.jwt import create_access_token

auth_router = APIRouter(
    prefix = '/auth',
    tags=['auth']
)


@auth_router.post('/Signup')
def Signup (user:UserCreateSchema,
            db: Session = Depends(get_db)):
    
 if db.query(UserModel).filter(UserModel.email == user.email).first():
    raise HTTPException(status_code=400, detail='Email already exists')

 if db.query(UserModel).filter(UserModel.username == user.username).first():
    raise HTTPException(status_code=400, detail='username already exists')
 
 new_user = UserModel(**user.model_dump())
 db.add(new_user)
 db.commit()
 db.refresh(new_user)

 return{'message': 'User created successfully'}



@auth_router.post('/Login')
def Login (user:UserLogin,
           db:Session = Depends(get_db)):
  
  db_user = db.query(UserModel).filter(UserModel.username == user.username).first()

  if not db_user:
    raise HTTPException(status_code=401, detail='invaild credentials')
  
  if db_user.hashed_password != user.password:
    raise HTTPException(status_code=401, detail='invaild credentials')
  
  
  access_token = create_access_token(
    data={
      'sub': db_user.username,
      'user_id' : db_user.id 
    }
  )

  return{
    'access_token' : access_token,
    'token_type' : 'bearer'
  }


