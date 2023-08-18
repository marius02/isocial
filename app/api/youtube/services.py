from sqlalchemy.orm import Session
from db.models.youtube import YouTubeComment
from db.repositories.youtube_repository import YouTubeRepository


class YouTubeService:
    def __init__(self, db: Session):
        self.db = db
        self.youtube_repo = YouTubeRepository(db)

    def save_comment(self, comment: str):
        comment = YouTubeComment(text=comment)
        self.youtube_repo.create_comment(comment)
