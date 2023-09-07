'''
site group is a group of sites made to scrape top level site
as well as all self links inside this web site
'''

import queue
from threading import Thread
from typing import Dict, List

import src.request_utils as ru
from src.settings import Settings
from src.site import Site


class SiteGroup(Thread):
    '''class handles the whole site'''
    link: str
    settings: Settings
    main_page: Site
    children: List[Site]
    combined_dict: Dict

    def __init__(
        self,
        group=None,
        target=None,
        threadLimiter=None,
        **kwargs
    ) -> None:
        self.__dict__.update(kwargs)
        if self.link:
            self.link = ru.check_link(self.link)

        super().__init__(group, target, name=kwargs.get('link'))
        self.queue = queue.Queue()
        self.thread_limiter = threadLimiter

    def run(self):
        '''method is called when the thread is initialized'''
        self._set_main_site()
        self.main_page.start()
        self.main_page.join()

        self._set_children()
        if self.children:
            child_threads = []
            for child_page in self.children:
                child_thread = Thread(
                    target=self._fetch_child_page,
                    args=(child_page,)
                )
                child_thread.start()
                child_threads.append(child_thread)

            self.main_page.join()

            # Wait for all child threads to finish.
            for child_thread in child_threads:
                child_thread.join()

        self._combine_results()

    def _combine_results(self) -> None:
        '''function combines all return dictionaries'''
        combined_site = self.main_page
        if not self.children:
            self.combined_dict = self.main_page.return_dict
            return

        for child in self.children:
            combied_site = combined_site + child

        self.combined_dict = combied_site.return_dict  # type: ignore

    def _set_main_site(self) -> None:
        '''function parses the main page'''

        self.main_page = Site(
            link=self.link,
            settings=self.settings,
            group=None,  # type: ignore
            target=None,  # type: ignore
            thread_limiter=self.thread_limiter,  # type: ignore
        )

    def _set_children(self) -> None:
        '''function fetches and parses child pages of the main site'''

        child_links = self.main_page.self_links
        if not child_links:
            self.children = None  # type: ignore
            return

        child_sites = [
            Site(
                link=link,
                settings=self.settings,
                group=None,  # type: ignore
                target=None,  # type: ignore
                thread_limiter=self.thread_limiter,  # type: ignore
                check_children=False,
            )
            for link in child_links
        ]

        self.children = child_sites

    def _fetch_child_page(self, child_page):
        child_page.start()
        child_page.join()
        self.queue.put(child_page.return_dict)
