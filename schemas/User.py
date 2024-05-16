from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    userId: str

    def toJSON(self):
        return {
            "userId": self.userId,
            "username": self.username,
            "email": self.email
        }

    class Config:
        orm_mode = True


class Login(BaseModel):
    username: str
    password: str



