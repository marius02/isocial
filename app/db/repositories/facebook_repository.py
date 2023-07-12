from sqlalchemy.orm import Session
from db.models.facebook import FacebookComment, FacebookPost


class FacebookRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_comment(self, comment: FacebookComment):
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)

    def create_post(self, post: FacebookPost):
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)

    def get_comments_by_post(self, post: FacebookPost):
        return self.db.query(FacebookComment).filter_by(post=post).all()

    def get_post_by_url(self, post_url: str):
        return self.db.query(FacebookPost).filter_by(post_url=post_url).first()
