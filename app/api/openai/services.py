from dotenv import load_dotenv
from fastapi import HTTPException
import openai
import os

load_dotenv()


class OpenAIService:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_TOKEN')

    def get_completion(self, comments: list[str], prompt: str):
        text = ';'.join(comments)
        messages = [
            {
                "role": "user",
                "content": f"""The following are users comments about the content with each comment separated by a ;.
                                {prompt[:2000]}
                                Comments: {text[:2097]}
                """
            }
        ]

        try:
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
