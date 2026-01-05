import sys
import aiohttp, asyncio
from crawl import crawl_page
from async_crawl import AsyncCrawler


def main():
    if len(sys.argv) > 2:
        print("too many arguments provided")
        exit(1)
    if len(sys.argv) < 2:
        print("no website provided")
        exit(1)

    base_url = sys.argv[1]
    print(f"starting crawl of: {base_url}")
    results, num_pages = crawl_page(base_url, debug=False)

    print(f"Visited {num_pages} pages under {base_url}")
    for url, rich_data in results.items():
        print(url, rich_data)
        print("-----------------")

    sys.exit(0)


async def main_async():

    if len(sys.argv) > 2:
        print("too many arguments provided")
        exit(1)
    if len(sys.argv) < 2:
        print("no website provided")
        exit(1)

    base_url = sys.argv[1]

    # Initialize session
    async with aiohttp.ClientSession() as client:
        crawler = AsyncCrawler(
            base_url=base_url,
            page_data={},
            max_concurrency=10,
            session=client,
            debug=True,
        )
        await crawler.async_crawl()

    for url, rich_data in crawler.page_data.items():
        print(url, rich_data)
        print("-----------------")
    print(f"Visited {crawler.num_pages_visited} pages under {crawler.base_url}")
    print(f"Unique pages: {len(crawler.page_data.keys())}")

    sys.exit(0)


if __name__ == "__main__":
    # main()
    asyncio.run(main_async())
