'''helper functions to make requests'''

import logging
import re
from typing import Any, Dict, Union

import bs4
import requests
import validators
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)

def get_page_content(url: str, header: Dict) -> Union[str, Any]:
    '''gets content from a page'''

    validation_check = validators.url(url)
    if not validation_check:
        old_url = url
        url = re.sub(r'www\.', '', url)
        url = f'https://{url}'
        logger.warn(f'invalid url: {old_url}, will be scraping {url} instead')

    try:
        response = requests.get(url, headers=header)
        return response.content.decode()  # type:ignore
    except ConnectionError:
        return None
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        return None



def convert_content_into_soup(content: str) -> Union[bs4.BeautifulSoup, Any]:
    '''converts given content into soup'''

    if not content:
        return None

    return bs4.BeautifulSoup(content, 'html.parser')
