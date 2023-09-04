'''functions to load data from configuration'''

from pathlib import Path
from typing import List


def load_sites(path: Path) -> List[str]:
    '''loads list of sites from a given path'''

    with open(path, 'r', encoding='utf-8') as file:
        content = file.readlines()

    return [link.strip() for link in content]
