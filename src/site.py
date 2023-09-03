'''module for Site class'''

import re
from typing import Any, Dict, List, Union

import bs4

import src.parsing_utils as pu
from src.request_utils import (check_link, convert_content_into_soup,
                               get_page_content)
from src.settings import Settings


class Site():
    '''class is responsible to fetching and parsing single page content'''
    link: str
    settings: Settings
    site_content: str

    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)

        if self.link:
            self.link = check_link(self.link)

    def fetch_site_content(self) -> None:
        '''fetch page content'''

        self.site_content = get_page_content(self.link, self.settings.header) # type: ignore

    @property
    def site_soup(self) -> Union[bs4.BeautifulSoup, Any]:
        '''convert site content into bs4 soup'''
        if not self.site_content:
            return None

        return convert_content_into_soup(self.site_content)

    @property
    def links(self) -> Union[List[str], Any]:
        '''list of links found on the web site'''
        if not self.site_soup:
            return None

        found_links = pu.get_links(self.site_soup)
        found_links = [
            self.link + link
            if link[0] == '/' else link
            for link in found_links
        ]
        found_links = list(
            set(
                re.sub(r'www\.', '', link)
                for link in found_links
            )
        )

        found_links = [link for link in found_links if link != self.link]
        return found_links
    
    @property
    def self_links(self):
        '''returns a list of links to the same web site'''

        print(
            f'****************************\n'
            f'{self.link=}\n'
            f'{self.links=}\n'
            f'{pu.check_specific_links(self.links, "/", False)=}\n'
            f'{pu.check_specific_links(self.links, self.link, False)=}\n'
        )

    def to_dict(self):
        '''prepares a dictionary with all scraped information frm the web site'''
        return {
            **self._get_name(),
            **self._get_address(),
            **self._get_phones(),
            **self._get_emails(),
            **self._get_social(),
            **self._get_keywords(),
        }

    def _get_name(self) -> Dict:
        '''return dictionary with company names'''
        return {'name': None}

    def _get_address(self) -> Dict:
        '''return dictionary with addresses'''
        return {'address': None}

    def _get_phones(self) -> Dict:
        '''get phone links from the page'''
        if not self.links:
            return {'found phones': None}

        found_phones = pu.check_specific_links(
            link_list=self.links,
            link_type=self.settings.phone_link_identifier,
            clean_links=True,
        )

        found_phones = [
            re.sub(r'\D', '', phone)
            for phone in found_phones
        ]
        found_phones = list(set(found_phones))

        return {'found phones': found_phones}

    def _get_emails(self) -> Dict:
        '''get email links from the page'''

        if not self.links:
            return {'found emails': None}

        found_emails = pu.check_specific_links(
            link_list=self.links,
            link_type=self.settings.email_link_identifier,
            clean_links=True,
        )

        return {'found emails': found_emails}

    def _get_social(self) -> Dict:
        '''checks presents of social link accounts'''

        return pu.check_social_mdeia(self.links, self.settings.social_links)

    def _get_keywords(self):
        '''checks precence of keywords on the page'''

        return pu.check_keywords(self.site_content, self.settings.key_words)
