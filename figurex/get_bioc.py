"""
Usage:
    script.py -i SOURCE -o DEST_DIR

Options:
    -i <file>           PMC csv file
    -o <directory>      BioC folder
"""

import collections
import urllib.error
import urllib.request
from pathlib import Path

import docopt
import pandas as pd
import tqdm

from figurex.utils import is_file_not_empty


def get_bioc(pmid, dest):
    url = f'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/{pmid}/unicode'
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')
    with open(dest, 'w', encoding='utf8') as fp:
        fp.write(text)


def get_bioc_f(src, dest_dir):
    df = pd.read_csv(src, dtype=str)
    cnt = collections.Counter()
    for pmid, pmc in tqdm.tqdm(zip(df['pmid'], df['pmcid']), total=len(df)):
        if not pmid:
            continue

        cnt['total pmc'] += 1
        biocfile = dest_dir / f'{pmc}.xml'

        if biocfile.exists():
            if is_file_not_empty(biocfile):
                cnt['total bioc'] += 1
            continue

        try:
            get_bioc(pmid, biocfile)
            cnt['total_bioc'] += 1
            cnt['new bioc'] += 1
        except urllib.error.HTTPError:
            with open(biocfile, 'w') as _:
                pass
    for k, v in cnt.most_common():
        print(k, ':', v)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    get_bioc_f(src=args['-i'], dest_dir=Path(args['-o']))
