import logging
from typing import Any, Iterable

from scrapy import Request, Spider
from scrapy.http import Response, JsonRequest

from util import get_stripped, get_all_stripped, get_list

logger = logging.getLogger('bmwsb')

BASE_URL = 'https://www.bmwsb.bund.de'
LIST_URL = (f'{BASE_URL}/SiteGlobals/Forms/Webs/BMWSB/suche/expertensuche-formular.html'
            f'?gts=9398922_list%253DunifiedDate_dt%2Bdesc'
            f'&documentType_=pbjournal+news+basepage+speech'
            f'&timerange=all#facets-17138440')


class BMWSBSpider(Spider):
    name = 'bmwsb'
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) '
                      'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
    }
    start_urls = [LIST_URL]

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield JsonRequest(url=url, callback=self.parse_list, dont_filter=True, meta={'offset': 0})

    def parse_list(self, response: Response):
        for link in response.css('ol > li a.c-search-teaser__link::attr("href")').getall():
            logger.debug(f'Found article link: {link}')
            yield response.follow(f'{BASE_URL}/{link}', self.parse_article)

        next_link = response.css('.navIndex ul.advancedSearch > li.forward > a::attr("href")').get()
        if next_link is not None:
            logger.info(f'Found next page: {next_link}')
            yield response.follow(f'{BASE_URL}/{next_link}', self.parse_list)

    def parse_article(self, response: Response, **kwargs: Any):
        logger.debug(f'Parsing article page: {response.request.url}')
        content = response.css('#main')

        yield {
            'date': get_stripped(content, '.c-content-stage__subheadline .c-content-stage__date::text'),
            'descriptor': get_stripped(content, '.c-content-stage__subheadline .c-content-stage__type::text'),
            'tags': get_list(content, '.c-content-stage__theme::text'),
            'title': get_all_stripped(content, 'h1.c-content-stage__headline *::text'),
            'teaser': get_all_stripped(content, 'p.c-content-stage__p *::text'),
            'text': get_all_stripped(content, '.c-content-article > p *::text'),
            'link': response.request.url
        }
