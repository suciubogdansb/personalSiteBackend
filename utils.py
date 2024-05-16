import bcrypt

from databaseManagement.models.models import UserModel

import dotenv
import os
import jwt

dotenv.load_dotenv()
ENCODE_KEY = os.getenv("ENCODE_KEY")


def hashPassword(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed


def checkPassword(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)


def encodeUserToJWT(user: UserModel):
    return jwt.encode(payload={
        "userId": str(user.userId),
        "email": user.email,
    },
        key=ENCODE_KEY,
        algorithm="HS256")


def decodeJWT(token):
    return jwt.decode(token, key=ENCODE_KEY, algorithms=["HS256"])
