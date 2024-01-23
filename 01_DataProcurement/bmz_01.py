import logging
from typing import Any, Iterable

from scrapy import Request, Spider
from scrapy.http import Response, JsonRequest

from util import get_stripped, get_all_stripped, get_list

logger = logging.getLogger('bmz')

BASE_URL = 'https://www.bmz.de'
LIST_URL = f'{BASE_URL}/de/aktuelles/aktuelle-meldungen'
AJAX_URL = f'{BASE_URL}/ajax/filterlist/de/aktuelles/aktuelle-meldungen/36334-36334?datefield=date'

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}


class BMZSpider(Spider):
    name = 'bmz'
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/119.0.0.0 '
                      'Safari/537.36',
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True
    }
    start_urls = [f'{AJAX_URL}&year={year}&month={month}'
                  for year in [2021, 2022, 2023, 2024]
                  for month in range(1, 13, 1)]

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_list, dont_filter=True, headers=HEADERS)

    def parse_list(self, response: Response):
        for article in response.css('.m-reports__teaser-wrapper'):
            link = article.css('a.e-teaser-report__anchor::attr("href")').get()
            logger.debug(f'Found article link: {link}')
            yield response.follow(f'{BASE_URL}{link}', self.parse_article,
                                  cb_kwargs={'pdate': get_stripped(article, '.e-teaser-report__date::text')})

    def parse_article(self, response: Response, pdate: str):
        logger.debug(f'Parsing article page: {response.request.url}')
        content = response.css('main')

        yield {
            'date': pdate,
            'descriptor': 'Pressemitteilung',
            'tags': get_all_stripped(content, '.l-detail-page__roofline-main *::text'),
            'title': get_stripped(response, 'meta[property="og:title"]::attr("content")'),
            'teaser': get_stripped(response, 'meta[property="og:description"]::attr("content")'),
            'text': get_all_stripped(content, '.rte__detailtext *::text', join_on='\n'),
            'link': response.request.url
        }
