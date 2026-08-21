from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class FotoProduk(Base):
    __tablename__ = "foto_produk"
    id=Column(Integer, primary_key=True, index=True)
    created_at=Column(DateTime,server_default=func.now())
    updated_at=Column(DateTime,server_default=func.now(),onupdate=func.now())
    deleted_at=Column(DateTime,nullable=True,index=True) # this is soft delete column
    url_foto=Column(String(255),nullable=False)
    produk_id=Column(Integer,ForeignKey("produk.id"))
    produk=relationship("Produk",back_populates="photos")