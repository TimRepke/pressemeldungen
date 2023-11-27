import logging
from typing import Any, Iterable

from scrapy import Request, Spider
from scrapy.http import Response, JsonRequest

from util import get_stripped, get_all_stripped, get_list

logger = logging.getLogger('bmuv')

BASE_URL = 'https://www.bmuv.de'
LIST_URL = f'{BASE_URL}/presse/pressemitteilungen'


class BMUVSpider(Spider):
    name = 'bmuv'
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) '
                      'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
    }
    start_urls = [LIST_URL]

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield JsonRequest(url=url, callback=self.parse_list, dont_filter=True, meta={'offset': 0})

    def parse_list(self, response: Response):
        for link in response.css('.c-articles-list article a::attr("href")').getall():
            logger.debug(f'Found article link: {link}')
            yield response.follow(f'{BASE_URL}{link}', self.parse_article)

        next_link = response.css('li.c-pagination__item--next a::attr("href")').get()
        if next_link is not None:
            logger.info(f'Found next page: {next_link}')
            yield response.follow(f'{BASE_URL}{next_link}', self.parse_list)

    def parse_article(self, response: Response, **kwargs: Any):
        logger.debug(f'Parsing article page: {response.request.url}')
        content = response.css('#article')

        topic = None
        tpc = get_all_stripped(content, '.u-typo\:s *::text')
        if tpc is not None and len(tpc) > 0:
            parts = tpc.split('|')
            if len(parts) >= 3:
                topic = parts[2]

        yield {
            'date': get_all_stripped(content, '.c-hero .c-hero__rubric *::text'),
            'descriptor': 'Pressemitteilung',
            'tags': [topic] if topic is not None else None,
            'title': get_all_stripped(content, '.c-hero h1 *::text'),
            'teaser': get_all_stripped(content, '[itemprop="articleBody"] h2 *::text'),
            'text': get_all_stripped(content, '[itemprop="articleBody"] div[itemprop="description"] *::text'),
            'link': response.request.url
        }
