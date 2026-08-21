from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "user"
    id=Column(Integer, primary_key=True, index=True)
    created_at=Column(DateTime,server_default=func.now())
    updated_at=Column(DateTime,server_default=func.now(),onupdate=func.now())
    deleted_at=Column(DateTime,nullable=True,index=True) # this is soft delete column
    nama=Column(String(255),nullable=False)
    kata_sandi=Column(String(255),nullable=False)
    no_telp=Column(String(20),nullable=False, unique=True)
    tanggal_lahir=Column(DateTime,nullable=False)
    jenis_kelamin=Column(String(10),nullable=False)
    tentang=Column(String(1000),nullable=True)
    pekerjaan=Column(String(255),nullable=True)
    email=Column(String(255),nullable=False,unique=True)
    provinsi=Column(String(255),nullable=True)
    kota=Column(String(255),nullable=True)
    is_admin=Column(Integer,nullable=False,default=0) # 0 = user biasa, 1 = admin