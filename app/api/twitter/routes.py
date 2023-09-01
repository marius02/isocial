from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.db_config import get_user_db
from api.twitter.models import TwitterReplyCreate
import tweepy
from dotenv import load_dotenv
import os
import ssl


load_dotenv()


router = APIRouter(prefix="/twitter", tags=["Twitter API"])


ssl._create_default_https_context = ssl._create_unverified_context

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")


auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


@router.get("/{tweet_id}/replies")
def get_twitter_tweet_replies(username: str, tweet_id: str):
    replies = []
    try:
        tweets = tweepy.Cursor(api.search, q='to:' + username,
                               result_type='recent', timeout=999999).items(1000)
        if tweets:
            for tweet in tweets:
                if hasattr(tweet, 'in_reply_to_status_id_str'):
                    if (tweet.in_reply_to_status_id_str == tweet_id):
                        replies.append(tweet)
        return replies
    except Exception as err:
        print(f"Error: {err}")

    return replies