from fastapi import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.base import get_db
from api.facebook.models import (FacebookCommentCreate, FacebookPostCreate,
                                 FacebookPost, FacebookComment)
from api.facebook.utils.url_converter import convert_facebook_url
from db.repositories.facebook_repository import FacebookRepository
from api.facebook.services import FacebookService
from dotenv import load_dotenv
import os
import requests


load_dotenv()


router = APIRouter(prefix="/facebook", tags=["Facebook Graph API"])


ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_PAGE_TOKEN")


@router.get("/{post_url}/comments")
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


@router.post("/{post_url}/comments")
def save_facebook_post_comments(post_url: str, db: Session = Depends(get_db)):
    post_id = convert_facebook_url(post_url)

    try:
        # Check if the post exists in the database
        repository = FacebookRepository(db)
        post = repository.get_post_by_url(post_url)

        if post:
            # Check if all comments are already saved in the database
            service = FacebookService()
            comments = service.get_comments_by_post_id(post_id)

            existing_comments = repository.get_comments_by_post(post)
            existing_comments_text = [
                comment.text for comment in existing_comments]
            new_comments = [
                comment for comment in comments if comment['message'] not in existing_comments_text]

            if len(new_comments) == 0:
                # All comments are already saved, return the saved comments
                return {"message": "All comments already exist in the database.", "comments": existing_comments}
            else:
                # Save the new comments to the database
                for comment in new_comments:
                    comment_create = FacebookCommentCreate(
                        text=comment['message'],
                        post=post
                    )
                    repository.create_comment(comment_create)
                return {"message": "New comments saved to the database.", "comments": comments}
        else:
            # Save the post and all comments to the database
            service = FacebookService()
            post_data = service.get_post_data(post_id)

            post_create = FacebookPostCreate(
                post_url=post_url,
                post_text=post_data['post_text']
            )
            post = repository.create_post(post_create)

            comments = service.get_comments_by_post_id(post_id)
            for comment in comments:
                comment_create = FacebookCommentCreate(
                    text=comment['message'],
                    post=post
                )
                repository.create_comment(comment_create)
            return {"message": "Post and comments saved to the database.", "comments": comments}

    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve comments from the API.")
    except requests.exceptions.RequestException as err:
        print(f"Request Exception: {err}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve comments from the API.")
