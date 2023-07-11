from sqlalchemy.orm import Session
from db.models.twitter import TwitterReply


class TwitterRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_reply(self, reply: TwitterReply):
        self.db.add(reply)
        self.db.commit()
        self.db.refresh(reply)
