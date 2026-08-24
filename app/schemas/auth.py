from pydantic import BaseModel, ConfigDict
from datetime import date

class RegisterRequest(BaseModel):
    nama:str
    kata_sandi:str
    no_telp: str
    email: str
    tanggal_lahir: date | None=None
    jenis_kelamin: str | None=None
    tentang: str | None=None
    pekerjaan: str | None=None
    provinsi: str | None=None
    kota: str | None=None

class LoginRequest(BaseModel):
    no_telp: str
    kata_sandi: str

class UserResponse(BaseModel):
    id: int
    nama: str
    no_telp: str
    email: str
    is_admin: int
    token: str | None=None
    model_config=ConfigDict(from_attributes=True)