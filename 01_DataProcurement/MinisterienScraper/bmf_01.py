import logging
from typing import Any, Iterable

from scrapy import Request, Spider
from scrapy.http import Response

logger = logging.getLogger('bmf')

BASE_URL = 'https://www.bundesfinanzministerium.de'


class BMFSpider(Spider):
    name = 'bmf'
    start_urls = [
        ('https://www.bundesfinanzministerium.de/Web/DE/Presse/Pressemitteilungen/pressemitteilungen.html'
         '?gts=%25260d98ed53-72cb-49a5-a190-6fbf6c483869_list%253DdateOfIssue_dt%252Basc'),
        ('https://www.bundesfinanzministerium.de/Web/DE/Presse/Pressemitteilungen/Pressemitteilungen-Archiv/'
         'pressemitteilungen-archiv.html?gts=%25264f02cb35-a846-493a-88ee-33d14ded5a55_list%253DdateOfIssue_dt%252Basc')
    ]

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_list, dont_filter=True)

    def parse_list(self, response: Response):
        for article in response.css('div.bmf-entry a.bmf-resultlist-teaser-link::attr("href")').getall():
            logger.debug(f'Found article link: {article}')
            yield response.follow(BASE_URL + article, self.parse_article)

        next_link = response.css('ul.bmf-navIndex-list > li.bmf-forward > a::attr("href")').get()
        if next_link is not None:
            logger.info(f'Found next page: {next_link}')
            yield response.follow(BASE_URL + next_link, self.parse_list)

    def parse_article(self, response: Response, **kwargs: Any):
        logger.debug(f'Parsing article page: {response.request.url}')
        content = response.css('#content')
        yield {
            'date': content.css('div.bmf-date::text').get().strip(),
            'descriptor': None,
            'tag': content.css('p.dachzeile::text').get().strip(),
            'title': content.css('div.article-header h1::text').get().strip(),
            'text': '\n'.join(content.css('div.article-text ::text').getall()).strip(),
            'link': response.request.url
        }
