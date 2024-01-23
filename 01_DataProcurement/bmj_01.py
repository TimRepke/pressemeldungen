import logging
from typing import Any, Iterable

from scrapy import Request, Spider
from scrapy.http import Response

from util import get_stripped, get_all_stripped

logger = logging.getLogger('bmj')

BASE_URL = 'https://www.bmj.de'

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
class BMJSpider(Spider):
    name = 'bmj'
    start_urls = [f'{BASE_URL}/SiteGlobals/Forms/Dokumenttypsuche/Dokumenttypsuche_Formular.html?nn=148026'
                  f'&folderInclude.HASH=eed2fpFDtvtyioHOwVz6jK_tIh4zwSc%3D&folderExclude=-%2FBMJ%2F*%2FRestricted'
                  f'&defaultFilter=documentType_%3APressRelease&defaultFilter.HASH=7f8aqx8Bv4VOx999EgpiDtKxIGzL7E0%3D'
                  f'&callerId.HASH=818bKvjZjjdad0vcaEpNJaQbOhKvnok%3D'
                  f'&folderExclude.HASH=45eapg3qTQ140sxaYkSoqXsuauF-7XE%3D'
                  f'&folderInclude=%2FBMJ%2FDE%2F*+%2FBMJ%2FEN%2F*+%2FBMJ%2FSharedDocs%2F*&callerId=110490']

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_list, dont_filter=True, headers=HEADERS)

    def parse_list(self, response: Response):
        for link in response.css('a.c-teaser__link::attr("href")').getall():
            logger.debug(f'Found article link: {link}')
            yield response.follow(f'{BASE_URL}/{link}', self.parse_article, headers=HEADERS)

        next_link = response.css('nav.c-nav-index li.c-nav-index__item--next > a::attr("href")').get()
        if next_link is not None:
            logger.info(f'Found next page: {next_link}')
            yield response.follow(f'{BASE_URL}/{next_link}', self.parse_list, headers=HEADERS)

    def parse_article(self, response: Response, **kwargs: Any):
        logger.debug(f'Parsing article page: {response.request.url}')
        content = response.css('#content')

        yield {
            'date': get_stripped(content, '.c-meta-info > time::attr("datetime")')[:10],
            'descriptor': 'Pressemitteilung',
            'title': get_all_stripped(content, 'h1.c-page-intro__headline *::text'),
            'teaser': get_all_stripped(content, '.c-page-intro__text *::text'),
            'text': get_all_stripped(content, '.s-richtext *::text', join_on='\n'),
            'link': response.request.url
        }
