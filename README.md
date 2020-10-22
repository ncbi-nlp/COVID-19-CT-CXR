# Under construction

# COVID-19-CT-CXR

## Description

COVID-19-CT-CXR is a public database of COVID-19 CXR and CT images, which are automatically extracted from COVID-19-relevant articles from the PubMed Central Open Access (PMC-OA) Subset. 

The annotations, relevant text, and a local copy of figures can be found at [Releases](https://github.com/ncbi-nlp/COVID-19-CT-CXR/releases/)

## Get started

### Prepare virtual environment

```bash
$ git clone https://github.com/ncbi-nlp/COVID-19-CT-CXR.git
$ cd path/to/COVID-19-CT-CXR
$ virtualenv -p python3 /path/to/venv
$ source /path/to/venv
$ pip -r requirements.txt
```

## Prepare source file

1. Go to https://www.ncbi.nlm.nih.gov/research/coronavirus/#data-download
2. Download the "CSV" file: `/path/to/litcovid.export.csv`

## Run the script

Change the paths in `run_keys_db.sh`

```text
source_dir=$HOME'/path/to/COVID-19-CT-CXR'
venv_dir=$HOME'/path/to/venv'
top_dir=$HOME'/path/to/litcovid.export.tsv'
```

```bash
$ bash run_keys.sh step1 step2 step3 step4 step5 step6 step7 step8
```

The output is at `/path/to/litcovid.figure_text.json`

## Citing COVID-19-CT-CXR

If you're using this dataset, please cite:


Peng Y, Tang YX, Lee S, Zhu Y, Summers RM, Lu Z. [COVID-19-CT-CXR: a freely
accessible and weakly labeled chest X-ray and CT image collection on COVID-19
from the biomedical literature](https://arxiv.org/abs/2006.06177). arxiv:2006.06177. 2020.


## Acknowledgments

This work was supported by the Intramural Research Programs of the National Institutes of Health, National Library of Medicine and Clinical Center.

## Disclaimer

This tool shows the results of research conducted in the Computational Biology Branch, NCBI/NLM. The information produced on this website is not intended for direct diagnostic use or medical decision-making without review and oversight by a clinical professional. Individuals should not change their health behavior solely on the basis of information produced on this website. NIH does not independently verify the validity or utility of the information produced by this tool. If you have questions about the information produced on this website, please see a health care professional. More information about NCBI's disclaimer policy is available.
