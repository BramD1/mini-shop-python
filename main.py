from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import auth, user, category, alamat, toko, produk, trx

app=FastAPI(title="Mini Shop")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(category.router)
app.include_router(alamat.router)
app.include_router(toko.router)
app.include_router(produk.router)
app.include_router(trx.router)