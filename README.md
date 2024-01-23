# Pressemeldungen


## Data procurement / scraping
In order to get the press releases by the ministries, you have to execute the scrapers like so: 
```bash
$ cd 01_DataProcurement
$ python -m scrapy runspider aa_01.py -o ../data/raw/articles_aa.jsonl
$ python -m scrapy runspider bmdv_01.py -o ../data/raw/articles_bmdv.jsonl
$ python -m scrapy runspider bmel_01.py -o ../data/raw/articles_bmel.jsonl
$ python -m scrapy runspider bmf_01.py -o ../data/raw/articles_bmf.jsonl
$ python -m scrapy runspider bmi_01.py -o ../data/raw/articles_bmi.jsonl
$ python -m scrapy runspider bmuv_01.py -o ../data/raw/articles_bmuv_archive.jsonl
$ python -m scrapy runspider bmuv_02.py -o ../data/raw/articles_bmuv_current.jsonl
$ python -m scrapy runspider bmwk_01.py -o ../data/raw/articles_bmwk.jsonl
$ python -m scrapy runspider bmwsb_01.py -o ../data/raw/articles_bmwsb.jsonl
$ python -m scrapy runspider reg_01.py -o ../data/raw/articles_reg.jsonl
$ python -m scrapy runspider bmj_01.py -o ../data/raw/articles_bmj.jsonl
$ python -m scrapy runspider bmas_01.py -o ../data/raw/articles_bmas.jsonl
$ python -m scrapy runspider bmvg_01.py -o ../data/raw/articles_bmvg.jsonl
$ python -m scrapy runspider bmfsfj_01.py -o ../data/raw/articles_bmfsfj.jsonl
$ python -m scrapy runspider bmg_01.py -o ../data/raw/articles_bmg.jsonl

BMBF
https://www.bmbf.de/SiteGlobals/Forms/bmbf/suche/pressemitteilungen/Pressemitteilungensuche_Formular.html?gtp=33424_list%253D33&resultsPerPage=50#searchResults

BMZ
https://www.bmz.de/de/aktuelles/aktuelle-meldungen
https://www.bmz.de/de/aktuelles/archiv-aktuelle-meldungen
```