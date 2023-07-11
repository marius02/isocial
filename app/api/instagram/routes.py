from fastapi import APIRouter
from dotenv import load_dotenv
import os
import requests

load_dotenv()


router = APIRouter(prefix="/instagram", tags=["Instagram Graph API"])


ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_USER_TOKEN")


@router.get("/user-pages")
def get_user_pages():
    api_endpoint = 'https://graph.facebook.com/v17.0/me/accounts'
    params = {
        'access_token': ACCESS_TOKEN,
        'fields': 'name,id'
    }

    try:
        response = requests.get(api_endpoint, params=params)
        response.raise_for_status()

        json_data = response.json()
        if 'data' in json_data:
            return json_data['data']
        else:
            print('Error: Response data is missing "data" field.')
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Request Exception: {err}")

    return []

# You can also inject the database session and use the FacebookRepository
# to interact with the database if needed

# Example of injecting the database session and repository:
# def get_facebook_post_comments(post_id: str, db: Session = Depends(get_db)):
#     facebook_repo = FacebookRepository(db)
#     # Perform database operations using the repository


# facebook page should be connected to instagram business account
@router.get("/{facebook_page_id}/user-ig-business-account")
def get_user_ig_business_account(facebook_page_id):
    api_endpoint = f'https://graph.facebook.com/v17.0/{facebook_page_id}'
    params = {
        'access_token': ACCESS_TOKEN,
        'fields': 'instagram_business_account'
    }
    try:
        response = requests.get(api_endpoint, params=params)
        response.raise_for_status()

        json_data = response.json()
        if 'instagram_business_account' in json_data:
            return json_data['instagram_business_account']['id']
        else:
            print('Error: Response data is missing "instagram_business_account" field.')
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Request Exception: {err}")

    return None


@router.get("/{account_id}/media-and-comments")
def get_ig_business_account_media(account_id):
    api_endpoint = f'https://graph.facebook.com/v17.0/{account_id}/media'
    params = {
        'access_token': ACCESS_TOKEN,
        'fields': 'comments{replies{text,id},text},comments_count,is_comment_enabled,media_url,media_type'
    }
    try:
        response = requests.get(api_endpoint, params=params)
        response.raise_for_status()

        json_data = response.json()
        if 'data' in json_data:
            return json_data['data']
        else:
            print('Error: Response data is missing "data" field.')
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Request Exception: {err}")

    return []
