# https://github.com/DucHung0109/Post_News_FanPage

import requests
from PIL import Image
from io import BytesIO
from urllib.parse import urlparse, parse_qs, unquote

MAX_SIZE = 4 * 1024 * 1024
MAX_DIM = 2048


def unwrap_image_url(url: str):
    """
    Unwraps a url

    Input: wraped url

    Output: - str: unwraped url
    """

    parsed_url = urlparse(url)
    qs = parse_qs(parsed_url.query)
    candidates = ["src", "url", "img", "image", "picture"]
    for key in candidates:
        if key in qs:
            value = qs[key][0]
            return unquote(value)
    return url

def load_image(url: str, source_url: str):
    """
    Get image and convert it into a format supported by Facebook for posting.

    Input:
            - url: url to image
            - source_url: url to source page, where image was found
    
    Output: A tuple include:
            - str: file name
            - bytes: binary content of image
            - str: MIME type of image
    """
    
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Referer": source_url,
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    }

    url = unwrap_image_url(url)
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        print(url)
        print(source_url)
        return None
    
    
    img = Image.open(BytesIO(response.content))

    # Chuyển đổi sang định dạng JPG (Facebook hỗ trợ)
    img = img.convert("RGB")

    # Resize nếu quá lớn (giảm tối đa xuống 2048px mỗi chiều)
    img.thumbnail((MAX_DIM, MAX_DIM))

    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    data = buffer.getvalue()

    return ("image.jpg", data, "image/jpeg")