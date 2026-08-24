from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Toko(Base):
    __tablename__ = "toko"
    id=Column(Integer, primary_key=True, index=True)
    created_at=Column(DateTime,server_default=func.now())
    updated_at=Column(DateTime,server_default=func.now(),onupdate=func.now())
    deleted_at=Column(DateTime,nullable=True,index=True) # this is soft delete column
    nama_toko=Column(String(255),nullable=False)
    url_foto=Column(String(255),nullable=True)
    user_id=Column(Integer,ForeignKey("user.id"))
    user=relationship("User")