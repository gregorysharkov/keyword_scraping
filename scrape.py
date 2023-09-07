'''main scraping script'''
import asyncio
from datetime import datetime
from pathlib import Path
from threading import BoundedSemaphore
from typing import Dict, List

import pandas as pd
import yaml
from tqdm import tqdm

from src.load_settings import load_sites
from src.settings import Settings
from src.site_group import SiteGroup

CONF_PATH = Path() / 'conf'
TIME_FORMAT = "%H:%M:%S"


def load_settings(path: Path) -> Settings:
    '''loads project settings'''

    with open(path, 'r', encoding='utf-8') as file:
        settings = yaml.safe_load(file)
        return Settings(**settings)  # type: ignore


# def parse_sites(site_links: List[str], settings: Dict, thread_limiter=None) -> Dict:
#     '''parse list of sites and return a dictionar'''

#     threads = []
#     for link in tqdm(site_links, 'getting site information'):
#         site = Site(link=link, settings=settings, threadLimiter=thread_limiter)
#         site.start()
#         threads.append(site)

#     return_dict = {}
#     for site in tqdm(threads, 'Completing requests'):
#         site.join()
#         return_dict.update({site.link: site.return_dict})

#     return return_dict


async def parse_site_groups(
    site_links: List[str],
    settings: Settings,
    chunkid: int
) -> Dict:
    '''function processes a group of site links. Each link is processed as a site link'''
    print(f'{datetime.now().strftime(TIME_FORMAT)} - Starting chunk {chunkid}')
    max_threads = 20
    thread_limiter = BoundedSemaphore(max_threads)
    threads = []
    for link in site_links:
        site_group = SiteGroup(link=link, settings=settings,
                               threadLimiter=thread_limiter)
        site_group.start()
        threads.append(site_group)

    return_dict = {}
    for site_group in threads:
        site_group.join()
        return_dict.update(
            {
                site_group.link: site_group.combined_dict
            }
        )

    print(f'{datetime.now().strftime(TIME_FORMAT)} - Done with chunk {chunkid}')
    return return_dict


async def main():
    '''go trhough each site and scrape it'''

    print(f'{datetime.now().strftime(TIME_FORMAT)} - Start')
    # site_links = ['https://achieveaustralia.org.au/',
    #               'https://enabled4life.com.au/']
    # site_links = ['https://enabled4life.com.au/',
    #               'https://acerehabsolutions.com/']
    site_links = load_sites(CONF_PATH / 'site_list.txt')[:500]
    settings = load_settings(CONF_PATH / 'settings.yml')

    chunk_size = 20
    chunks = [
        site_links[i:min(i+chunk_size, len(site_links))]
        for i in range(0, len(site_links), chunk_size)
    ]

    # start a separate task for each task
    tasks = []
    for idx, chunk in enumerate(tqdm(chunks, 'creating tasks')):
        tasks.append(
            asyncio.create_task(
                parse_site_groups(chunk, settings, idx)
            )
        )

    # wait for all tasks to complete
    await asyncio.gather(*tasks)

    # combine all results
    site_dict = {}
    for task in tasks:
        site_dict.update(task.result())

    return_df = pd.DataFrame(data=site_dict).T
    print(return_df.head())
    return_df.to_excel(
        'data/scraped_data.xlsx',
        engine='xlsxwriter',
    )
    print(f'{datetime.now().strftime(TIME_FORMAT)} - End')


if __name__ == '__main__':
    asyncio.run(main())
