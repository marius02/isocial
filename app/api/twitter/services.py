from sqlalchemy.orm import Session
from db.models.twitter import TwitterReply
from db.repositories.twitter_repository import TwitterRepository


class TwitterService:
    def __init__(self, db: Session):
        self.db = db
        self.twitter_repo = TwitterRepository(db)

    def save_reply(self, message: str):
        reply = TwitterReply(message=message)
        self.twitter_repo.create_reply(reply)
