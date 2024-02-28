import locale
import re
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


def kwic(text: str | None, pattern: re.Pattern, window: int = 20) -> Iterable[tuple[str, str, str]]:
    if text:
        text = WS.sub(' ', text)
        for match in pattern.finditer(text):
            span = match.span()
            yield (text[max(0, span[0] - window):span[0]],
                   text[span[0]:span[1]],
                   text[span[1]:span[1] + window])



log = []
for file in files:
    fname = str(file)
    ministry = REGEX.findall(fname)[0].upper()
    print(f'Transforming {file}...')
    with open(file) as f:
        for li, line in enumerate(f):
            obj = json.loads(line)
            txt = obj.get('text')
            if txt:
                txt = BMWK.sub('WuKs', txt)
                if 'klima' in txt.lower():
                    # fout.write((obj.get('title') or '[title missing]'))
                    # fout.write((obj.get('teaser') or '[teaser missing]'))
                    # fout.write((obj.get('text') or '[text missing]'))

                    for l, c, r in kwic(txt, sstrs[0], 60):
                       # print(f'{l} ..|.. {c} ..|.. {r}      -> {li} in {file}')
                        log.append({
                            'left': l,
                            'target': c,
                            'right': r,
                            'line': li,
                            'source': file
                        })

for ministry, file in stock_files:
    print(f'Transforming {file}...')
    tmp = pd.read_excel(file)
    tmp = tmp.replace({np.nan: None})
    out_folder = OUTPUT_DIR / ministry
    out_folder.mkdir(exist_ok=True, parents=True)
    for ai, obj in tmp.iterrows():
        # fout.write((obj.get('title') or '[title missing]'))
        # fout.write((obj.get('teaser') or '[teaser missing]'))
        # fout.write((obj.get('full_text') or '[text missing]'))

        for l, c, r in kwic(obj.get('full_text'), sstrs[0], 60):
            log.append({
                'left': l,
                'target': c,
                'right': r,
                'line': li,
                'source': file
            })

pd.DataFrame(log).to_excel('../data/kwic_klima.xlsx')

# for ministry, file in stock_files:
#     print(f'Transforming {file}...')
#     tmp = pd.read_excel(file)
#     tmp = tmp.replace({np.nan: None})
#     out_folder = OUTPUT_DIR / ministry
#     out_folder.mkdir(exist_ok=True, parents=True)
#     for ai, obj in tmp.iterrows():
#         # fout.write((obj.get('title') or '[title missing]'))
#         # fout.write((obj.get('teaser') or '[teaser missing]'))
#         # fout.write((obj.get('full_text') or '[text missing]'))
#
#         txt = obj.get('full_text')
#         if txt:
#             sstrs[0].search(txt)
