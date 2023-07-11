from sqlalchemy.orm import Session
from db.models.facebook import FacebookComment
from db.repositories.facebook_repository import FacebookRepository


class FacebookService:
    def __init__(self, db: Session):
        self.db = db
        self.facebook_repo = FacebookRepository(db)

    def save_comment(self, message: str):
        comment = FacebookComment(message=message)
        self.facebook_repo.create_comment(comment)
