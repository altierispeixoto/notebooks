import pandas as pd
from googletrans import Translator
import requests


hotproxy = ''

def get_proxy_list():
    url_proxy = 'https://free-proxy-list.net/'
    response = requests.get(url_proxy)
    df = pd.read_html(response.text)
    df_proxies = df[0]
    df_proxies.columns = ['ip_address', 'port', 'code', 'country', 'anonymity', 'google', 'https', 'last_checked']
    df_proxies['port'] = df_proxies['port'].astype(str).str[:-2]
    df_proxies['address'] = df_proxies['ip_address'] + ':' + df_proxies['port']

    proxy_ips = df_proxies[(df_proxies.anonymity == 'elite proxy') & (df_proxies.https == 'yes')]['address']

    return proxy_ips


def translate(text, src, dest,hotproxy):
        for proxy in get_proxy_list():
            try:

                text = text.replace(')','').replace('(','').replace('[','').replace(']','').replace('\'','')
                if len(text) > 5000:
                    return '',''
                if hotproxy == '':
                    hotproxy = proxy

                translator = Translator(proxies={'https': hotproxy}, timeout=5)
                t = translator.translate(text, dest=dest, src=src)

                if t.text != '':
                    return hotproxy, t.text.strip()

            except Exception as err:
                hotproxy = ''
                print('{} - {}'.format(err,text))


drugbank = pd.read_csv('/data/drugbank/processed/drugbank.tsv',sep='\t')
translated = pd.read_csv('/data/drugbank/processed/drugbank_translated.tsv',sep='\t',names=['drugbank_id','name','decription','name_pt_br','description_pt_br'])


approved_drugs = drugbank[(drugbank['groups'].str.contains('approved'))]
approved_drugs = approved_drugs[~approved_drugs['drugbank_id'].isin(translated['drugbank_id'].values)]


print('{}'.format(approved_drugs.shape[0]))

approved_drugs = approved_drugs.fillna('')
drug = dict()
hotproxy = ''
for index, approved_drug in approved_drugs.iterrows():

    drug['drugbank_id'] = approved_drug['drugbank_id']
    drug['name'] = approved_drug['name']
    drug['description'] = approved_drug['description']

    hotproxy, drug['name_pt_br'] = translate(drug['name'],'en','pt',hotproxy)

    hotproxy, drug['desription_pt_br'] = hotproxy,'' #translate(drug['description'],'en','pt',hotproxy)


    print('{} - {} '.format(drug['name'],drug['name_pt_br']))

    drug_df = pd.DataFrame(drug,index=[0])

    drug_df.to_csv('/data/drugbank/processed/drugbank_translated.tsv', header=False, sep='\t', index=False, mode='a')
