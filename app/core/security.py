from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain:str):
    return pwd_context.hash(plain)

def validate_password(plain:str,hash:str):
    decoded=pwd_context.verify(plain,hash)
    return decoded

def create_access_token(user_id:int,email:str,is_admin:int):
    payload_dict={"user_id":user_id,"email":email,"is_admin":is_admin, "exp":datetime.now(timezone.utc) + timedelta(hours=24)}

    return jwt.encode(payload_dict, settings.JWT_SECRET, algorithm="HS256")

def decode_token(token: str):
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])