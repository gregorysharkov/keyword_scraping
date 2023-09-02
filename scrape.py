from pathlib import Path

import pandas as pd
from tqdm import tqdm

import src.parsing_utils as pu
from src.load_settings import load_sites
from src.request_utils import convert_content_into_soup, get_page_content

CONF_PATH = Path() / 'conf'
HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
}

KEY_WORDS = [
    r'Age Care',
    r'Domestic Assistance',
    r'Personal Care',
    r'Nursing',
    r'Homecare package',
    r'Support Workers',
    r'Career',
    r'Support Coordination',
    r'NDIS',
    r'Plan management',
]

SOCIAL_LINKS = [
    'linkedin',
    'facebook',
    'instagram',
]

EMAIL_LINK_IDENTIFIER = 'mailto:'
PHONE_LINK_IDENTIFIER = 'tel:'

def main():
    site_links = load_sites(CONF_PATH / 'site_list.txt')[:20]

    sites_content = [get_page_content(link, HEADER) for link in tqdm(site_links, 'Fetching sites')]
    site_soups = [
        convert_content_into_soup(site_content)
        for site_content in sites_content
    ]


    return_dict = {}
    for link, site_soup in tqdm(zip(site_links, site_soups), 'Analyzing sites'):

        page_text = pu.get_main_page_text(site_soup) # type: ignore
        site_links = pu.get_links(site_soup)
        return_dict.update(
            {
                link: {
                    'name': None,
                    'address': None,
                    'found_phones': pu.check_specific_links(site_links, PHONE_LINK_IDENTIFIER, True),
                    'found_emails': pu.check_specific_links(site_links, EMAIL_LINK_IDENTIFIER, True),
                    **pu.check_social_mdeia(site_links, SOCIAL_LINKS),
                    **pu.check_keywords(page_text, KEY_WORDS),
                }
            }
        )

    return_df = pd.DataFrame(data=return_dict)

    return_df.T.to_csv('scraped_data.csv', sep=';')

if __name__ == '__main__':
    main()