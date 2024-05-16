import uuid

from sqlalchemy.orm import Session

import utils
from databaseManagement.models import models
from databaseManagement.models.models import UserModel
from schemas.Post import PostCreate
from schemas.User import UserCreate


class Service:
    def getUserByUsername(self, userName: str, db: Session):
        return db.query(UserModel).filter(UserModel.username == userName).first()

    def getUserByEmail(self, email: str, db: Session):
        return db.query(UserModel).filter(UserModel.email == email).first()

    def createUser(self, user: UserCreate, db: Session):
        hashedPassword = utils.hashPassword(user.password)
        dbUser = UserModel(username=user.username, email=user.email, hashedPassword=hashedPassword, userId=uuid.uuid4())
        db.add(dbUser)
        db.commit()
        db.refresh(dbUser)
        return dbUser

    def getUserById(self, userId: uuid.UUID, db: Session):
        return db.query(UserModel).filter(UserModel.userId == userId).first()

    def getPostsByUserId(self, userId: uuid.UUID, db: Session):
        return db.query(models.PostModel).filter(models.PostModel.userId == userId).all()

    def getPosts(self, db: Session):
        return db.query(models.PostModel).all()

    def addPost(self, post: PostCreate, db: Session):
        dbPost = models.PostModel(title=post.title, content=post.content, userId=uuid.UUID(post.userId), postId=uuid.uuid4())
        db.add(dbPost)
        db.commit()
        db.refresh(dbPost)
        return dbPost
