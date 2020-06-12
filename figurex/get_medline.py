"""
Usage:
    script.py [options] -i SOURCE -o DEST --email EMAIL --api-key API_KEY

Options:
    -i <file>           PMC csv file
    -o <directory>      MedLine folder
    --email <str>       E-utils email
    --api-key <str>     E-utils API key
"""

import json
from io import StringIO
from pathlib import Path

import docopt
import pandas as pd
import tqdm
from Bio import Entrez, Medline


def get_medline(pmcids, dst_dir):
    fetch_handle = Entrez.efetch(db="pmc", rettype="medline", retmode="text", id=','.join(pmcids))
    try:
        data = fetch_handle.read()
        fetch_handle.close()
    except:
        return
    for record in Medline.parse(StringIO(data)):
        try:
            pmcid = record['PMC']
            dst = dst_dir / f'{pmcid}.json'
            with open(dst, 'w') as fp:
                json.dump(record, fp, indent=2)
        except:
            print('Cannot find', str(json.dumps(record, indent=2)))
            continue


def get_medline_file(src, dst_dir, batch_size=200):
    df = pd.read_csv(src)
    total_pmcids = list(df['pmcid'])
    print('Total pmcids', len(total_pmcids))
    pmcids = []
    for pmcid in tqdm.tqdm(df['pmcid'], total=len(df['pmcid'])):
        dst = dst_dir / f'{pmcid}.json'
        if not dst.exists():
            pmcids.append(pmcid)
            if len(pmcids) == batch_size:
                get_medline(pmcids, dst_dir)
                pmcids = []
    if pmcids:
        get_medline(pmcids, dst_dir)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    Entrez.email = args['--email']
    Entrez.api_key = args['--api-key']
    get_medline_file(Path(args['-i']), Path(args['-o']))
