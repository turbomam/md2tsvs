import markdown
import click

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

    print(dataFrame)


if __name__ == '__main__':
    md2tsvs()
