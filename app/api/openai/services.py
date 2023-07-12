from dotenv import load_dotenv
from fastapi import HTTPException
import openai
import os
import requests

load_dotenv()

openai.api_key = os.getenv('OPENAI_TOKEN')


class OpenAIService:
    def __init__(self):
        pass

    def summarize_comments(self, platform: str, comments: list):
        platforms_objects = {
            'youtube': 'video',
            'twitter': 'tweet',
            'facebook': 'post',
            'instagram': 'post',
            'tiktok': 'video'
        }

        if platform.lower() not in platforms_objects:
            raise HTTPException(status_code=400, detail="Invalid Platform")

        try:
            prompt = f"""The following are users comments of a {platform} {platforms_objects[platform.lower()]}, with each comment separated by a ;. 
                        Provide a summary of what users think about the {platforms_objects[platform.lower()]}.

                        Comments: {';'.join(comments)}
                        """
            messages = [{"role": "user", "content": prompt[:12000]}]
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0,
                max_tokens=800
            )
            return response.choices[0].message["content"]

        except openai.OpenAIError as e:
            raise HTTPException(
                status_code=500, detail=f"OpenAI Error: {str(e)}")
