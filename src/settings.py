'''data class to store project settings'''
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Settings():
    '''class stores all project settings'''
    header: Dict
    key_words: List[str]
    social_links: List[str]
    email_link_identifier: str
    phone_link_identifier: str
