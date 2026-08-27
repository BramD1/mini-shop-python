from pydantic import BaseModel, ConfigDict

class CategoryCreate(BaseModel):
    nama_category: str

class CategoryResponse(BaseModel):
    id: int
    nama_category: str
    model_config = ConfigDict(from_attributes=True)