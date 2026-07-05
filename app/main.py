from fastapi import FastAPI
from fastapi import APIRouter
from core.auth import auth_router

app = FastAPI()


app.include_router(auth_router)
