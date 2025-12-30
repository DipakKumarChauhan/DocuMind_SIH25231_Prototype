from datetime import datetime, timedelta
from jose import jwt
from app.config import settings

SECRET_KEY= settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_DAYS = settings.JWT_ACCESS_TOKEN_EXPIRE_DAYS

def create_access_token(data:dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp":expire})


    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)