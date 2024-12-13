from urllib.parse import urlparse


def extract_permalink_from_url(url: str) -> str:
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.strip('/').split('/')

    if len(path_segments) < 2 or path_segments[0] != 'p':
        return ''

    permalink = f"https://www.instagram.com/p/{path_segments[1]}/"
    return permalink
