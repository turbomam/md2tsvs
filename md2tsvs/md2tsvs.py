import re

import click
import markdown
# import os
# import sys
import pandas as pd
from bs4 import BeautifulSoup


@click.command()
@click.option('--mdfile', required=True, help="markdown file to parse", type=click.Path(exists=True))
def md2tsvs(mdfile):
    """convert all tables in a markdown document to TSV files."""
    file = open(mdfile)
    lines = file.read()
    file.close()

    as_html = markdown.markdown(lines, extensions=['tables'])

    soup = BeautifulSoup(as_html, 'html.parser')

    header = soup.find_all("table")[1].find("tr")

    data = []
    list_header = []

    for items in header:
        try:
            list_header.append(items.get_text())
        except:
            continue

    HTML_data = soup.find_all("table")[1].find_all("tr")[1:]

    for element in HTML_data:
        sub_data = []
        for sub_element in element:
            try:
                sub_data.append(sub_element.get_text())
            except:
                continue
        data.append(sub_data)

    dataFrame = pd.DataFrame(data=data, columns=list_header)

    # col_count = len(dataFrame.columns)

    dataFrame.drop(labels=["\n"], axis=1, inplace=True)

    # make this an option step
    meaning_count = dataFrame['Meaning']
    meaning_count = meaning_count.value_counts().rename_axis('Meaning').reset_index(name='enum_count')
    meaning_count = meaning_count.loc[~meaning_count['Meaning'].eq("")]

    # print(meaning_count)

    withcounts = dataFrame.merge(meaning_count, how="left", on="Meaning")

    wcd = withcounts.to_dict(orient="records")

    oi = [row['Other Information'] for row in [row for row in wcd]]

    oi0 = oi[0]
    # print(oi0)

    mv_pat = "'match_val': Annotation\\(tag='match_val', value='([^']*)', extensions={}, annotations={}\\)"
    mt_pat = "'match_type': Annotation\\(tag='match_type', value='([^']*)', extensions={}, annotations={}\\)"
    cos_pat = "'cosine': Annotation\\(tag='cosine', value='([^']*)', extensions={}, annotations={}\\)"

    mv_res = re.search(mv_pat, oi0)[1]
    mt_res = re.search(mt_pat, oi0)[1]
    cos_res = re.search(cos_pat, oi0)[1]
    print(mv_res)
    print(mt_res)
    print(cos_res)

    withcounts['Other Information'] = oi

    print(withcounts)

    withcounts.to_csv("table1.tsv", sep="\t", index=False)

    dict_list = []
    for i in oi:
        inner_dict = {}
        mv_res = re.search(mv_pat, i)
        mt_res = re.search(mt_pat, i)
        cos_res = re.search(cos_pat, i)
        if mv_res is not None:
            inner_dict['match_val'] = mv_res[1]
        if mt_res is not None:
            inner_dict['match_type'] = mt_res[1]
        if cos_res is not None:
            inner_dict['cosine'] = cos_res[1]
        dict_list.append(inner_dict)
    dlf = pd.DataFrame(dict_list)
    # print(dlf)

    catted = pd.concat([withcounts, dlf], axis=1)
    catted.drop(labels="Other Information", axis=1, inplace=True)
    print(catted)

    catted.to_csv("catted.tsv", sep="\t", index=False)


if __name__ == '__main__':
    md2tsvs()
