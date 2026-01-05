import sys
import time
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


async def main_async(max_concurrency):

    print(f"Running with {max_concurrency} workers")

    if len(sys.argv) > 2:
        print("too many arguments provided")
        exit(1)
    if len(sys.argv) < 2:
        print("no website provided")
        exit(1)

    base_url = sys.argv[1]

    start_time = time.perf_counter()

    # Initialize session
    async with AsyncCrawler(
        base_url=base_url,
        max_concurrency=max_concurrency,
        debug=False,
    ) as crawler:
        await crawler.crawl()

        # for url, rich_data in crawler.page_data.items():
        #     print(url, rich_data)
        #     print("-----------------")
        print(f"Visited {crawler.num_pages_visited} pages under {crawler.base_url}")
        # print(f"Unique pages: {len(crawler.page_data.keys())}")

    # Code to be timed goes here
    end_time = time.perf_counter()

    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time} seconds")


if __name__ == "__main__":
    # main()

    for n_workers in [1, 2, 5, 10]:
        asyncio.run(main_async(n_workers))
        time.sleep(2)

    sys.exit(0)
