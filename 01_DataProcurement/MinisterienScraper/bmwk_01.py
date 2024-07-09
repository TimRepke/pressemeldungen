import logging
from typing import Any, Iterable

from scrapy import Request, Spider
from scrapy.http import Response
from util import get_stripped, get_any, get_all_stripped

logger = logging.getLogger('bmwk')


class BMWKSpider(Spider):
    name = 'bmwk'
    start_urls = [
        ('https://www.bmwk.de/SiteGlobals/BMWI/Forms/Listen/Medienraum/Medienraum_Formular.html'
         '?resourceId=80d4e326-fa53-4240-b747-874d2b8e1dd2&input_=b85129ab-7314-4382-8f1c-5a6beff4f49a'
         '&pageLocale=de&templateQueryStringListen=&to=&from=&documentType_=PressRelease&documentType_.GROUP=1'
         '&cl2Categories_LeadKeyword=&cl2Categories_LeadKeyword.GROUP=1&selectSort=commonSortDate_dt+asc'
         '&selectSort.GROUP=1&selectTimePeriod=&selectTimePeriod.GROUP=1#form-80d4e326-fa53-4240-b747-874d2b8e1dd2')
    ]

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_list, dont_filter=True)

    def parse_list(self, response: Response):
        for block in response.css('ul.card-list-media-space > li.media-space-list-item div.card-block'):
            article = block.css('a.card-link-overlay::attr("href")').get()
            logger.debug(f'Found article link: {article}')
            yield response.follow(article, self.parse_article)

        next_link = response.css('div.container > ul.pagination > li > a[aria-label="Next"]')
        if next_link is not None:
            next_url = next_link.css('::attr("href")').get()
            next_title = next_link.css('::attr("title")').get()
            if next_url is not None:
                logger.info(f'Found next page ({next_title}): {next_url}')
                yield response.follow(next_url, self.parse_list)

    def parse_article(self, response: Response, **kwargs: Any):
        logger.debug(f'Parsing article page: {response.request.url}')
        head = response.css('main#main > div.main-head')
        content = response.css('main#main > div.main-content')
        yield {
            'date': get_stripped(head, 'p.topline > span.date::text'),
            'descriptor': get_stripped(head, 'p.topline > span.topline-descriptor::text'),
            'tag': get_stripped(head, 'p.topline a.tag span::text'),
            'title': get_stripped(head, '.title::text'),
            'text': get_all_stripped(content, 'div.content ::text', join_on='\n'),
            'link': response.request.url
        }
