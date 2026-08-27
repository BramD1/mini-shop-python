from fastapi import FastAPI
from app.routers import auth, user,category,alamat

app=FastAPI(title="Mini Shop")
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(category.router)
app.include_router(alamat.router)

