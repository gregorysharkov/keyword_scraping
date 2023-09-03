'''main scraping script'''
from pathlib import Path
from typing import Dict

import pandas as pd
import yaml
from tqdm import tqdm

from src.load_settings import load_sites
from src.settings import Settings
from src.site import Site

CONF_PATH = Path() / 'conf'


def load_settings(path: Path) -> Dict:
    '''loads project settings'''

    with open(path, 'r', encoding='utf-8') as file:
        settings = yaml.safe_load(file)
        return Settings(**settings) # type: ignore


def main():
    '''go trhough each site and scrape it'''
    site_links = load_sites(CONF_PATH / 'site_list.txt')[:5]
    settings = load_settings(CONF_PATH / 'settings.yml')

    return_dict = {}
    for link in tqdm(site_links):
        site = Site(link=link, settings=settings)
        site.fetch_site_content()
        return_dict.update({link: site.to_dict()})
        site.self_links

    return_df = pd.DataFrame(data=return_dict).T
    print(return_df.head())
    return_df.to_csv('scraped_data.csv', sep=';')

if __name__ == '__main__':
    # from urllib.parse import urlparse
    # print(urlparse('https://enabled4life.com.au'))
    # print(urlparse('https://www.enabled4life.com.au/sign-up/'))
    # print(urlparse('https://invoices.enabled4life.com.au/'))
    main()

# https://interhealthcare.com.au//contact-us/
# https://interhealthcare.com.au/contact-us/
