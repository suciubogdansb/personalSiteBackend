from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    content: str


class Post(PostBase):
    postId: str

    def toJSON(self):
        return {
            "postId": self.postId,
            "title": self.title,
            "content": self.content,
        }

    class Config:
        orm_mode = True


class PostWithUser(Post):
    username: str

    def toJSON(self):
        return {
            "postId": self.postId,
            "title": self.title,
            "content": self.content,
            "username": self.username
        }


class PostCreate(PostBase):
    userId: str
