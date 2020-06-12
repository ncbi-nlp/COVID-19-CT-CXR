"""
Usage:
    script.py [options] -i SOURCE -o DEST -f FIGURE_DIR

Options:
    -i <file>   Figure csv file
    -o <file>   Local figure csv file
    -f <dir>    Figure folder
"""

import collections
import urllib.error
import urllib.request
from pathlib import Path

import docopt
import pandas as pd
import tqdm


def get_figures(src, dest, image_dir):
    figure_df = pd.read_csv(src)

    data = []
    cnt = collections.Counter()
    for _, row in tqdm.tqdm(figure_df.iterrows(), total=len(figure_df)):
        pmc = row['pmcid']
        local_file = image_dir / '{}_{}'.format(pmc, row['figure url'])
        if not local_file.exists():
            url = 'https://www.ncbi.nlm.nih.gov/pmc/articles/{}/bin/{}'.format(pmc, row['figure url'])
            try:
                urllib.request.urlretrieve(url, local_file)
                cnt['new figure'] += 1
            except urllib.error.HTTPError:
                cnt['Http error'] += 1
                with open(local_file, 'w') as _:
                    pass
        row['figure filename'] = str(local_file.name)
        cnt['total figure'] += 1
        data.append(row)

    df = pd.DataFrame(data)
    df.to_csv(dest, index=False)

    for k, v in cnt.most_common():
        print(k, ':', v)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    get_figures(src=Path(args['-i']),
                dest=Path(args['-o']),
                image_dir=Path(args['-f']))
