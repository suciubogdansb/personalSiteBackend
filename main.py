import os
import uuid

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Form, UploadFile, File
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from Repository.PostRepository import PostRepository
from Repository.UserRepository import UserRepository
from Service.PostService import PostService
from Service.UserService import UserService
from Service.LLMService import LLMService
from databaseManagement.database import engine
from databaseManagement.models import models
from schemas.BotResponse import BotResponse
from schemas.User import User, UserCreate, Login
from schemas.Post import PostWithUser
import socketio

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

models.Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost",
    f"http://localhost:3000",
]

socketIo = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=origins)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists('images'):
    os.makedirs('images')

app.mount("/images", StaticFiles(directory="images"), name="images")


@socketIo.event
async def connect(sid, environ):
    print(f"connect {sid}")


@socketIo.event
async def disconnect(sid):
    print(f"disconnect {sid}")


@app.get("/check", status_code=200)
def check():
    return {"message": "Ok"}


userRepository = UserRepository()
postRepository = PostRepository()

userService = UserService(repository=userRepository)


@app.post("/authenticate")
async def createUser(user: UserCreate):
    try:
        token, userDto = userService.authenticateUser(user)
        await socketIo.emit("userCreated", {"user": userDto.toJSON()})
        return {"message": "User created", "user": userDto}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/login")
def login(user: Login):
    try:
        token, role = userService.loginUser(user)
        return {"message": "Logged in", "token": token, "role": role}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users", response_model=list[User])
def getUsers():
    users = userService.getUsers()
    return users


@app.put("/users/{userId}")
async def promoteUser(userId: str):
    try:
        user = userService.promoteUser(userId)
        await socketIo.emit("userPromoted", {"user": user.toJSON()})
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/users/{userId}", status_code=204)
async def deleteUser(userId: str):
    try:
        userService.deleteUser(userId)
        await socketIo.emit("userDeleted", {"userId": userId})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# @app.get("/posts", response_model=list[PostWithUser])
# def getPosts(db: Session = Depends(getDb)):
#     posts = service.getPosts(db)
#     postsWithUser = [
#         PostWithUser(title=post.title, content=post.content, postId=str(post.postId), username=post.user.username)
#         for post in posts
#     ]
#     return postsWithUser
#
#
# @app.post("/posts", status_code=201)
# def addPost(post: PostBase, token: str, db: Session = Depends(getDb)):
#     try:
#         userPayload = utils.decodeJWT(token)
#     except InvalidSignatureError as e:
#         raise HTTPException(status_code=401, detail=str(e))
#     userDb = service.getUserById(uuid.UUID(userPayload["userId"]), db)
#     if userDb is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     postCreate = PostCreate(title=post.title, content=post.content, userId=userPayload["userId"])
#     dbPost = service.addPost(postCreate, db)
#     return {"postId": str(dbPost.postId), "username": userDb.username}
#
#
# @app.get("/posts/{token}", response_model=list[Post])
# def getPostsByUser(token: str, db: Session = Depends(getDb)):
#     try:
#         user = utils.decodeJWT(token)
#     except InvalidSignatureError as e:
#         raise HTTPException(status_code=401, detail=str(e))
#     if service.getUserById(uuid.UUID(user["userId"]), db) is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     posts = service.getPostsByUserId(uuid.UUID(user["userId"]), db)
#     postsSchemas = [
#         Post(title=post.title, content=post.content, postId=str(post.postId))
#         for post in posts
#     ]
#     return postsSchemas


llmService = LLMService(postRepository=postRepository)

postService = PostService(repository=postRepository, userRepository=userRepository)


@app.get("/posts", response_model=list[PostWithUser])
def getPosts():
    posts = postService.getAll()
    return posts


@app.get("/posts/{postId}", response_model=PostWithUser)
def getPost(postId: str):
    try:
        post = postService.getById(uuid.UUID(postId))
        return post
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/posts", status_code=201)
async def addPost(token: str = Form(...),
                  title: str = Form(...),
                  content: str = Form(...),
                  image: UploadFile = File(None)):
    try:
        post = await postService.createPost(token, title, content, image)
        await socketIo.emit("postCreated", {"post": post.toJSON()})
        llmService.reloadChain()
        return post
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/posts/{postId}", status_code=204)
async def deletePost(postId: str):
    try:
        postService.deletePost(uuid.UUID(postId))
        await socketIo.emit("postDeleted", {"postId": postId})
        llmService.reloadChain()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/posts/{postId}")
async def updatePost(postId: str,
                     token: str = Form(...),
                     title: str = Form(...),
                     content: str = Form(...),
                     image: UploadFile = File(None)
                     ):
    try:
        post = await postService.updatePost(uuid.UUID(postId), token, title, content, image)
        await socketIo.emit("postUpdated", {"post": post.toJSON()})
        llmService.reloadChain()
        return post
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/posts/{postId}/image")
def getImage(postId: str, filler: str | None = None):
    try:
        image = postService.getImage(uuid.UUID(postId))
        if image:
            return FileResponse(image)
        return {"message": "No image"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/filter/posts", response_model=list[PostWithUser])
def getPostsByFilter(option: str, filtered: str = ""):
    try:
        posts = postService.getPostsByFilter(filtered, option)
        return posts
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/chat", response_model=BotResponse)
async def chat(request: BotResponse):
    try:
        response = await llmService.getResponse(request.message)
        botResponse = BotResponse(message=response, role="bot")
        return botResponse
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


socketApp = socketio.ASGIApp(socketIo, app)

if __name__ == "__main__":
    uvicorn.run(socketApp, host="0.0.0.0", port=8000)
