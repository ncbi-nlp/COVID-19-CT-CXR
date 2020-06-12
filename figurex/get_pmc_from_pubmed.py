"""
Usage:
    script.py [options] -i SOURCE -o DEST

Options:
    -i <file>       LitCovid file
    -o <file>       PMC file
    -l <file>       History PMC file
"""

import io
from pathlib import Path
from typing import List, Dict
import docopt
import pandas as pd
import requests
import tqdm


def get_pmc_from_pmid(pmids: List[str]) -> Dict:
    assert len(pmids) <= 200
    url = 'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&format=csv&email=yifan.peng@nih.gov&ids='
    url += ','.join(pmids)
    x = requests.get(url)
    f = io.StringIO(x.text.strip())
    pmcdf = pd.read_csv(f, dtype=str)

    rst = {}
    for pmid, pmcid, doi in zip(pmcdf['PMID'], pmcdf['PMCID'], pmcdf['DOI']):
        if not pd.isna(pmcid):
            rst[pmid] = {'pmcid': pmcid, 'doi': doi}
    return rst


def get_pmc_from_pmid_f(src, dest, history=None):
    litcovid_df = pd.read_csv(src, sep='\t', dtype=str, comment='#')
    litcovid_data = {row['pmid']: row for _, row in litcovid_df.iterrows()}

    new_pmids = set(litcovid_df['pmid'])
    if history is not None:
        history_df = pd.read_csv(history, dtype=str)
        new_pmids = new_pmids - set(history_df['pmid'])

    pmids = list(new_pmids)
    data = []
    for i in tqdm.tqdm(range(0, len(pmids), 200)):
        results = get_pmc_from_pmid(pmids[i: i + 200])
        for k, v in results.items():
            x = {
                'pmid': k,
                'pmcid': v['pmcid'],
                'doi': v['doi'],
                'title': litcovid_data[k]['title'],
                'journal': litcovid_data[k]['journal'],
            }
            data.append(x)

    new_df = pd.DataFrame(data)
    if history is not None:
        new_df = pd.concat([history_df, new_df], axis=0)
    new_df.sort_values(by='pmid', inplace=True)
    new_df.to_csv(dest, index=False)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    get_pmc_from_pmid_f(Path(args['-i']), Path(args['-o']), args['-l'])
