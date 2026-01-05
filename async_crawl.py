import aiohttp
import asyncio
from collections import deque
from crawl import normalize_url, extract_page_data, parse_domain


class AsyncCrawler:

    def __init__(self, base_url, max_concurrency, debug=False, max_size=1000):
        self.base_url = base_url
        self.base_domain = parse_domain(normalize_url(self.base_url))
        self.page_data = {}
        self.lock = asyncio.Lock()
        self.visited = set()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.queue = asyncio.Queue(max_size)
        self.num_pages_visited = 0
        self.debug = debug

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers={"User-Agent": "BootCrawler/1.0"})
        await self.queue.put(self.base_url)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def get_html_async(self, url: str) -> str:
        async with self.semaphore:
            try:
                timeout = aiohttp.ClientTimeout(total=30)
                async with self.session.request(
                    "GET", url, timeout=timeout
                ) as response:
                    if response.status != 200:
                        if self.debug:
                            print(f"{url} resulted in {response.status} status code")
                        return None
                    if "text/html" not in response.headers.get("content-type", ""):
                        if self.debug:
                            print(f"{url} is not text/html type")
                        return None
                    return await response.text()
            except Exception as e:
                if self.debug:
                    print(f"{url}", e)
                return None

    async def reserve_url(self, url):
        async with self.lock:
            if url in self.visited:
                return False
            self.visited.add(url)
            return True

    async def worker(self):
        while True:
            url = await self.queue.get()

            if url is None:
                self.queue.task_done()
                return

            norm_url = normalize_url(url)
            domain = parse_domain(norm_url)

            if domain != self.base_domain:
                if self.debug:
                    print(f"{url} does not match base domain")
                self.queue.task_done()
                continue

            if not await self.reserve_url(norm_url):
                self.queue.task_done()
                continue

            html = await self.get_html_async(url)

            if not html:
                self.queue.task_done()
                continue

            self.num_pages_visited += 1
            page_data = extract_page_data(html, self.base_url)
            self.page_data[norm_url] = page_data

            for child_url in page_data["outgoing_links"]:
                await self.queue.put(child_url)

            self.queue.task_done()

    async def crawl(self):
        workers = [
            asyncio.create_task(self.worker()) for _ in range(self.max_concurrency)
        ]

        await self.queue.join()

        # Put sentinel values to stop workers
        for _ in range(self.max_concurrency):
            await self.queue.put(None)

        # Wait for workers to finish

        await asyncio.gather(*workers, return_exceptions=True)
