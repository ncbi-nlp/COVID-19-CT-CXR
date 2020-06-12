"""
Usage:
    script.py [options] -i SOURCE -o DEST -b BIOC_DIR

Options:
    -i <file>       PMC csv file
    -o <file>       Total figure csv file
    -b <dir>        BioC folder
    --overwrite
"""

import collections
from pathlib import Path

import bioc
import docopt
import pandas as pd
import tqdm

from figurex.utils import is_file_not_empty

FIG_PASSAGE = {"fig_caption",
               "fig_title_caption",
               "fig",
               "fig_footnote",
               "fig_footnote_caption",
               "fig_footnote_title_caption"}

Figure = collections.namedtuple('figure', 'PMC url caption')


def get_figure_link(pmc, bioc_file):
    with open(bioc_file, encoding='utf8') as fp:
        c = bioc.load(fp)

    figures = []
    for doc in c.documents:
        for p in doc.passages:
            if len(p.text) == 0:
                continue
            p.text = p.text.replace('\n', ' ')
            if 'file' in p.infons and 'type' in p.infons and p.infons['type'] in FIG_PASSAGE:
                url = f'https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc}/bin/{p.infons["file"]}'
                caption = p.text.replace('\n', ' ')
                f = Figure(pmc, url, caption)
                figures.append(f)
    return figures


def get_figure_caption(src, dest, bioc_dir, overwrite=False):
    if dest.exists() and not overwrite:
        print('%s will not be overwritten' % dest.name)
        return

    df = pd.read_csv(src, dtype=str)

    data = []
    for pmc in tqdm.tqdm(df['pmcid'], total=len(df)):
        biocfile = bioc_dir / f'{pmc}.xml'
        if is_file_not_empty(biocfile):
            figures = get_figure_link(pmc, biocfile)
            for f in figures:
                data.append({
                    'pmcid': pmc,
                    'figure url': f.url[f.url.rfind('/') + 1:]
                })

    df = pd.DataFrame(data)
    df = df.drop_duplicates()
    df.to_csv(dest, index=False)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    get_figure_caption(src=Path(args['-i']),
                       dest=Path(args['-o']),
                       bioc_dir=Path(args['-b']),
                       overwrite=args['--overwrite'])
