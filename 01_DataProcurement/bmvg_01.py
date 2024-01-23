import json
import logging
from typing import Any, Iterable

from scrapy import Request, Spider
from scrapy.exceptions import NotSupported
from scrapy.http import Response, JsonRequest

from util import get_stripped, get_all_stripped, get_list

logger = logging.getLogger('bmvg')

BASE_URL = 'https://www.bmvg.de'
START_URL = (f'{BASE_URL}/service/queryListFilter/10834?filters%5BFormat%5D=7442%2C7434%2C5019424'
             f'&darkTheme=false&mediathek=false&requiresFallbackImage=true')
PAGE_SIZE = 6


class BMVGSpider(Spider):
    name = 'bmvg'
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) '
                      'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
    }
    start_urls = [START_URL]

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield JsonRequest(url=url, callback=self.parse_list, dont_filter=True, cb_kwargs={'offset': 0})

    def parse_list(self, response: Response, offset: int) -> Iterable[Request]:

        json_response = json.loads(response.text)

        for item in json_response['items']:
            link = item['linkHref']
            logger.debug(f'Found article link: {link}')
            yield response.follow(link, self.parse_article)

        total = json_response['totalItemCount']
        if offset < total:
            logger.info(f'There is more data (offset: {offset}, total: {total})')
            yield response.follow(f'{START_URL}&offset={offset + PAGE_SIZE}',
                                  self.parse_list, cb_kwargs={'offset': offset + PAGE_SIZE})

    def parse_article(self, response: Response, **kwargs: Any):
        logger.debug(f'Parsing article page: {response.request.url}')
        try:
            content = response.css('main')
            dt = get_stripped(content, '.content-header__headline-date time::attr("datetime")')
            yield {
                'date': dt[:10] if dt is not None else None,
                'descriptor': get_all_stripped(content, '.content-header__headline-label *::text'),
                'title': get_all_stripped(content, 'h1.content-header__headline-text *::text'),
                'text': get_all_stripped(content, '.section__content *::text'),
                'link': response.request.url
            }
        except NotSupported as e:
            logger.warning(f'Failed to parse article: {e}')
