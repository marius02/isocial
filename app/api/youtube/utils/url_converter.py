from urllib.parse import urlparse, parse_qs


def extract_video_id(video_url: str) -> str:
    parsed_url = urlparse(video_url)
    video_id = parsed_url.path.strip('/')
    return video_id
