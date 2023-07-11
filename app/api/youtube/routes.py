from fastapi import APIRouter
from dotenv import load_dotenv
import googleapiclient.discovery
import os


load_dotenv()


router = APIRouter(prefix="/youtube", tags=["YouTube Google API"])


# Instructions for creating API key
# https://developers.google.com/youtube/v3/quickstart/python

API_KEY = os.getenv("YOUTUBE_API_KEY")


@router.get("/{video_id}/comments")
def get_comments(video_id):

    api_service_name = "youtube"
    api_version = "v3"

    all_extracted_comments = []

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=API_KEY)

    request = youtube.commentThreads().list(
        part="snippet,replies",
        videoId=video_id
    )
    response = request.execute()
    comments = response['items']

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
