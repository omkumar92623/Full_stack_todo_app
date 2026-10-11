from sqlalchemy import String
from database import Base
from sqlalchemy.orm import Mapped, mapped_column

class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    title : Mapped[str] = mapped_column(String(30))
    completed : Mapped[bool] = mapped_column(default=False,server_default="0")