from fastapi import APIRouter
from dotenv import load_dotenv
import os
import requests
from api.instagram.utils.url_converter import extract_permalink_from_url

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


@router.get("/{post_url}/comments")
def filter_media_by_permalink(user_ig_business_account_id: str, post_url: str):
    permalink = extract_permalink_from_url(post_url)
    print(permalink)
    api_endpoint = f"https://graph.facebook.com/v17.0/{user_ig_business_account_id}/media"
    params = {
        "access_token": ACCESS_TOKEN,
        "fields": "caption,permalink,comments"
    }

    try:
        response = requests.get(api_endpoint, params=params)
        response.raise_for_status()

        json_data = response.json()
        if "data" in json_data:
            filtered_media = [media for media in json_data["data"]
                              if media.get("permalink") == permalink]
            return filtered_media
        else:
            print('Error: Response data is missing "data" field.')
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Request Exception: {err}")

    return []
