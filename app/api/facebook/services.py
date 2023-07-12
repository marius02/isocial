from sqlalchemy.orm import Session
from db.models.facebook import FacebookComment, FacebookPost
from db.repositories.facebook_repository import FacebookRepository


class FacebookService:
    def __init__(self, db: Session):
        self.db = db
        self.facebook_repo = FacebookRepository(db)

    def save_comment(self, comment: str):
        comment = FacebookComment(text=comment)
        self.facebook_repo.create_comment(comment)

    def save_post(self, post_url: str):
        post = FacebookPost(post_url=post_url)
        self.facebook_repo.create_post(post)
