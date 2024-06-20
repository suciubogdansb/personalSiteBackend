import uuid
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

import utils
from databaseManagement.database import SessionLocal
from databaseManagement.models.models import UserModel
from schemas.Role import Role
from schemas.User import UserCreate


class UserRepository:
    def __init__(self):
        self.__db: Session = SessionLocal()

    def getUserByUsername(self, userName: str):
        return self.__db.query(UserModel).filter(UserModel.username == userName).first()

    def getUserByEmail(self, email: str):
        return self.__db.query(UserModel).filter(UserModel.email == email).first()

    def checkForIdentifier(self, identifier: str):
        return self.__db.query(UserModel).filter(
            UserModel.email == identifier or UserModel.username == identifier).first()

    def getUserById(self, id: UUID):
        return self.__db.query(UserModel).filter(UserModel.userId == id).first()

    def createUser(self, user: UserCreate):
        hashedPassword = utils.hashPassword(user.password)
        dbUser = UserModel(username=user.username, email=user.email, hashedPassword=hashedPassword,
                           userId=uuid.uuid4(), )
        self.__db.add(dbUser)
        self.__db.commit()
        self.__db.refresh(dbUser)
        return dbUser

    def getUsers(self):
        return self.__db.query(UserModel).all()

    def makeUserAdmin(self, userId: UUID):
        user = self.getUserById(userId)
        user.role = Role.ADMIN
        self.__db.commit()
        return user

    def deleteUser(self, userId: UUID):
        user = self.getUserById(userId)
        self.__db.delete(user)
        self.__db.commit()
        return user
