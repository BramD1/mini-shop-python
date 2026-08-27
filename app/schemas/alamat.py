from pydantic import BaseModel, ConfigDict

class AlamatCreate(BaseModel):
    judul_alamat: str
    nama_penerima: str
    no_telp: str
    detail_alamat: str

class AlamatResponse(BaseModel):
    id: int
    judul_alamat:str
    nama_penerima: str
    no_telp: str
    detail_alamat: str
    model_config=ConfigDict(from_attributes=True)