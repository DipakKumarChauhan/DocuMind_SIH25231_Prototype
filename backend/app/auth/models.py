from sqlalchemy import Column,String,DateTime
from sqlalchemy.sql import func
from app.db.base import Base
import uuid


class User(Base):
    __tablename__= "users"

    id = Column(String,primary_key=True,default=lambda:str(uuid.uuid4()))
    email = Column(String,unique=True,index=True,nullable=False)
    google_sub = Column(String,unique=True,nullable=False)
    name = Column(String,nullable=True)
    created_at = Column(DateTime(timezone=True),server_default=func.now())


