from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    UniqueConstraint,
    CheckConstraint,
)

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from .database import Base


class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    published: Mapped[bool] = mapped_column(
        Boolean, server_default='TRUE', nullable=False
    )

    # __table_args__ allows you to specify additional constraints and table-level options.
    __table_args__ = (
        # UniqueConstraint ensures that no two posts can have the same title.
        # This enforces a rule at the database level.
        UniqueConstraint('title'),
        # CheckConstraint ensures that the length of the 'content' field is greater than 10.
        # This prevents inserting posts with very short content. The `name` parameter
        # assigns a name to the constraint, making it easier to reference or debug.
        CheckConstraint('length(content) > 5', name='content_length_check'),
    )
