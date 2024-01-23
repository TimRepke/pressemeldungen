import logging
from typing import Any, Iterable

from scrapy import Request, Spider
from scrapy.http import Response, JsonRequest

from util import get_stripped, get_all_stripped, get_list

logger = logging.getLogger('bmdv')

BASE_URL = 'https://bmdv.bund.de'



class BMDVSpider(Spider):
    name = 'bmdv'
    start_urls = [f'{BASE_URL}/SiteGlobals/Forms/Suche/DE/Expertensuche_Formular.html?documentType_=PressRelease',
                  f'{BASE_URL}/SiteGlobals/Forms/Suche/DE/Expertensuche_Formular.html?documentType_=Basepage']

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield JsonRequest(url=url, callback=self.parse_list, dont_filter=True, meta={'offset': 0})

    def parse_list(self, response: Response):
        for link in response.css('.search-results ul > li > div a.card-link::attr("href")').getall():
            logger.debug(f'Found article link: {link}')
            yield response.follow(f'{BASE_URL}/{link}', self.parse_article)

        next_link = response.css('ul.pagination > li.pagination-item > a.pagination-link-next::attr("href")').get()
        if next_link is not None:
            logger.info(f'Found next page: {next_link}')
            yield response.follow(f'{BASE_URL}/{next_link}', self.parse_list)

    def parse_article(self, response: Response, **kwargs: Any):
        logger.debug(f'Parsing article page: {response.request.url}')
        content = response.css('#main')

        yield {
            'date': get_stripped(content, '.content-meta-info p.number::text'),
            'descriptor': get_stripped(content, '.headline .headline-topline span.topline-format::text'),
            'tags': get_list(content, '.content-meta-info p.format::text'),
            'title': get_all_stripped(content, 'h1.headline-title *::text'),
            'teaser': get_all_stripped(content, 'h1.headline-subtitle *::text'),
            'text': get_all_stripped(content, 'div.main-content .content *::text', join_on='\n'),
            'link': response.request.url
        }
