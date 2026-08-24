from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class DetailTrx(Base):
    __tablename__ = "detail_trx"
    id=Column(Integer, primary_key=True, index=True)
    created_at=Column(DateTime,server_default=func.now())
    updated_at=Column(DateTime,server_default=func.now(),onupdate=func.now())
    deleted_at=Column(DateTime,nullable=True,index=True) # this is soft delete column
    trx_id=Column(Integer,ForeignKey("trx.id"))
    log_produk_id=Column(Integer,ForeignKey("log_produk.id"))
    toko_id=Column(Integer,ForeignKey("toko.id"))
    kuantitas=Column(Integer,nullable=False)
    harga_total=Column(Integer,nullable=False)
    log_produk=relationship("LogProduk")
    toko=relationship("Toko")
    trx = relationship("Trx", back_populates="detail_trx")