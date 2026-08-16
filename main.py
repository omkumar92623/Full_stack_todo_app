from fastapi import FastAPI, Depends,HTTPException
from sqlalchemy import create_engine,Column,Integer,VARCHAR,Boolean
from sqlalchemy.orm import DeclarativeBase,Session,sessionmaker
from typing import Annotated 

import os
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

engine = create_engine(
    DATABASE_URL
)

SessionLocal = sessionmaker(autoflush=False,autocommit = False,bind=engine)

class Base(DeclarativeBase):
    pass

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer,primary_key= True,index = True)
    title = Column(VARCHAR(100))
    completed = Column(Boolean,default=False)

Base.metadata.create_all(bind=engine)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

DBSession = Annotated[Session,Depends(get_db)]

@app.post("/todos")
def create_todo(title:str,db:DBSession):
    todo = Todo(title=title)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return{
        "Msg" : "todo created",
        "Data" : todo
    }

@app.get("/todos/{todo_id}")
def get_todo(todo_id:int,db:DBSession):

    todo = db.query(Todo).filter(todo_id == Todo.id).first()
    if not todo:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )
    return todo

@app.get("/todos")
def read_all(db:DBSession):
    todo = db.query(Todo).all()
    return{
        "Data" : todo
    }


@app.put("/todos/{todo_id}")
def update_todo(todo_id:int,completed:bool,db:DBSession):
    todo = db.query(Todo).filter(todo_id == Todo.id).first()
    if not todo:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )
    todo.completed = completed
    db.commit()
    db.refresh(todo)
    return{
        "Msg" : "Todo updated",
        "data" : todo
    }

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id:int,db:DBSession):
    todo = db.query(Todo).filter(todo_id == Todo.id).first()
    if not todo:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    
    db.delete(todo)
    db.commit()

    return{
        "Msg" : "Todo deleted",
        "Data" : todo
    }