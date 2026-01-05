from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional 
from datetime import datetime 

class UserCreate(BaseModel):
    id: Optional[int]
    username: str = Field(..., min_length=3, max_length=50, description='username required')
    email: EmailStr = Field(..., description='valid email address')
    password_hased: str = Field(..., min_length=8, description='Password(min 8 characters)')
    is_active: Optional[bool]
    is_staff: Optional[bool]

    
class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description='username required')
    password_hased: str = Field(...,min_length=8, description= 'Password required')
    


    







