import logging
from typing import Any, Iterable

from scrapy import Request, Spider
from scrapy.http import Response, JsonRequest

from util import get_stripped, get_all_stripped, get_list

logger = logging.getLogger('aa')

PAGE_SIZE = 10
BASE_URL = 'https://www.auswaertiges-amt.de'
LIST_URL = (f'{BASE_URL}/ajax/json-filterlist/de/search/-/1798?search=%22%22'
            f'&documenttype=1796%23AAArticle%20OR%20AAPress%20OR%20AAInterview%20OR%20AAFaq'
            f'&startfield=date&endfield=date&limit={PAGE_SIZE}')


class AASpider(Spider):
    name = 'aa'
    start_urls = [LIST_URL]

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield JsonRequest(url=url, callback=self.parse_list, dont_filter=True, meta={'offset': 0})

    def parse_list(self, response: Response):
        body = response.json()
        num_total = body.get('itemsTotal')
        next_offset = response.meta.get('offset', 0) + PAGE_SIZE

        for article in body.get('items', []):
            logger.debug(f'Found article link: {article["link"]}')
            yield response.follow(BASE_URL + article['link'], self.parse_article)

        if next_offset < num_total:
            next_link = f'{LIST_URL}&offset={next_offset}'
            logger.info(f'Found next page: {next_link}')
            yield JsonRequest(url=next_link, callback=self.parse_list, meta={'offset': next_offset})

    def parse_article(self, response: Response, **kwargs: Any):
        logger.debug(f'Parsing article page: {response.request.url}')
        content = response.css('#main')
        head = response.css('#main header')

        date = None
        desc = None
        date_type = get_stripped(head, 'span.heading__meta::text')
        if date_type is not None:
            parts = date_type.split(' - ')
            if len(parts) >= 2:
                date = parts[0]
                desc = parts[1]

        yield {
            'date': date,
            'descriptor': desc,
            'tags': get_list(content, 'section.u-section ul.link-list__list a.link-list__link::attr("title")'),
            'title': get_all_stripped(head, 'h1.heading__title *::text'),
            'teaser': get_stripped(head, 'p.heading__intro *::text'),
            'text': get_all_stripped(content, 'div.c-rte--default *::text', join_on='\n'),
            'link': response.request.url
        }
