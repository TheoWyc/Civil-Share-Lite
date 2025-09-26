from sqlalchemy import Column, Integer, String
from database import Base

class Notes(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    save_name = Column(String)
    color = Column(Integer)
    height = Column(Integer)
    width = Column(Integer)
    content = Column(String)
    posX = Column(Integer)
    posY = Column(Integer)