from fastapi import Depends , HTTPException
from fastapi.security import OAuth2PasswordBearer , HTTPBearer, HTTPAuthorizationCredentials

from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.config import settings
from app.db.session import SessionLocal
from app.auth.models import User
from app.auth.security import SECRET_KEY, ALGORITHM

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/google")
security = HTTPBearer()

# Dependency to get DB session Starts the session and closes after the request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    # token:str = Depends(oauth2_scheme), # this one when using OAuth2PasswordBearer
    credentials: HTTPAuthorizationCredentials = Depends(security), # this one when using HTTPBearer
    db: Session = Depends(get_db)
)->User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )
        
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )
    
    user = db.query(User).filter(User.id ==user_id).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )
    
    return user