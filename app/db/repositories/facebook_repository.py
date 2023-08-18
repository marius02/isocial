from sqlalchemy.orm import Session
from api.facebook.models import FacebookCommentCreate, FacebookCommentResponse
from db.models.facebook import FacebookComment
import uuid


class FacebookRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_comment(self, comment: FacebookCommentCreate):
        chatid = f"facebook_{uuid.uuid4()}"
        truncated_comments = comment.text[:2097]  # Truncate comments
        db_comment = FacebookComment(
            chatid=chatid,
            url=comment.url,
            text=truncated_comments,
        )
        self.db.add(db_comment)
        self.db.commit()
        self.db.refresh(db_comment)
        return db_comment

    def get_comments(self, chatid: str, skip: int = 0, limit: int = 10):
        return self.db.query(FacebookComment).filter(FacebookComment.chatid == chatid).offset(skip).limit(limit).all()
