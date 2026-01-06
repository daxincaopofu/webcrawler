import sys
import time
import aiohttp, asyncio
from crawl import crawl_page, write_csv_report
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

    if len(sys.argv) > 4:
        print("too many arguments provided")
        exit(1)
    if len(sys.argv) < 4:
        print("not enough arguments")
        exit(1)

    base_url = sys.argv[1]
    max_concurrency = int(sys.argv[2])
    max_pages = int(sys.argv[3])

    print(f"Running with {max_concurrency} workers and {max_pages} page limit")

    start_time = time.perf_counter()

    # Initialize session
    async with AsyncCrawler(
        base_url=base_url,
        max_concurrency=max_concurrency,
        max_pages=max_pages,
        debug=True,
    ) as crawler:
        await crawler.crawl()

        for url, rich_data in crawler.page_data.items():
            print(url, rich_data)
            print("-----------------")
        print(f"Visited {crawler.num_pages_visited} pages under {crawler.base_url}")
        print(f"Unique pages: {len(crawler.page_data.keys())}")

        # Code to be timed goes here
        end_time = time.perf_counter()

        elapsed_time = end_time - start_time
        print(f"Execution time: {elapsed_time} seconds")
        return crawler.page_data


async def main_time(max_concurrency):

    if len(sys.argv) > 4:
        print("too many arguments provided")
        exit(1)
    if len(sys.argv) < 4:
        print("not enough arguments")
        exit(1)

    base_url = sys.argv[1]
    max_concurrency = int(sys.argv[2])
    max_pages = int(sys.argv[3])

    print(f"Running with {max_concurrency} workers and {max_pages} page limit")

    start_time = time.perf_counter()

    # Initialize session
    async with AsyncCrawler(
        base_url=base_url,
        max_concurrency=max_concurrency,
        max_pages=max_pages,
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

    page_data = asyncio.run(main_async())

    write_csv_report(page_data, "report.csv")

    # for n_workers in [1, 2, 5, 10]:
    #     asyncio.run(main_time(n_workers))
    #     time.sleep(2)

    sys.exit(0)
