from fastapi import APIRouter, Depends
from dotenv import load_dotenv
from db.db_config import get_async_session
from db.models.youtube import YouTubeComment
from api.youtube.models import YouTubeCommentCreate, YouTubeCommentResponse
import googleapiclient.discovery
import os
from db.repositories.youtube_repository import YouTubeRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from urllib.parse import urlparse
import re

load_dotenv()


router = APIRouter(prefix="/youtube", tags=["YouTube Google API"])


# Instructions for creating API key
# https://developers.google.com/youtube/v3/quickstart/python

API_KEY = os.getenv("YOUTUBE_API_KEY")


@router.get("/comments/")
async def get_comments(video_url: str):

    # Parse the URL
    parsed_url = urlparse(video_url)

    video_id = re.sub(r'^/', '', parsed_url.path)

    api_service_name = "youtube"
    api_version = "v3"

    all_extracted_comments = []

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=API_KEY)

    request = youtube.commentThreads().list(
        part="snippet,replies",
        videoId=video_id,
        maxResults=100
    ).execute()

    comments = request['items']

    if comments:
        for comment in comments:
            all_extracted_comments.append(
                comment['snippet']['topLevelComment']['snippet']['textOriginal'])
            if 'replies' in comment:
                # Iterate over each reply
                for reply in comment['replies']['comments']:
                    all_extracted_comments.append(
                        reply['snippet']['textOriginal'])

    return all_extracted_comments


@router.post("/comments/")
async def save_comment(comment: YouTubeCommentCreate, db: AsyncSession = Depends(get_async_session)):
    youtube_repo = YouTubeRepository(db)
    return await youtube_repo.create_comment(comment)


@router.get("/comments/{chatid}", response_model=YouTubeCommentResponse)
async def get_comments_by_chatid(chatid: str, db: AsyncSession = Depends(get_async_session)):
    async with db.begin():
        query = select(YouTubeComment).where(YouTubeComment.chat_id == chatid)
        db_comment = await db.execute(query)

        return db_comment.scalar_one()
