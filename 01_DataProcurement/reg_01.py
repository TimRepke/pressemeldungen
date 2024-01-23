import json
import logging
from typing import Any, Iterable

from scrapy import Request, Spider, Selector
from scrapy.http import Response, JsonRequest

from util import get_stripped, get_all_stripped, get_list

logger = logging.getLogger('bundesregierung')
BASE_URL = 'https://www.bundesregierung.de'


class BundesregierungSpider(Spider):
    name = 'bundesregierung'
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) '
                      'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'DOWNLOAD_DELAY': 0.25,
        'RANDOMIZE_DOWNLOAD_DELAY': True
    }

    # start_urls = [
    #     'https://www.bundesregierung.de/breg-de/service/archiv'
    #     '?f=1982102%3ABPAArticle--1982102%3ABPAInterview--1982102%3ABPAPressConference--1982102%3'
    #     'ABPAPressRelease--1982102%3ABPASpeech',
    #     'https://www.bundesregierung.de/breg-de/aktuelles/pressemitteilungen?page=1'
    # ]

    def start_requests(self) -> Iterable[Request]:
        # Recent press release search
        yield JsonRequest(url='https://www.bundesregierung.de/breg-de/suche/1000406!searchJson',
                          data={
                              'search': {'query': '', 'zipCodeCityQuery': '', 'sortOrder': 'sortDate desc', 'page': 1},
                              'filters': []
                          },
                          method='POST',
                          callback=self.parse_list, dont_filter=True)

        # Archive search
        yield JsonRequest(url='https://www.bundesregierung.de/breg-de/service/archiv/1982110!searchJson',
                          data={
                              'search': {'query': '', 'zipCodeCityQuery': '', 'sortOrder': 'sortDate desc', 'page': 1},
                              'filters': ['1982102:BPAArticle', '1982102:BPAInterview', '1982102:BPAPressConference',
                                          '1982102:BPAPressRelease', '1982102:BPASpeech']
                          },
                          method='POST',
                          callback=self.parse_list, dont_filter=True)

    def parse_list(self, response: Response):
        body = response.json()
        result = body.get('result', {})
        curr_page = result.get('page')
        num_pages = result.get('pageCount')

        for article in result.get('items', []):
            entry = Selector(text=article['payload'])
            link = entry.css('.bpa-link::attr("href")').get()
            logger.debug(f'Found article link: {link}')
            yield response.follow(f'{BASE_URL}{link}', self.parse_article)

        if curr_page < num_pages:
            logger.info(f'Fetching next page ({curr_page + 1}/{num_pages})')
            payload = json.loads(response.request.body)
            payload['search']['page'] += 1
            yield JsonRequest(url=response.request.url, data=payload, method='POST', callback=self.parse_list)

    def parse_article(self, response: Response, **kwargs: Any):
        logger.debug(f'Parsing article page: {response.request.url}')
        content = response.css('#main')

        date = content.css('.bpa-time time::attr("datetime")').get()
        if date is None:
            date = get_stripped(content, '.bpa-government-declaration-place-date *::text')

        yield {
            'date': date,
            'descriptor': 'Pressemitteilung' if content.css('.bpa-collection-item') else 'Other',
            'tags': None,
            'title': get_all_stripped(content, '.bpa-teaser-title-text *::text'),
            'teaser': get_all_stripped(content, '.bpa-short-text p:not([class]) *::text'),
            'text': get_all_stripped(content, '.bpa-article *::text', join_on='\n'),
            'link': response.request.url
        }
