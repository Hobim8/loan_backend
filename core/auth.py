from fastapi import APIRouter, status, HTTPException, Depends
from db.session import engine, get_db
from schemas.user import UserCreate as UserCreateSchema 
from db.models import UserCreate as UserModel  
from sqlalchemy.orm import Session 

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