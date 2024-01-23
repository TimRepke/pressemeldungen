import logging
from typing import Any, Iterable

from scrapy import Request, Spider
from scrapy.http import Response

from util import get_stripped, get_all_stripped, get_list

logger = logging.getLogger('bmg')

BASE_URL = 'https://www.bundesgesundheitsministerium.de'

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}


class BMGSpider(Spider):
    name = 'bmg'
    start_urls = [f'{BASE_URL}/presse/pressemitteilungen.html']

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_list, dont_filter=True, headers=HEADERS)

    def parse_list(self, response: Response):
        for link in response.css('.c-teaser a::attr("href")').getall():
            logger.debug(f'Found article link: {link}')
            yield response.follow(link, self.parse_article, headers=HEADERS)

        next_link = response.css('.c-pagination__item--next > a::attr("href")').get()
        if next_link is not None:
            logger.info(f'Found next page: {next_link}')
            yield response.follow(f'{BASE_URL}/{next_link}', self.parse_list, headers=HEADERS)

    def parse_article(self, response: Response, **kwargs: Any):
        logger.debug(f'Parsing article page: {response.request.url}')
        content = response.css('article')

        yield {
            'date': get_all_stripped(content, '.c-component--page-date *::text'),
            'title': get_all_stripped(content, '.c-page-title h1 *::text'),
            'teaser': get_all_stripped(content, '.c-page-title p *::text'),
            'text': get_all_stripped(content, '.c-component--content .c-text *::text, '
                                              '.c-component--content .c-quote *::text, '
                                              '.c-component--content .c-text-media *::text'),
            'link': response.request.url
        }
