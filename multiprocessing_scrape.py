import multiprocessing
from datetime import datetime
from pathlib import Path
from threading import BoundedSemaphore
from typing import Dict, List

import pandas as pd
import yaml

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


def parse_site_group(
    site_links: List[str],
    settings: Settings,
    chunkid: int
) -> None:
    '''function processes a group of site links. Each link is processed as a site link'''
    print(f'{datetime.now().strftime(TIME_FORMAT)} - Starting chunk {chunkid}')

    output_path = Path() / 'data' / f'scraped_data_chunk_{chunkid}.xlsx'
    if output_path.exists():
        print(f'{datetime.now().strftime(TIME_FORMAT)} - Done with chunk {chunkid}')
        return None

    max_threads = 30
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

    store_dict(return_dict, chunkid)
    print(f'{datetime.now().strftime(TIME_FORMAT)} - Done with chunk {chunkid}')
    # return return_dict


def store_dict(data: Dict, idx: int) -> None:
    '''store chunk data in an excel file'''
    return_df = pd.DataFrame(data=data).T
    return_df.to_excel(
        f'data/scraped_data_chunk_{idx}.xlsx',
        engine='xlsxwriter',
    )


def create_chunks(data: List, chunk_size) -> List:
    '''split data into chunks'''

    return [
        data[i:min(i+chunk_size, len(data))]
        for i in range(0, len(data), chunk_size)
    ]


def main():
    print(f'{datetime.now().strftime(TIME_FORMAT)} - Start')
    site_links = load_sites(CONF_PATH / 'site_list.txt')
    n_cores = 4
    settings = load_settings(CONF_PATH / 'settings.yml')
    chunk_size = 50

    chunks = create_chunks(site_links, chunk_size)

    pool = multiprocessing.Pool(n_cores)
    pool.starmap(
        parse_site_group,
        [(chunk, settings, idx) for idx, chunk in enumerate(chunks)]
    )


if __name__ == '__main__':
    main()
