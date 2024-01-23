import logging
from typing import Any, Iterable

from scrapy import Request, Spider
from scrapy.http import Response

from util import get_stripped, get_all_stripped, get_list

logger = logging.getLogger('bmas')

BASE_URL = 'https://www.bmas.de'

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
class BMASSpider(Spider):
    name = 'bmas'
    start_urls = [f'{BASE_URL}/SiteGlobals/Forms/Suche/Aktuelles-Suche_Formular.html?documentType_=pressrelease+news&showNoGesetzesstatus=true&showNoStatus=true']

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_list, dont_filter=True, headers=HEADERS)

    def parse_list(self, response: Response):
        for link in response.css('pp-teaser pp-link::attr("href")').getall():
            logger.debug(f'Found article link: {link}')
            yield response.follow(link, self.parse_article, headers=HEADERS)

        next_link = response.css('pp-pagination-item[data-slot="pp-pagination-item-next"]::attr("href")').get()
        if next_link is not None:
            logger.info(f'Found next page: {next_link}')
            yield response.follow(f'{BASE_URL}/{next_link}', self.parse_list, headers=HEADERS)

    def parse_article(self, response: Response, **kwargs: Any):
        logger.debug(f'Parsing article page: {response.request.url}')
        content = response.css('#content')

        yield {
            'date': get_stripped(content, 'article time::attr("datetime")')[:10],
            'descriptor': get_list(content, '[nav-id="breadcrumbnavigation"] pp-breadcrumb-item::attr("text")')[-2],
            'title': get_all_stripped(content, 'article h1[data-slot="pp-headline"] *::text'),
            'teaser': get_all_stripped(content, 'article div[data-slot="pp-text"] *::text'),
            'tags': get_list(content, 'pp-document-tags pp-tag pp-link > div::text'),
            'text': get_all_stripped(content, 'article div.body-text *::text'),
            'link': response.request.url
        }
