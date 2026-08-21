from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Category(Base):
    __tablename__ = "category"
    id=Column(Integer, primary_key=True, index=True)
    created_at=Column(DateTime,server_default=func.now())
    updated_at=Column(DateTime,server_default=func.now(),onupdate=func.now())
    deleted_at=Column(DateTime,nullable=True,index=True) # this is soft delete column
    nama_category=Column(String(255),nullable=False)
    