from sqlalchemy import Column,Integer,VARCHAR,Boolean
from database import Base

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer,primary_key= True,index = True)
    title = Column(VARCHAR(100))
    completed = Column(Boolean,default=False)