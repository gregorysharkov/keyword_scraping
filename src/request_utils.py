'''helper functions to make requests'''

import logging
import re
from typing import Any, Dict, Union

import bs4
import requests
import urllib3
import validators
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)
urllib3.disable_warnings()


def check_link(url: str) -> str:
    '''validates the link and if not tries to correct it'''
    url = re.sub(r'www\.', '', url)
    validation_check = validators.url(url)
    if not validation_check:
        url = f'https://{url}/'
        url = url[:-1] if url[-2:] == '//' else url

    return url


def get_page_content(url: str, header: Dict) -> Union[str, Any]:
    '''gets content from a page'''

    try:
        response = requests.get(url, headers=header, verify=False)
        return response.content.decode()  # type:ignore
    except ConnectionError:
        return None
    except Exception as err:
        # print(f"Unexpected {err=}, {type(err)=}")
        return None


def convert_content_into_soup(content: str) -> Union[bs4.BeautifulSoup, Any]:
    '''converts given content into soup'''

    if not content:
        return None

    return bs4.BeautifulSoup(content, 'html.parser')
