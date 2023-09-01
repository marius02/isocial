from dotenv import load_dotenv
import googleapiclient.discovery
from urllib.parse import urlparse
import os
import re

load_dotenv()


# Instructions for creating API key
# https://developers.google.com/youtube/v3/quickstart/python


class YouTubeAPIService:
    def __init__(self):
        self.API_KEY = os.getenv("YOUTUBE_API_KEY")

    def get_comments(self, video_url: str):
        parsed_url = urlparse(video_url)
        video_id = re.sub(r'^/', '', parsed_url.path)
        api_service_name = "youtube"
        api_version = "v3"
        all_extracted_comments = []

        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=self.API_KEY)

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
                    for reply in comment['replies']['comments']:
                        all_extracted_comments.append(
                            reply['snippet']['textOriginal'])

        return ';'.join(all_extracted_comments)
