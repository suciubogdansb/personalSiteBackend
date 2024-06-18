from pydantic import BaseModel

from schemas.Role import Role


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class UserGet(UserBase):
    postCount: int


class User(UserBase):
    userId: str
    role: str

    def toJSON(self):
        return {
            "userId": self.userId,
            "username": self.username,
            "email": self.email,
            "role": self.role,
        }

    class Config:
        orm_mode = True


class Login(BaseModel):
    username: str
    password: str
