from fastapi import FastAPI
from app.routers import auth

app=FastAPI(title="Mini Shop")
app.include_router(auth.router)
