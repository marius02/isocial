from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.base import get_db
from api.facebook.models import FacebookCommentCreate
from api.facebook.utils.url_converter import convert_facebook_url
from db.repositories.facebook_repository import FacebookRepository
from api.facebook.services import FacebookService
from dotenv import load_dotenv
import os
import requests


load_dotenv()


router = APIRouter(prefix="/facebook", tags=["Facebook Graph API"])


ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_PAGE_TOKEN")


@router.get("/comments")
def get_facebook_post_comments(post_url: str):
    post_id = convert_facebook_url(post_url)
    api_endpoint = f'https://graph.facebook.com/v17.0/{post_id}'
    params = {
        'access_token': ACCESS_TOKEN,
        'fields': 'comments{message,comments{message}}'
    }
    try:
        response = requests.get(api_endpoint, params=params)
        response.raise_for_status()

        json_data = response.json()
        if 'comments' in json_data:
            return json_data['comments']['data']
        else:
            return []
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Request Exception: {err}")

    return []
