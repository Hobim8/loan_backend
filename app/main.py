from fastapi import FastAPI 
from fastapi import APIRouter

app = FastAPI()  
auth = APIRouter() 

app.include_router(auth)  

