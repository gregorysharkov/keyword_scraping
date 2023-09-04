'''
functions used to extract information from parsed html structures
'''

import re
from typing import Any, Dict, List, Union

import bs4


def get_main_page_text(element_soup = bs4.BeautifulSoup) -> Union[str, Any]:
    '''function recovers text of the element and does some cleaning'''
    if not element_soup:
        return None

    site_text = element_soup.text.strip() # type: ignore
    site_text = re.sub(r' {1,}\n', '\n', site_text)
    site_text = re.sub(r'\n{2,}', '\n\n', site_text)
    site_text = re.sub(r'\t{1,}', ' ', site_text).strip()
    site_text = re.sub(r'\xa0{1,}', ' ', site_text).strip()

    return site_text


def check_keywords(text: str, keywords: List[str]) -> Dict[str, Union[bool, Any]]:
    '''
    function checks presence if keywords in the text
    returns a list of booleans of the same length as the list of keywords
    '''
    if not text:
        return {keyword: None for keyword in keywords}

    return_dict = {}
    for word in keywords:
        search_result = not re.search(word.lower(), text.lower()) is None
        return_dict.update({word: search_result})

    return return_dict


def get_links(page_soup: bs4.BeautifulSoup) -> Union[List[str], Any]:
    '''function gets all the links from the given page'''

    if not page_soup:
        return None

    link_list = page_soup.find_all('a')

    if not link_list:
        return None

    link_list = list(
        set(
            element.get('href', f'invalid_link: {repr(element)}')
            for element in link_list
        )
    )
    return [link for link in link_list if len(link)]


def check_social_mdeia(link_list: List[str], social_list: List[str]) -> Dict[str, Any]:
    '''function checks for any links to social media in a given soup'''

    if not link_list:
        return {social: None for social in social_list}

    found_links = {}
    for social in social_list:
        found_elements = list(
            set(
                element for element in link_list if social in element
            )
        )
        found_links.update({social: found_elements})

    return found_links


def check_specific_links(
        link_list: List[str],
        link_type: str,
        clean_links: bool
) -> Union[List[str], Any]:
    '''
    function returns all links in the link_list that match link_type
    
    Args:
        link_list: list of links to be parsed
        link_type: type of links to be searched for
        clean_links: boolean flag indicating whether the links need to be cleaned

    Returns:
        either an empty list or none if the original link list is enmpty
    '''

    if not link_list:
        return None


    found_links = list(
        set(
            element for element in link_list if re.match(link_type, element)
        )
    )

    if clean_links:
        found_links = [
            re.sub(link_type, '', link) for link in found_links
        ]

    return found_links
