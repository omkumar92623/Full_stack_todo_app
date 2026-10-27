from typing import Annotated, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from slowapi.errors import RateLimitExceeded
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from Auth import CurrentUser, create_access_token, hash_password, verify_password
from config import settings
from database import Base, engine, get_db
from limiter import limiter
from models import Todo, User
from schema import Create_Todo, Token, Update_Todo, UserCreate, UserResponse

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

DBSession = Annotated[Session, Depends(get_db)]

Base.metadata.create_all(bind=engine)


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"},
    )

#  Authentication Routes (Create User & Login)

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: DBSession):
    """
    Register a new user: checks if username or email already exists,
    hashes password, and saves the user using SQLAlchemy 2.0.
    """
    stmt = select(User).where(
        or_(User.username == user_data.username, User.email == user_data.email)
    )
    existing_user = db.scalar(stmt)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DBSession,
):
    """
    Authenticate user credentials, return JWT access token.
    Compatible with Swagger UI 'Authorize' button.
    """
    stmt = select(User).where(User.username == form_data.username)
    user = db.scalar(stmt)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


#  Todo Routes (Protected by CurrentUser dependency)


@app.post("/todos")
@limiter.limit("5/minute")
def create_todo(
    request: Request,
    title: Create_Todo,
    db: DBSession,
    current_user: CurrentUser,
):
    todo = Todo(title=title.title, user_id=current_user.id)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return {
        "Msg": "todo created",
        "Data": todo,
    }


@app.get("/todos/{todo_id}")
def get_todo(
    todo_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    stmt = select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    todo = db.scalar(stmt)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )
    return todo


@app.get("/todos")
def read_all(
    db: DBSession,
    current_user: CurrentUser,
):
    stmt = select(Todo).where(Todo.user_id == current_user.id)
    todos = db.scalars(stmt).all()
    return {
        "Data": [
            {
                "id": todo.id,
                "title": todo.title,
                "completed": todo.completed,
            }
            for todo in todos
        ]
    }


@app.put("/todos/{todo_id}")
@limiter.limit("5/minute")
def update_todo(
    request: Request,
    todo_id: int,
    db: DBSession,
    current_user: CurrentUser,
    todo_data: Optional[Update_Todo] = None,
    completed: Optional[bool] = None,
):
    stmt = select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    todo = db.scalar(stmt)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    if todo_data and todo_data.title is not None:
        todo.title = todo_data.title
    if todo_data and todo_data.completed is not None:
        todo.completed = todo_data.completed
    elif completed is not None:
        todo.completed = completed

    db.commit()
    db.refresh(todo)
    return {
        "Msg": "Todo updated",
        "Data": {
            "id": todo.id,
            "title": todo.title,
            "completed": todo.completed,
        },
    }


@app.delete("/todos/{todo_id}")
def delete_todo(
    todo_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    stmt = select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    todo = db.scalar(stmt)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    db.delete(todo)
    db.commit()

    return {
        "Msg": "Todo deleted",
        "Data": todo,
    }