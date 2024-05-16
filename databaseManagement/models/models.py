from sqlalchemy import Column, UUID, String, ForeignKey
from sqlalchemy.orm import relationship

from databaseManagement.database import Base


class UserModel(Base):
    __tablename__ = "users"

    userId = Column(UUID, primary_key=True)
    username = Column(String, unique=True, index=True)
    hashedPassword = Column(String)
    email = Column(String, unique=True, index=True)

    posts = relationship("PostModel", back_populates="user")


class PostModel(Base):
    __tablename__ = "posts"

    postId = Column(UUID, primary_key=True)
    title = Column(String)
    content = Column(String)
    userId = Column(UUID, ForeignKey("users.userId", onupdate="CASCADE", ondelete="CASCADE"), index=True)

    user = relationship("UserModel", back_populates="posts")
