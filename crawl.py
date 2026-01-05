from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import requests


def normalize_url(url: str) -> str:
    parsed_url = urlparse(url)
    normalized_url = f"{parsed_url.netloc}{parsed_url.path.rstrip('/')}"
    return normalized_url.lower()


def get_h1_from_html(html_body: str) -> str:
    soup = BeautifulSoup(html_body, "html.parser")
    h1_tag = soup.find("h1")
    return h1_tag.get_text(strip=True) if h1_tag else ""


def get_first_paragraph_from_html(html_body: str) -> str:
    soup = BeautifulSoup(html_body, "html.parser")
    main_tag = soup.find("main")
    if main_tag:
        p_tag = main_tag.find("p")
        if p_tag:
            return p_tag.get_text(strip=True)
    p_tag = soup.find("p")
    return p_tag.get_text(strip=True) if p_tag else ""


def get_urls_from_html(html_body: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html_body, "html.parser")
    urls = []
    for a_tag in soup.find_all("a"):
        href = a_tag.get("href")
        # Resolve relative URLs against the base URL
        absolute = urljoin(base_url, href)
        urls.append(absolute)
    return urls


def get_images_from_html(html_body: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html_body, "html.parser")
    images = []
    for img_tag in soup.find_all("img", src=True):
        src = img_tag["src"]
        absolute = urljoin(base_url, src)
        images.append(absolute)
    return images


def extract_page_data(html_body: str, base_url: str) -> dict:
    return {
        "h1": get_h1_from_html(html_body),
        "first_paragraph": get_first_paragraph_from_html(html_body),
        "url": base_url,
        "outgoing_links": get_urls_from_html(html_body, base_url),
        "image_urls": get_images_from_html(html_body, base_url),
    }


def get_html(url: str) -> str:
    try:
        result = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
    except Exception as e:
        return e
    if result.status_code >= 400:
        raise Exception(f"{result.status_code} found for url")
    if "text/html" not in result.headers["content-type"]:
        raise Exception(
            f"Can only parse text/html results. Not {result.headers.get('content-type')}"
        )
    return result


def parse_domain(url: str) -> str:
    return url.split("/")[0]


def crawl_page(base_url, debug=True):

    normalized_base_url = normalize_url(base_url)
    urls_to_visit = [base_url]
    num_pages_visited = 0
    page_data = {}

    while urls_to_visit:
        cur_url = urls_to_visit.pop()
        num_pages_visited += 1
        print(f"{num_pages_visited} Visiting {cur_url}")
        try:
            response = get_html(cur_url)
        except Exception as e:
            if debug:
                print(e)
            continue
        try:
            cur_data = extract_page_data(response.text, base_url)
        except Exception as e:
            print(e)
            # print(f'Unable to extract from {cur_url}')
            continue

        page_data[normalize_url(cur_url)] = cur_data
        if debug:
            print(f"Successfully extracted {cur_url}")

        for child_url in cur_data.get("outgoing_links"):
            normalized_child_url = normalize_url(child_url)

            if parse_domain(normalized_child_url) != parse_domain(normalized_base_url):
                if debug:
                    print(
                        "Domain mismatch",
                        f"{parse_domain(normalized_child_url)} != {parse_domain(normalized_base_url)}",
                    )
                continue
            if normalized_child_url in page_data:
                continue
            if debug:
                print(f"{num_pages_visited}, Visiting {normalized_child_url}")
            page_data[normalized_child_url] = {}
            urls_to_visit.append(child_url)

    return page_data, num_pages_visited
