import argparse
import asyncio
import json
import re
from json import JSONDecodeError
from typing import List, Optional

import httpx as httpx
from bs4 import BeautifulSoup

PARALLELISM = 3

phone_pattern = re.compile(r"(?:\+7|8)([\s\d()-]*)")
trash_pattern = re.compile(r"[\s()-]*")


def find_phones(raw_text: str) -> list[str]:
    def _clean_phone(dirty_phone: str) -> str:
        cleaned = trash_pattern.sub("", dirty_phone)
        if len(cleaned) == 7:
            return "8495{}".format(cleaned)
        elif len(cleaned) == 10:
            return "8{}".format(cleaned)

    return list(filter(bool, map(_clean_phone, phone_pattern.findall(raw_text))))


async def get_html(url: str) -> Optional[str]:
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code == 200:
            return r.text


def find_phones_in_schema(soup) -> List[str]:
    schema = soup.findAll("script", attrs={"type": "application/ld+json"})
    phones = []
    for item in schema:
        try:
            meta_data = json.loads(item.string)
        except JSONDecodeError:
            continue

        if "telephone" in meta_data:
            ph = find_phones(meta_data["telephone"])
            phones.extend(ph)
    return phones


def parse_html(html: str) -> List[str]:
    soup = BeautifulSoup(html, "lxml")
    phones = []
    phones.extend(find_phones_in_schema(soup))

    for tag_content in soup.body.stripped_strings:
        phones.extend(find_phones(tag_content))
    return phones


async def start_parsing(urls: List[str]):
    for url_idx in range(0, len(urls), PARALLELISM):
        batch_urls = urls[url_idx: url_idx + PARALLELISM]
        coros = [get_html(url) for url in batch_urls]
        html_results = await asyncio.gather(*coros)

        for url, html in zip(batch_urls, html_results):
            phones = parse_html(html)
            print(url, ", ".join(phones), sep="\t")


def get_url_list() -> List[str]:
    parser = argparse.ArgumentParser()
    parser.add_argument("urls", type=str, help="list of urls", nargs="+")
    parsed_args = parser.parse_args()
    return parsed_args.urls


def main():
    arg_urls = get_url_list()
    asyncio.run(start_parsing(arg_urls))


if __name__ == "__main__":
    main()
