import uuid

import utils
from Exceptions.Exceptions import UserException
from Repository.UserRepository import UserRepository
from schemas.User import UserCreate, Login


class UserService:
    def __init__(self, repository: UserRepository = None):
        self.__repository = repository if repository is not None else UserRepository()

    def authenticateUser(self, user: UserCreate):
        if self.__repository.getUserByEmail(user.email) is not None:
            raise UserException("Email address already exists")
        if self.__repository.getUserByUsername(user.username) is not None:
            raise UserException("Username already exists")
        dbUser = self.__repository.createUser(user)
        token = utils.encodeUserToJWT(dbUser)
        userDto = utils.userToDTO(dbUser)
        return token, userDto

    def loginUser(self, loginCredentials: Login):
        dbUser = self.__repository.checkForIdentifier(loginCredentials.username)
        if dbUser is None:
            raise UserException("User and password do not match")
        if not utils.checkPassword(loginCredentials.password, dbUser.hashedPassword):
            raise UserException("User and password do not match")
        token = utils.encodeUserToJWT(dbUser)
        return token, dbUser.role

    def getUsers(self):
        users = self.__repository.getUsers()
        return [utils.userToDTO(user) for user in users]

    def promoteUser(self, userId: str):
        user = self.__repository.getUserById(uuid.UUID(userId))
        if user is None:
            raise UserException("User not found")
        user = self.__repository.makeUserAdmin(user.userId)
        return utils.userToDTO(user)

    def deleteUser(self, userId: str):
        user = self.__repository.getUserById(uuid.UUID(userId))
        if user is None:
            raise UserException("User not found")
        user = self.__repository.deleteUser(user.userId)
        return utils.userToDTO(user)



