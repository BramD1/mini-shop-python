from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Alamat(Base):
    __tablename__ = "alamat"
    id=Column(Integer, primary_key=True, index=True)
    created_at=Column(DateTime,server_default=func.now())
    updated_at=Column(DateTime,server_default=func.now(),onupdate=func.now())
    deleted_at=Column(DateTime,nullable=True,index=True) # this is soft delete column
    judul_alamat=Column(String(255),nullable=False)
    nama_penerima=Column(String(255),nullable=False)
    no_telp=Column(String(20),nullable=False)
    detail_alamat=Column(String(1000),nullable=False)
    user_id=Column(Integer,ForeignKey("user.id"))
    user=relationship("User")