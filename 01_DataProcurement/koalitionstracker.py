import logging
from typing import Iterable

from scrapy import Request, Spider
from scrapy.http import Response

from util import get_stripped, get_list

logger = logging.getLogger('oknf.koalitionstracker')

BASE = 'https://fragdenstaat.de'

class OKNFSpider(Spider):
    name = 'oknf'

    def start_requests(self) -> Iterable[Request]:
        yield Request(url=BASE + '/koalitionstracker/',
                      callback=self.parse_categories, dont_filter=True, meta={'offset': 0})

    def parse_categories(self, response: Response):
        for cat in response.css('#reveal-226216 > .row > .col'):
            links = cat.css('a::attr("href")').getall()
            names = get_list(cat, '.box-card-header > h3::text')
            for link, n in zip(links, names):
                yield response.follow(BASE + link, self.parse_category, cb_kwargs={'link': link, 'name': n})

    def parse_category(self, response: Response, link: str, name: str):
        for vorhaben in response.css('.container > .row > .col > a'):
            v_link = vorhaben.css('::attr("href")').get()
            v_name = get_stripped(vorhaben, '.box-card-header > h3::text')
            v_status = get_stripped(vorhaben, 'span.badge::text')
            yield response.follow(BASE + v_link, self.parse_vorhaben,
                                  cb_kwargs={'link': link, 'name': name,
                                             'v_link': v_link, 'v_name': v_name, 'v_status': v_status})

    def parse_vorhaben(self, response: Response, link: str, name: str, v_link: str, v_name: str, v_status: str):
        yield {
            'bereich': name,
            'bereich_link': BASE + link,
            'vorhaben': v_name,
            'vorhaben_link': BASE + v_link,
            'status': v_status,
            'ministerium': response.xpath(
                "normalize-space(//dl/dt[contains(text(), 'Federführung')]/following-sibling::dd//a[1])"
            ).get()
        }

# Run scraper:
# python -m scrapy runspider koalitionstracker.py -o ../data/koalitionstracker.jsonl
#
# Post-process jsonl:
# import pandas as pd
# import json
# with open('data/koalitionstracker.jsonl', 'r') as f:
#     data = [json.loads(line) for line in f]
#     df = pd.DataFrame(data)
#     df.to_excel('data/koalitionstracker.xlsx')
