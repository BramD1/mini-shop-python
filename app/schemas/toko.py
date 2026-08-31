from pydantic import BaseModel, ConfigDict

class TokoResponse(BaseModel):
    id: int
    nama_toko: str
    url_foto: str|None=None
    user_id: int
    model_config=ConfigDict(from_attributes=True)