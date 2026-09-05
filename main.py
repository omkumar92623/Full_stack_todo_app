from fastapi import FastAPI, Depends,HTTPException,Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine,Column,Integer,VARCHAR,Boolean
from sqlalchemy.orm import DeclarativeBase,Session,sessionmaker
from typing import Annotated 
from pydantic import BaseModel
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from limiter import limiter
from config import settings

app = FastAPI()
app.state.limiter = limiter

origins = settings.ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



DATABASE_URL = (
    f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
    f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
)

engine = create_engine(
    DATABASE_URL
)

SessionLocal = sessionmaker(autoflush=False,autocommit = False,bind=engine)

class Base(DeclarativeBase):
    pass

class Create_Todo(BaseModel):
    title:str

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


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request:Request, exc:RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests"
        })


@app.post("/todos")
@limiter.limit("5/minute")
def create_todo(request:Request,title:Create_Todo,db:DBSession):
    todo = Todo(title=title.title)
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
    todos = db.query(Todo).all()
    return {
        "Data": [
            {
                "id": todo.id,
                "title": todo.title,
                "completed": todo.completed
            }
            for todo in todos
        ]
    }


@app.put("/todos/{todo_id}")
@limiter.limit("5/minute")
def update_todo(request:Request,todo_id:int,completed:bool,db:DBSession):
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