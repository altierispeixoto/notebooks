import os

import wget
import requests
from bs4 import BeautifulSoup


page = requests.post("http://www.anvisa.gov.br/datavisa/fila_bula/frmResultado.asp#", data={'hddPageAbsolute': 1})
soup = BeautifulSoup(page.content, 'html.parser')

pgs = []
for page in soup.find_all('label'):
    pg = page.get('onclick')
    if pg is not None:
        pg = pg.replace("fPaginar", "").replace("(","").replace(")","").replace(";","")
        pgs.append(int(pg))


def create_directory(path):
    try:
        os.mkdir(path)
    except OSError as e:
        print(e)
        print("Creation of the directory {} failed".format(path))
    else:
        print("Successfully created the directory {} ".format(path))


def realizar_download(i):
    if i % 2 != 0:
        return True
    else:
        return False


def do_page_request(i):
    page = requests.post("http://www.anvisa.gov.br/datavisa/fila_bula/frmResultado.asp#", data={'hddPageAbsolute': i})
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


for i in range(607, max(pgs) + 1):

    soup = do_page_request(i)

    path = "/data/bulario/bulas-pdf/" + str(i)
    create_directory(path)

    links = soup.find_all('a')

    for link_nr in range(1, len(links)):
        if realizar_download(link_nr):
            lk = links[link_nr]
            link = lk.get('onclick')
            if link is not None:
                params = tuple(
                    link.replace("fVisualizarBula", "").replace("(", "").replace(")", "").replace("'", "").split(","))
                print(params)
                try:
                    url = "http://www.anvisa.gov.br/datavisa/fila_bula/frmVisualizarBula.asp?pNuTransacao={}&pIdAnexo={}" \
                        .format(params[0], int(params[1]))
                    # print(url)
                    wget.download(url, path + "/" + str(i) + "-" + params[0] + "-" + str(int(params[1])) + '.pdf')
                except Exception as e:
                    print(e)
                    pass
    print("download realizado das bulas para a pasta : {} ".format(path))

