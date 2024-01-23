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

BMAS
https://www.bmas.de/SiteGlobals/Forms/Suche/Aktuelles-Suche_Formular.html?dateOfIssue_dt=2020-12-31T23%3A00%3A00Z+2021-12-31T23%3A00%3A00Z+2022-12-31T23%3A00%3A00Z&documentType_=pressrelease&showNoGesetzesstatus=true&showNoStatus=true

BMVg
https://www.bmvg.de/de/presse/alle-pressetermine-pressemitteilungen-bmvg

BMFSJF
https://www.bmfsfj.de/bmfsfj/aktuelles/presse/pressemitteilungen/106404!search?state=H4sIAAAAAAAAAFWOPQ-CMBCG_4q5uQNEg9DNoMyYsBmGBg5tUltsD78I_91SHWS797mvZ4RWEBbWXIHrQSkWcmX-09yt8EnLiX8yONw9hG33vgO8E8phgIc7alrAXgmpC6kI7XFAK9EBP9UMOtEg-XqE9TbbpB5CnCZJFkE9MbhIciXaUpz9pThicPO7L-AADN6yz02L3-CM9VLBcNWiayBozAa50Y6sf04_l-kDs-ug0_sAAAA%3D&hitsPerPage=20#search106404

BMG
https://www.bundesgesundheitsministerium.de/presse/pressemitteilungen.html

BMBF
https://www.bmbf.de/SiteGlobals/Forms/bmbf/suche/pressemitteilungen/Pressemitteilungensuche_Formular.html?gtp=33424_list%253D33&resultsPerPage=50#searchResults

BMZ
https://www.bmz.de/de/aktuelles/aktuelle-meldungen
https://www.bmz.de/de/aktuelles/archiv-aktuelle-meldungen
```