from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Produk(Base):
    __tablename__ = "produk"
    id=Column(Integer, primary_key=True, index=True)
    created_at=Column(DateTime,server_default=func.now())
    updated_at=Column(DateTime,server_default=func.now(),onupdate=func.now())
    deleted_at=Column(DateTime,nullable=True,index=True) # this is soft delete column
    nama_produk=Column(String(255),nullable=False)
    slug=Column(String(255),nullable=False)
    harga_seller=Column(Integer)
    harga_konsumen=Column(Integer)
    stok=Column(Integer)
    deskripsi=Column(String(1000))
    toko_id=Column(Integer,ForeignKey("toko.id"))
    category_id=Column(Integer,ForeignKey("category.id"))
    toko=relationship("Toko")
    category=relationship("Category")
    photos=relationship("FotoProduk",back_populates="produk")
