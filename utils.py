import json

import bcrypt

from databaseManagement.models.models import UserModel, PostModel, ContactModel

import dotenv
import os
import jwt

from schemas.Contact import Contact
from schemas.Post import PostWithUser
from schemas.User import User

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
        "role": user.role.value
    },
        key=ENCODE_KEY,
        algorithm="HS256")


def decodeJWT(token):
    return jwt.decode(token, key=ENCODE_KEY, algorithms=["HS256"])


def userToDTO(user: UserModel):
    return User(userId=str(user.userId), username=user.username, email=user.email, role=user.role.name)


def postToDTO(post: PostModel) -> PostWithUser:
    return PostWithUser(postId=str(post.postId), title=post.title, content=post.content,
                        creationDate=post.creationDate,
                        filepath=post.filePath, username=post.user.username, userId=str(post.userId))


def contactToDTO(contact: ContactModel):
    return Contact(contactId=str(contact.contactId), name=contact.name, email=contact.email, message=contact.message,
                   creationDate=contact.creationDate)


def getTextFromPostContent(content: str) -> str:
    jsonContent = json.loads(content)
    text = ""
    for block in jsonContent["blocks"]:
        if block["text"]:
            text += block["text"] + "\n"
    return text
