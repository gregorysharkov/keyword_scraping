'''module for Site class'''

import re
from functools import cache
from threading import Thread
from typing import Any, Dict, List, Union

import bs4

import src.parsing_utils as pu
from src.request_utils import (check_link, convert_content_into_soup,
                               get_page_content)
from src.settings import Settings


class Site(Thread):
    '''class is responsible to fetching and parsing single page content'''
    link: str
    settings: Settings
    site_content: str
    return_dict: dict
    check_children = False

    def __init__(
        self,
        group=None,
        target=None,
        threadLimiter=None,
        **kwargs
    ) -> None:
        super().__init__(group=group, target=target, name=kwargs.get('link'))

        self.thread_limiter = threadLimiter
        self.__dict__.update(kwargs)

        if self.link:
            self.link = check_link(self.link)

    def fetch_site_content(self) -> None:
        '''fetch page content'''

        self.site_content = get_page_content(
            self.link, self.settings.header)  # type: ignore

    def run(self):
        """function that is called whenever the thread is started"""
        if self.thread_limiter:
            self.thread_limiter.acquire()
        try:
            self.fetch_site_content()
        except Exception as err:
            print(
                f'Could not parse {self.name} due to the following error: {err}')
        finally:
            self.return_dict = self.to_dict()
            if self.thread_limiter:
                self.thread_limiter.release()

    def to_dict(self):
        '''prepares a dictionary with all scraped information frm the web site'''
        self.return_dict = {
            'link': self.link,
            **self._get_name(),
            **self._get_address(),
            **self._get_phones(),
            **self._get_emails(),
            **self._get_social(),
            **self._get_keywords(),
            **self._get_page_text(),
            **self._get_self_links(),
        }
        return self.return_dict

    def __add__(self, other):
        '''method for mergin information from two sites'''
        # if not other:
        #     return self

        dict_a = self.return_dict
        dict_b = other.return_dict
        updated_dict = {}
        for key in dict_a.keys():
            if key == 'name':
                update_element = None
            elif key in self.settings.key_words:
                update_element = combine(
                    dict_a.get(key, False),
                    dict_b.get(key, False),
                    _max,
                )
            elif key == 'site_text':
                update_element = combine(
                    dict_a.get(key, ''),
                    dict_b.get(key, ''),
                    _concat,
                )
            elif key == 'next level links':
                update_element = dict_a.get(key)
            elif key == 'link':
                update_element = dict_a.get(key)
            elif key == 'address':
                update_element = combine(
                    dict_a.get(key, ''),
                    dict_b.get(key, ''),
                    _concat,
                )
            else:
                update_element = combine(
                    dict_a.get(key, []),
                    dict_b.get(key, []),
                    _common,
                )

            updated_dict.update({key: update_element})

        self.return_dict = updated_dict
        return self

    @property
    @cache
    def site_soup(self) -> Union[bs4.BeautifulSoup, Any]:
        '''convert site content into bs4 soup'''
        if not self.site_content:
            return None

        return convert_content_into_soup(self.site_content)

    @property
    @cache
    def links(self) -> Union[List[str], Any]:
        '''list of links found on the web site'''
        if not self.site_soup:
            return None

        found_links = pu.get_links(self.site_soup)
        if not found_links:
            return None

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
    @cache
    def self_links(self):
        '''returns a list of links to the same web site'''

        if not self.links:
            return None

        if not self.check_children:
            return None

        # check short links, the ones that start with / symbol
        short_links = pu.check_specific_links(self.links, "/", False)
        link = self.link[:-1] if self.link[-1] == '/' else self.link
        short_links = [link + short_link for short_link in short_links]

        # check long linksm the ones that contain the original link
        long_links = pu.check_specific_links(self.links, self.link, False)

        link_list = short_links + long_links

        def clean_link(link: str) -> str:
            link = re.sub(r'https://', 'qwerty', link)
            link = re.sub(r'//', '/', link)
            link = re.sub('qwerty', 'https://', link)
            return link

        link_list = list(
            set(
                map(clean_link, link_list)
            )
        )

        def select_first_level_links(link_list, self_link=self.link) -> List[str]:
            '''function removes second level links fromt he link list'''

            clean_links = []
            for link in link_list:
                clean_link = re.sub(r'\?.+', '', link)
                clean_link = clean_link if clean_link[-1] != '/' else clean_link[-1]
                remainder = re.sub(self_link, '', clean_link)
                if not re.match(r'\/', remainder):
                    clean_links.append(clean_link)

            if not clean_links:
                return None

            return list(set(clean_links))

        link_list = select_first_level_links(link_list, self.link)
        if not link_list:
            return None

        return link_list

    def _get_self_links(self):
        '''temporary function'''

        return {'next level links': self.self_links}

    def _get_name(self) -> Dict:
        '''return dictionary with company names'''
        return {'name': None}

    def _get_address(self) -> Dict:
        '''return dictionary with addresses'''
        soup = self.site_soup
        if not soup:
            return {'address': None}

        def custom_tag_selector(tag):
            tag_match = re.search(r'a|h\d|div|span', tag.name) is not None
            text_match = re.search('^address', tag.text.lower()) is not None
            return tag_match & text_match

        address_element = soup.find(custom_tag_selector)
        if not address_element:
            return {'address': None}

        return {'address': address_element.text}

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

    def _get_keywords(self) -> Dict:
        '''checks precence of keywords on the page'''

        return pu.check_keywords(self.site_content, self.settings.key_words)

    def _get_page_text(self) -> Dict:
        '''returns cleaned text from the page'''

        if not self.site_soup:
            return {'site_text': None}

        page_text = pu.get_main_page_text(self.site_soup)  # type: ignore
        return {
            'site_text': f'page: {self.link}\n{page_text[:min(1000, len(page_text))]}'
        }


def combine(el_a, el_b, combination_function):
    """
    Concatenation of two lists, handling `None` values.

    Args:
    el_a: The first list.
    el_b: The second list.
    combination_function callable to collect results

    Returns:
    The concatenation of the two lists, with unique elements.
    """

    if el_a is None:
        return el_b

    if el_b is None:
        return el_a

    return combination_function(el_a, el_b)


def _concat(el_a, el_b):
    return f'{el_a}\n{el_b}'


def _max(el_a, el_b):
    return max(el_a, el_b)


def _common(el_a, el_b):
    list(set(el_a + el_b))
