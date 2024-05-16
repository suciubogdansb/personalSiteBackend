import uuid

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidSignatureError
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

import utils
from databaseManagement.database import engine, SessionLocal
from databaseManagement.models import models
from databaseManagement.models.models import PostModel
from schemas.User import User, UserCreate, Login
from schemas.Post import PostWithUser, PostBase, PostCreate, Post
from service import Service

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost",
    f"http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = Service()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def getDb():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/check", status_code=200)
def check():
    return {"message": "Ok"}


@app.post("/authenticate")
def createUser(user: UserCreate, db: Session = Depends(getDb)):
    if service.getUserByEmail(user.email, db) is not None:
        raise HTTPException(status_code=400, detail="Email address already exists")
    if service.getUserByUsername(user.username, db) is not None:
        raise HTTPException(status_code=400, detail="Username already exists")
    dbUser = service.createUser(user, db)
    token = utils.encodeUserToJWT(dbUser)
    return {"message": "User created", "token": token}


@app.post("/login")
def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(getDb)):
    dbUser = service.getUserByUsername(user.username, db)
    if dbUser:
        if utils.checkPassword(user.password, dbUser.hashedPassword):
            token = utils.encodeUserToJWT(dbUser)
            return {"message": "Login successful", "token": token}
        raise HTTPException(status_code=400, detail="User and password do not match")
    else:
        dbUser = service.getUserByEmail(user.username, db)
        if dbUser:
            if utils.checkPassword(user.password, dbUser.hashedPassword):
                token = utils.encodeUserToJWT(dbUser)
                return {"message": "Login successful", "token": token}
            raise HTTPException(status_code=400, detail="User and password do not match")
        raise HTTPException(status_code=404, detail="User and password do not match")


@app.get("/posts", response_model=list[PostWithUser])
def getPosts(db: Session = Depends(getDb)):
    posts = service.getPosts(db)
    postsWithUser = [
        PostWithUser(title=post.title, content=post.content, postId=str(post.postId), username=post.user.username)
        for post in posts
    ]
    return postsWithUser


@app.post("/posts", status_code=201)
def addPost(post: PostBase, token: str, db: Session = Depends(getDb)):
    try:
        userPayload = utils.decodeJWT(token)
    except InvalidSignatureError as e:
        raise HTTPException(status_code=401, detail=str(e))
    userDb = service.getUserById(uuid.UUID(userPayload["userId"]), db)
    if userDb is None:
        raise HTTPException(status_code=404, detail="User not found")
    postCreate = PostCreate(title=post.title, content=post.content, userId=userPayload["userId"])
    dbPost = service.addPost(postCreate, db)
    return {"postId": str(dbPost.postId), "username": userDb.username}

@app.get("/posts/{token}", response_model=list[Post])
def getPostsByUser(token: str, db: Session = Depends(getDb)):
    try:
        user = utils.decodeJWT(token)
    except InvalidSignatureError as e:
        raise HTTPException(status_code=401, detail=str(e))
    if service.getUserById(uuid.UUID(user["userId"]), db) is None:
        raise HTTPException(status_code=404, detail="User not found")
    posts = service.getPostsByUserId(uuid.UUID(user["userId"]), db)
    postsSchemas = [
        Post(title=post.title, content=post.content, postId=str(post.postId))
        for post in posts
    ]
    return postsSchemas
