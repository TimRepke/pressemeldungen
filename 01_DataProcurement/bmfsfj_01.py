import logging
from typing import Any, Iterable

from scrapy import Request, Spider
from scrapy.http import Response

from util import get_stripped, get_all_stripped, get_list

logger = logging.getLogger('bmfsfj')

BASE_URL = 'https://www.bmfsfj.de'
START_URL = (f'{BASE_URL}/bmfsfj/aktuelles/presse/pressemitteilungen/106404!search?state=H4sIAAAAAAAAA'
             f'FWOuw7CMAxFfwV5zoAYs6FC5yJ1Qx2ixoVIISm2y6vqv5MGhnbzfVjnjmCNYEnxBjoM3qus67hUc1rjS9aNpTMw7p-'
             f'G7CEloDvjGbN5fGCQldl740LpvCCdBiSHDPrcKOhMi5LucVJwdcIVUmUu6W-3VXBPzTdoAAUf1xfR4k9wpDQh79lY5B'
             f'YydOYVMbBQQsmfPH0BauryyukAAAA%3D&sort=date+desc')

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}


class BMFSFJSpider(Spider):
    name = 'bmfsfj'
    start_urls = [START_URL]

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_list, dont_filter=True, headers=HEADERS)

    def parse_list(self, response: Response):
        for link in response.css('ul.search-list > li.teaser-list-item .teaser-headline a::attr("href")').getall():
            logger.debug(f'Found article link: {link}')
            yield response.follow(link, self.parse_article, headers=HEADERS)

        pager = response.css('.pager-container')
        next_page = pager.css('li.next > button[name="pageNum"]::attr("value")').get()
        state = pager.css('input[name="state"]::attr("value")').get()
        has_next = pager.css('li.next > button[name="pageNum"]::attr("disabled")').get()

        if has_next is None and state is not None and next_page is not None:
            next_link = (f'{BASE_URL}/bmfsfj/aktuelles/presse/pressemitteilungen/106404!search'
                         f'?state={state}&pageNum={next_page}')
            logger.info(f'Found next page: {next_link}')
            yield response.follow(f'{next_link}', self.parse_list, headers=HEADERS)

    def parse_article(self, response: Response, **kwargs: Any):
        logger.debug(f'Parsing article page: {response.request.url}')
        content = response.css('main')

        yield {
            'date': get_stripped(content, '.article-intro .dateline time::attr("datetime")')[:10],
            'descriptor': get_all_stripped(content, '.article-intro .dateline::text'),
            'title': get_all_stripped(content, '.article-intro .title__text *::text'),
            'teaser': get_all_stripped(content, '.article-intro .article-teaser *::text'),
            'text': get_all_stripped(content, '.article-content *::text'),
            'link': response.request.url
        }
