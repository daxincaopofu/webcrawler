from urllib.parse import urlparse

def normalize_url(url: str) -> str:
    parsed_url = urlparse(url)
    normalized_url = f"{parsed_url.netloc}{parsed_url.path.rstrip('/')}"
    return normalized_url