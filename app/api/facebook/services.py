from sqlalchemy.orm import Session
from db.models.facebook import FacebookComment
from db.repositories.facebook_repository import FacebookRepository


class FacebookService:
    def __init__(self, db: Session):
        self.db = db
        self.fb_repo = FacebookRepository(db)

    def save_comment(self, comment: str):
        comment = FacebookComment(text=comment)
        self.fb_repo.create_comment(comment)
