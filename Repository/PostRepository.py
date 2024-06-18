import uuid
from uuid import UUID

from sqlalchemy.orm import Session

from databaseManagement.database import SessionLocal
from databaseManagement.models.models import PostModel
from schemas.Post import PostCreate


class PostRepository:
    def __init__(self):
        self.db: Session = SessionLocal()

    def getPosts(self):
        return self.db.query(PostModel).all()

    def getPostById(self, postId: UUID):
        return self.db.query(PostModel).filter(PostModel.postId == postId).first()

    def getPostsByUserId(self, userId: UUID):
        return self.db.query(PostModel).filter(PostModel.userId == userId).all()

    def addPost(self, post: PostCreate, postId: UUID):
        dbPost = PostModel(postId=postId, title=post.title, content=post.content, userId=uuid.UUID(post.userId),
                           filePath=post.filepath)
        self.db.add(dbPost)
        self.db.commit()
        self.db.refresh(dbPost)
        return dbPost

    def deletePost(self, postId: UUID):
        post = self.db.query(PostModel).filter(PostModel.postId == postId).first()
        if post is None:
            raise Exception("Post not found")
        self.db.delete(post)
        self.db.commit()
        return post

    def updatePost(self, post: PostCreate, postId: UUID):
        dbPost = self.db.query(PostModel).filter(PostModel.postId == postId).first()
        if dbPost is None:
            raise Exception("Post not found")
        dbPost.title = post.title
        dbPost.content = post.content
        if post.filepath is not None:
            dbPost.filePath = post.filepath
        self.db.commit()
        self.db.refresh(dbPost)
        return dbPost

    def getPostsFiltered(self, filter: str):
        filter_string = f"%{filter}%"
        return self.db.query(PostModel).filter(PostModel.title.ilike(filter_string)).all()

    def getPostsSortedByAge(self, filter: str):
        filter_string = f"%{filter}%"
        return self.db.query(PostModel).filter(PostModel.title.ilike(filter_string)).order_by(
            PostModel.creationDate).all()

    def getPostsSortedByTitle(self, filter: str):
        filter_string = f"%{filter}%"
        return self.db.query(PostModel).filter(PostModel.title.ilike(filter_string)).order_by(
            PostModel.title).all()

    def getPostsSortedByAgeDesc(self, filter: str):
        filter_string = f"%{filter}%"
        return self.db.query(PostModel).filter(PostModel.title.ilike(filter_string)).order_by(
            PostModel.creationDate.desc()).all()

    def getPostsSortedByTitleDesc(self, filter: str):
        filter_string = f"%{filter}%"
        return self.db.query(PostModel).filter(PostModel.title.ilike(filter_string)).order_by(
            PostModel.title.desc()).all()

