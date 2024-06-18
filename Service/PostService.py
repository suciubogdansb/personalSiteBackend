import uuid
from uuid import UUID

from fastapi import UploadFile

import utils
from Repository.PostRepository import PostRepository
from Repository.UserRepository import UserRepository
from schemas.Post import PostCreate


class PostService:

    def __init__(self):
        self.repository = PostRepository()
        self.userRepository = UserRepository()

        self.__filterOptions = {
            "Default": self.repository.getPostsFiltered,
            "A->Z": self.repository.getPostsSortedByTitle,
            "Z->A": self.repository.getPostsSortedByTitleDesc,
            "Oldest": self.repository.getPostsSortedByAge,
            "Newest": self.repository.getPostsSortedByAgeDesc
        }

    def getAll(self):
        posts = self.repository.getPosts()
        return [utils.postToDTO(post) for post in posts]

    def getById(self, id: UUID):
        post = self.repository.getPostById(id)
        if not post:
            raise Exception("Post not found")
        return utils.postToDTO(post)

    def getByUserId(self, id: UUID):
        return self.repository.getPostsByUserId(id)

    async def createPost(self, token: str, title: str, content: str, image: UploadFile):
        try:
            userPayload = utils.decodeJWT(token)
        except Exception as e:
            raise Exception(str(e))

        postId = uuid.uuid4()

        user = self.userRepository.getUserById(uuid.UUID(userPayload["userId"]))
        if not user:
            raise Exception("User not found")

        filepath = None

        if image:
            if not image.filename.endswith((".jpg", ".jpeg", ".png")):
                raise Exception("Invalid file format")
            filepath = f"images/{postId}_{image.filename}"
            with open(filepath, "wb") as image_file:
                imageContent = await image.read()
                image_file.write(imageContent)

        post = PostCreate(title=title, content=content, userId=userPayload["userId"], filepath=filepath)
        dbPost = self.repository.addPost(post, postId)
        return utils.postToDTO(dbPost)

    def deletePost(self, postId: UUID):
        post = self.repository.deletePost(postId)

    def getImage(self, postId: UUID):
        post = self.repository.getPostById(postId)
        if not post:
            raise Exception("Post not found")
        return post.filePath

    async def updatePost(self, postId: UUID, token: str, title: str, content: str, image: UploadFile):
        post = self.repository.getPostById(postId)
        if not post:
            raise Exception("Post not found")

        try:
            userPayload = utils.decodeJWT(token)
        except Exception as e:
            raise Exception(str(e))

        user = self.userRepository.getUserById(uuid.UUID(userPayload["userId"]))
        if not user:
            raise Exception("User not found")

        if post.userId != user.userId:
            raise Exception("Unauthorized")

        filepath = None

        if image:
            if not image.filename.endswith((".jpg", ".jpeg", ".png")):
                raise Exception("Invalid file format")
            filepath = f"images/{postId}_{image.filename}"
            with open(filepath, "wb") as image_file:
                imageContent = await image.read()
                image_file.write(imageContent)

        post = PostCreate(title=title, content=content, userId=userPayload["userId"], filepath=filepath)
        dbPost = self.repository.updatePost(post, postId)
        return utils.postToDTO(dbPost)

    def getPostsByFilter(self, filtered, option):
        print("Filter: ", filtered)
        if option not in self.__filterOptions:
            raise Exception("Invalid filter option")
        print("Option: ", option)
        posts = self.__filterOptions[option](filtered)
        print("Posts: ", posts)
        return [utils.postToDTO(post) for post in posts]



