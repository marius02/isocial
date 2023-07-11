# db/repositories/facebook_repository.py
from sqlalchemy.orm import Session
from db.models.facebook import FacebookComment


class FacebookRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_comment(self, comment: FacebookComment):
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
