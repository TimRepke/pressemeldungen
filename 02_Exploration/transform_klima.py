import locale
import re
from datetime import date, datetime
from pathlib import Path
import json
from typing import Iterable

import numpy as np
import pandas as pd

files = Path().glob(pattern='../data/raw/*')
stock_files = [
    ('BMJ_PDF', Path('../data/BMJ/BMJ_manual_2019.xlsx')),
    ('BMEL_PDF', Path('../data/BMEL/BMEL_PDF_extract.xlsx')),
    ('BMDV_PDF', Path('../data/BMDV/BMDV_manual_2019-2021.xlsx'))
]

OUTPUT_DIR = Path('../data/texts_klima')
REGEX = re.compile(r'articles_(.+)\.jsonl')

sstrs = [re.compile(r'klima', flags=re.IGNORECASE),
         re.compile(r'\bklima\b', flags=re.IGNORECASE),
         re.compile(r'\bklimawandel\b', flags=re.IGNORECASE),
         re.compile(r'\bklimaschutz\b', flags=re.IGNORECASE),
         re.compile(r'\bumwelt\b', flags=re.IGNORECASE)]

WS = re.compile(r'\s+')
BMWK = re.compile('für Wirtschaft und Klimaschutz', flags=re.IGNORECASE)
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')


def fmt1(x):
    yr = x[:4]
    mn = x[5:7]
    dy = x[8:10]
    return date(int(yr), int(mn), int(dy))


def fmt2(x):
    yr = x[6:10]
    mn = x[3:5]
    dy = x[:2]
    return date(int(yr), int(mn), int(dy))


def fmt3(x):
    return datetime.strptime(x, '%d. %B %Y').date()


DT_FORMATS = [
    (re.compile(r'\d{4}-\d{2}-\d{2}'), fmt1),
    (re.compile(r'\d{2}\.\d{2}\.\d{4}'), fmt2),
    (re.compile(r'\d{1,2}\.\s+\w+\s+\d{4}'), fmt3),
    (re.compile(r'\d{5}'), lambda x: None)
]
DROP = re.compile(r'Stand:'
                  r'|in([ /-]+\w+)+'
                  r'|in -+'
                  r'|\d{1,2}:\d{2} Uhr'
                  r'|(Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Sonnabend|Samstag|Sonntag)')


def transform_dt(x) -> date | None:
    if x is None:
        return None
    try:
        dt = DROP.sub('', x.replace(',', '')).strip()
        for fmt, trans in DT_FORMATS:
            if fmt.match(dt):
                return trans(dt)
    except Exception as e:
        print(e)
        print(x)
    return None


def kwic(text: str | None, pattern: re.Pattern, window: int = 20) -> Iterable[tuple[str, str, str]]:
    if text:
        text = WS.sub(' ', text)
        for match in pattern.finditer(text):
            span = match.span()
            yield (text[max(0, span[0] - window):span[0]],
                   text[span[0]:span[1]],
                   text[span[1]:span[1] + window])


kwic_log = []
log = []
for file in files:
    fname = str(file)
    ministry = REGEX.findall(fname)[0].upper()
    print(f'Transforming {file}...')
    with open(file) as f:
        out_folder = OUTPUT_DIR / ministry
        out_folder.mkdir(exist_ok=True, parents=True)
        for li, line in enumerate(f):
            obj = json.loads(line)
            txt = obj.get('text')
            if txt:
                dt = transform_dt(obj['date'])
                if dt is not None:
                    out_file = out_folder / f'{ministry}_{dt.strftime("%Y-%m-%d")}_{li:04}.txt'
                else:
                    out_file = out_folder / f'{ministry}-undated-{li:04}.txt'

                txt = BMWK.sub('WuKs', txt)
                if dt and dt >= date(2021, 10, 26):

                    for l, c, r in kwic(txt, sstrs[0], 60):
                        # print(f'{l} ..|.. {c} ..|.. {r}      -> {li} in {file}')
                        kwic_log.append({
                            'left': l,
                            'target': c,
                            'right': r,
                            'line': li,
                            'source': file
                        })

                    log.append({
                        'ministry': ministry,
                        'li': li,
                        'raw_date': obj['date'],
                        'date': dt,
                        'descriptor': obj.get('descriptor', 'Pressemitteilung'),
                        'title': obj['title'],
                        'file': str(out_file),
                        'url': obj.get('link'),
                        'src': fname,
                        **{
                            f'contains_{ss.pattern}': '1' if ss.search(obj.get('text') or '0')
                                                             or ss.search(obj.get('teaser') or '0')
                                                             or ss.search(obj.get('title') or '0') else '0'
                            for ss in sstrs
                        }
                    })

                    with open(out_file, 'w') as fout:
                        fout.write((obj.get('link') or '[link missing]') + '\n')
                        fout.write((obj.get('descriptor') or '[descriptor missing]') + '\n')
                        fout.write(', '.join((obj.get('tags') or ['[tags missing]'])) + '\n')
                        fout.write((obj.get('date') or '[date missing]') + '\n')
                        fout.write((obj.get('title') or '[title missing]') + '\n')
                        fout.write((obj.get('teaser') or '[teaser missing]') + '\n')
                        fout.write('----------------\n')
                        fout.write((obj.get('text') or '[text missing]'))

for ministry, file in stock_files:
    print(f'Transforming {file}...')
    tmp = pd.read_excel(file)
    tmp = tmp.replace({np.nan: None})
    out_folder = OUTPUT_DIR / ministry
    out_folder.mkdir(exist_ok=True, parents=True)
    for li, obj in tmp.iterrows():
        txt = obj.get('full_text')
        if txt:
            dt = transform_dt(obj.get('date'))
            if dt is not None:
                out_file = out_folder / f'{ministry}_{dt.strftime("%Y-%m-%d")}_{li:04}.txt'
            else:
                out_file = out_folder / f'{ministry}-undated-{li:04}.txt'
            txt = BMWK.sub('WuKs', txt)
            if dt and dt >= date(2021, 10, 26):

                for l, c, r in kwic(txt, sstrs[0], 60):
                    kwic_log.append({
                        'left': l,
                        'target': c,
                        'right': r,
                        'line': li,
                        'source': file
                    })

                log.append({
                    'ministry': ministry,
                    'li': li,
                    'raw_date': obj['date'],
                    'date': dt,
                    'descriptor': obj.get('descriptor', 'Pressemitteilung'),
                    'title': obj['title'],
                    'url': obj.get('link'),
                    'file': str(out_file),
                    'src': str(file),
                    **{
                        f'contains_{ss.pattern}': '1' if ss.search(obj.get('text') or '0')
                                                         or ss.search(obj.get('full_text') or '0')
                                                         or ss.search(obj.get('teaser') or '0')
                                                         or ss.search(obj.get('title') or '0') else '0'
                        for ss in sstrs
                    }
                })

                with open(out_file, 'w') as fout:
                    fout.write((obj.get('link') or '[link missing]') + '\n')
                    fout.write((obj.get('descriptor') or '[descriptor missing]') + '\n')
                    fout.write(', '.join((obj.get('tags') or ['[tags missing]'])) + '\n')
                    fout.write((obj.get('date') or '[date missing]') + '\n')
                    fout.write((obj.get('title') or '[title missing]') + '\n')
                    fout.write((obj.get('teaser') or '[teaser missing]') + '\n')
                    fout.write('----------------\n')
                    fout.write((obj.get('full_text') or '[text missing]'))

df = pd.DataFrame(log)
df.to_excel(OUTPUT_DIR / 'pressemeldungen_all.xlsx')

pd.DataFrame(kwic_log).to_excel(OUTPUT_DIR / 'kwic_all.xlsx')
