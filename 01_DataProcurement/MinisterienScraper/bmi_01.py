import logging
from typing import Any, Iterable

from scrapy import Request, Spider
from scrapy.http import Response

from util import get_stripped, get_any, get_all_stripped

logger = logging.getLogger('bmi')
BASE_URL = 'https://www.bmi.bund.de/'


class BMISpider(Spider):
    name = 'bmi'
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) '
                      'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
    }
    start_urls = [
        ('https://www.bmi.bund.de/SiteGlobals/Forms/suche/expertensuche-formular.html'
         '?documentType_=pbjournal+basepage+interview+news+namensartikel+law+speech+project+faqlist&timerange=all')
    ]

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_list, dont_filter=True)

    def parse_list(self, response: Response):
        for article in response.css('a.c-search-teaser__link::attr("href")').getall():
            logger.debug(f'Found article link: {article}')
            yield response.follow(BASE_URL + article, self.parse_article)

        next_link = response.css('div.navIndex li.forward > a::attr("href")').get()
        if next_link is not None:
            logger.info(f'Found next page: {next_link}')
            yield response.follow(BASE_URL + next_link, self.parse_list)

    def parse_article(self, response: Response, **kwargs: Any):
        logger.debug(f'Parsing article page: {response.request.url}')
        content = response.css('#content div.c-content-article')

        yield {
            'date': get_any(content, [
                'span.c-content-stage__date::text',
                'p.dateOfRevision::text'
            ]),
            'descriptor': get_stripped(content, 'span.c-content-stage__type::text'),
            'tag': get_stripped(content, 'span.c-content-stage__theme::text'),
            'title': get_any(content, [
                'h1.c-content-stage__headline::text',
                'h1.c-header__h',
                'div.c-content-article > h1'
            ]),
            'teaser': get_stripped(content, 'p.c-content-stage__p::text'),
            'text': get_all_stripped(content, '*:not(.c-content-stage)::text', join_on='\n'),
            'link': response.request.url
        }
