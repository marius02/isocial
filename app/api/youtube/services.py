from dotenv import load_dotenv
import googleapiclient.discovery
from googleapiclient.errors import HttpError

import os
import re

load_dotenv()


# Instructions for creating API key
# https://developers.google.com/youtube/v3/quickstart/python


class YouTubeAPIService:
    def __init__(self):
        self.API_KEY = os.getenv("YOUTUBE_API_KEY")

    def get_comments(self, video_url: str):
        regex_pattern = r"^.*(youtu\.be/|v/|u/\w/|embed/|watch\?v=|\&v=|live/)([^#\&\?]*).*"
        match = re.match(regex_pattern, video_url)
        if match and len(match.group(2)) == 11:
            video_id = match.group(2)

            api_service_name = "youtube"
            api_version = "v3"
            all_extracted_comments = []

            youtube = googleapiclient.discovery.build(
                api_service_name, api_version, developerKey=self.API_KEY)

            try:
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

                return '; '.join(all_extracted_comments)

            except HttpError as e:
                if e.error_details[0].get('reason') == "commentsDisabled":
                    return {
                        "detail": {
                            "code": "COMMENTS_DISABLED",
                            "reason": "Comments to this video are switched off"
                        }
                    }
        else:
            return {
                "detail": {
                    "code": "INVALID_URL",
                    "reason": "Only Youtube link using Share button is accepted"
                }
            }
