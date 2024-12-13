from urllib.parse import parse_qs, urlparse


def convert_facebook_url(url: str) -> str:
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    story_fbid = query_params.get('story_fbid', [''])[0]
    post_id = query_params.get('id', [''])[0]

    return f"{post_id}_{story_fbid}"
