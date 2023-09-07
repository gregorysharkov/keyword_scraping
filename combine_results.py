from functools import reduce
from pathlib import Path

import pandas as pd

OUTPUT_PATH = Path() / 'data'


def main():
    chunks = []

    for file_path in OUTPUT_PATH.iterdir():
        if file_path.is_dir() or 'chunk' not in file_path.name:
            pass

        chunks.append(
            pd.read_excel(file_path)
        )

    combined_df = reduce(lambda x, y: pd.concat([x, y]), chunks)
    combined_df.to_excel(OUTPUT_PATH / 'combined_sites.xls', index=False)


if __name__ == '__main__':
    main()
