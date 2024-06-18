from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import DateTime


class PostBase(BaseModel):
    title: str
    content: str
    filepath: str | None


class Post(PostBase):
    postId: str
    creationDate: datetime

    def toJSON(self):
        return {
            "postId": self.postId,
            "title": self.title,
            "content": self.content,
            "creationDate": str(self.creationDate),
            "filepath": self.filepath
        }

    class Config:
        orm_mode = True


class PostWithUser(Post):
    username: str
    userId: str

    def toJSON(self):
        return {
            "postId": self.postId,
            "title": self.title,
            "content": self.content,
            "creationDate": str(self.creationDate),
            "filepath": self.filepath,
            "userId": self.userId,
            "username": self.username
        }


class PostCreate(PostBase):
    userId: str
