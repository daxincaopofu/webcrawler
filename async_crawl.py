import aiohttp
import asyncio
from collections import deque
from crawl import normalize_url, extract_page_data, parse_domain


class AsyncCrawler:

    def __init__(self, base_url, page_data, max_concurrency, session, debug=False):
        self.base_url = base_url
        self.page_data = page_data
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.session = session
        self.num_pages_visited = 0
        self.debug = debug

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def add_page_visit_async(self, normalized_url):
        async with self.lock:
            return not normalized_url in self.page_data

    async def get_html_async(self, relative_url: str) -> str:

        if self.debug:
            print(f"Requesting from {relative_url} via {self.base_url}")
        try:
            response = await self.session.request(
                "GET", relative_url, headers={"User-Agent": "BootCrawler/1.0"}
            )
        except Exception as e:
            return e
        if response.status >= 400:
            raise Exception(f"{response.status} found for url")
        if "text/html" not in response.headers["content-type"]:
            raise Exception(
                f"Can only parse text/html results. Not {response.headers.get('content-type')}"
            )
        return await response.text()

    async def async_crawl(self, debug=True):

        urls_to_visit = deque([self.base_url])
        normalized_base_url = normalize_url(self.base_url)

        while urls_to_visit:
            cur_url = urls_to_visit.pop()
            normalized_cur_url = normalize_url(cur_url)

            if not await self.add_page_visit_async(normalized_cur_url):
                continue

            self.num_pages_visited += 1

            async with self.semaphore:
                try:
                    cur_page_html = await self.get_html_async(cur_url)
                except Exception:
                    continue
                cur_page_data = extract_page_data(cur_page_html, self.base_url)

                async with self.lock:
                    self.page_data[normalized_cur_url] = cur_page_data

                for child_url in cur_page_data["outgoing_links"]:
                    normalized_child_url = normalize_url(child_url)
                    if parse_domain(normalized_child_url) != parse_domain(
                        normalized_base_url
                    ):
                        continue
                    urls_to_visit.append(child_url)
