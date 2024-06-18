import uuid

import utils
from Exceptions.Exceptions import UserException
from Repository.UserRepository import UserRepository
from schemas.User import UserCreate, Login


class UserService:
    def __init__(self):
        self.repository = UserRepository()

    def authenticateUser(self, user: UserCreate):
        if self.repository.getUserByEmail(user.email) is not None:
            raise UserException("Email address already exists")
        if self.repository.getUserByUsername(user.username) is not None:
            raise UserException("Username already exists")
        dbUser = self.repository.createUser(user)
        token = utils.encodeUserToJWT(dbUser)
        userDto = utils.userToDTO(dbUser)
        return token, userDto

    def loginUser(self, loginCredentials: Login):
        dbUser = self.repository.checkForIdentifier(loginCredentials.username)
        if dbUser is None:
            raise UserException("User and password do not match")
        if not utils.checkPassword(loginCredentials.password, dbUser.hashedPassword):
            raise UserException("User and password do not match")
        token = utils.encodeUserToJWT(dbUser)
        return token, dbUser.role

    def getUsers(self):
        users = self.repository.getUsers()
        return [utils.userToDTO(user) for user in users]

    def promoteUser(self, userId: str):
        user = self.repository.getUserById(uuid.UUID(userId))
        if user is None:
            raise UserException("User not found")
        user = self.repository.makeUserAdmin(user.userId)
        return utils.userToDTO(user)

    def deleteUser(self, userId: str):
        user = self.repository.getUserById(uuid.UUID(userId))
        if user is None:
            raise UserException("User not found")
        user = self.repository.deleteUser(user.userId)
        return utils.userToDTO(user)



