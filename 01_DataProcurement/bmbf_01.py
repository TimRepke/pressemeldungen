import logging
from typing import Any, Iterable

from scrapy import Request, Spider
from scrapy.http import Response

from util import get_stripped, get_all_stripped, get_list

logger = logging.getLogger('bmbf')

BASE_URL = 'https://www.bmbf.de'

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}


class BMBFSpider(Spider):
    name = 'bmbf'
    start_urls = [f'{BASE_URL}/SiteGlobals/Forms/bmbf/suche/pressemitteilungen/Pressemitteilungensuche_Formular.html'
                  f'?resultsPerPage=50']

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_list, dont_filter=True, headers=HEADERS)

    def parse_list(self, response: Response):
        for link in response.css('a.c-teaser::attr("href")').getall():
            logger.debug(f'Found article link: {link}')
            yield response.follow(link, self.parse_article, headers=HEADERS)

        next_link = response.css('li.c-nav-index__item:has(strong) + li.c-nav-index__item > a::attr("href")').get()
        if next_link is not None:
            logger.info(f'Found next page: {next_link}')
            yield response.follow(f'{BASE_URL}/{next_link}', self.parse_list, headers=HEADERS)

    def parse_article(self, response: Response, **kwargs: Any):
        logger.debug(f'Parsing article page: {response.request.url}')
        content = response.css('#content')

        yield {
            'date': get_stripped(content, '.c-topline time::attr("datetime")'),
            'title': get_stripped(response, 'meta[name="title"]::attr("content")'),
            'teaser': get_stripped(response, 'meta[name="description"]::attr("content")'),
            'text': get_all_stripped(content, '.s-richtext *::text', join_on='\n'),
            'link': response.request.url
        }
