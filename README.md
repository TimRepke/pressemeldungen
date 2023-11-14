# Pressemeldungen


## Data procurement / scraping
In order to get the press releases by the ministries, you have to execute the scrapers like so: 
```bash
$ cd 01_DataProcurement
$ python -m scrapy runspider bmwk_01.py -o ../data/raw/articles_bmwk.jsonl
$ python -m scrapy runspider bmf_01.py -o ../data/raw/articles_bmf.jsonl
```