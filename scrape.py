'''main scraping script'''
from pathlib import Path
from threading import BoundedSemaphore
from typing import Dict, List

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


def parse_sites(site_links: List[str], settings: Dict, thread_limiter=None) -> Dict:
    '''parse list of sites and return a dictionar'''

    threads = []
    for link in tqdm(site_links, 'getting site information'):
        site = Site(link=link, settings=settings, threadLimiter=thread_limiter)
        site.start()
        threads.append(site)

    return_dict = {}
    for site in tqdm(threads, 'Completing requests'):
        site.join()
        return_dict.update({site.link: site.return_dict})

    return return_dict


def main():
    '''go trhough each site and scrape it'''
    site_links = load_sites(CONF_PATH / 'site_list.txt')[:200]
    settings = load_settings(CONF_PATH / 'settings.yml')

    max_num_threads = 32
    thread_limiter = BoundedSemaphore(max_num_threads)
    site_dict = parse_sites(site_links, settings, thread_limiter)

    return_df = pd.DataFrame(data=site_dict).T
    print(return_df.head())
    return_df.to_csv('data/scraped_data.csv', sep=';')

if __name__ == '__main__':
    main()
