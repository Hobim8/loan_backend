from fastapi import FastAPI
from core.auth import auth_router
from routes.loan import loan_route

app = FastAPI()


app.include_router(auth_router)
app.include_router(loan_route)
