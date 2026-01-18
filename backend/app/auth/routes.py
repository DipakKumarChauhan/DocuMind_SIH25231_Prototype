from fastapi import APIRouter, HTTPException,Depends
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests

from app.db.session import SessionLocal
from app.auth.models import User
from app.config import settings
from app.auth.security import create_access_token

router = APIRouter(prefix="/auth",tags=["AUTH"])

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID

# Dependency to get DB session Starts the session and closes after the request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("google")
def google_login(id_token_str:str, db:Session = Depends(get_db)):
    
    # try validates Google ID token and retrieves user info.
    try: 
        idinfo = id_token.verify_oauth2_token(
            id_token_str,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )


    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid Google token")
    

    email = idinfo["email"] # Extract email from token google sent 

    sub= idinfo["sub"]  # Unique Google user ID
                        # 'sub' full form is 'subject' and is the ID of the person the token belongs to and is a unique Id issued by google in our case. 

    name= idinfo.get("name")    # Optional name field

    user = db.query(User).filter(User.google_sub == sub).first() # Check if user exists in the db by using unique sub given by google

    print(f"[DEBUG AUTH] Email: {email}, Google Sub: {sub}")
    
    # Check for all users with this email
    all_users_with_email = db.query(User).filter(User.email == email).all()
    print(f"[DEBUG AUTH] Total users with this email: {len(all_users_with_email)}")
    for u in all_users_with_email:
        print(f"  - ID: {u.id}, google_sub: {u.google_sub}")
    
    print(f"[DEBUG AUTH] Existing user found by google_sub: {user}")
    
    if not user:
        # create a new user if it doesnot exists

        user = User(email=email,google_sub=sub,name=name)
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"[DEBUG AUTH] New user created with ID: {user.id}")
    else:
        print(f"[DEBUG AUTH] Existing user retrieved with ID: {user.id}")

    # Create JWT token for the user
    token = create_access_token({"sub":user.id})

    return {"access_token": token}





