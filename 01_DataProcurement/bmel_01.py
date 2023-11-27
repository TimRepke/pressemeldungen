import logging
from typing import Any, Iterable

from scrapy import Request, Spider
from scrapy.http import Response, JsonRequest

from util import get_stripped, get_all_stripped, get_list

logger = logging.getLogger('bmel')

BASE_URL = 'https://www.bmel.de'
LIST_URL = (f'{BASE_URL}/SiteGlobals/Forms/Suche/DE/Pressemitteilungssuche/Pressemitteilungssuche_Formular.html?resultsPerPage=50')


class BMELSpider(Spider):
    name = 'bmel'
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) '
                      'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
    }
    start_urls = [LIST_URL]

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield JsonRequest(url=url, callback=self.parse_list, dont_filter=True, meta={'offset': 0})

    def parse_list(self, response: Response):
        for link in response.css('.searchresult .row a::attr("href")').getall():
            logger.debug(f'Found article link: {link}')
            yield response.follow(f'{BASE_URL}/{link}', self.parse_article)

        next_link = response.css('li.c-pagination__item--active + li > a::attr("href")').get()
        if next_link is not None:
            logger.info(f'Found next page: {next_link}')
            yield response.follow(f'{BASE_URL}/{next_link}', self.parse_list)

    def parse_article(self, response: Response, **kwargs: Any):
        logger.debug(f'Parsing article page: {response.request.url}')
        content = response.css('#content')

        yield {
            'date': get_stripped(content, '.c-teaser__meta time::attr("datetime")'),
            'descriptor': 'Pressemitteilung',
            'tags': get_list(content, '.c-content-stage__theme::text'),
            'title': get_all_stripped(content, 'h1.c-intro__headline *::text'),
            'teaser': get_all_stripped(content, 'div.c-intro__text *::text'),
            'text': get_all_stripped(content, '#content p *::text'),
            'link': response.request.url
        }
