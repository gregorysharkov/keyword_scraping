from pathlib import Path

from src.load_settings import load_sites

CONF_PATH = Path() / 'conf'

def main():
    content = load_sites(CONF_PATH / 'site_list.txt')
    print(content[:5])

if __name__ == '__main__':
    main()