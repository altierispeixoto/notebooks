import pandas as pd
from googletrans import Translator
import requests


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


def translate(text, src, dest, hotproxy):
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
approved_drugs = drugbank[(drugbank['groups'].str.contains('approved'))]

drug_indications = pd.read_csv('/data/drugbank/processed/drugbank-indications.tsv', sep='\t', names=['drugbank_id','name_pt_br','disease']).drop_duplicates()
drug_interations = pd.read_csv('/data/drugbank/processed/drugbank_interations.tsv', sep='\t', names=['drug_interaction_id','name','description','drugbank_id'])

drug_interactions_filtered = drug_interations[(drug_interations.drugbank_id.isin(drug_indications.drugbank_id))]

drug_interactions_filtered = drug_interactions_filtered[(drug_interactions_filtered.drug_interaction_id.isin(approved_drugs.drugbank_id))]


drug_interactions_filtered = drug_interactions_filtered.fillna('')
drug = dict()
hotproxy = ''
for index, drug_interaction in drug_interactions_filtered.iterrows():

    drug['drug_interaction_id'] = drug_interaction['drug_interaction_id']
    drug['name'] = drug_interaction['name']
    drug['description'] = drug_interaction['description']
    drug['drugbank_id'] = drug_interaction['drugbank_id']

    hotproxy, drug['name_pt_br'] = translate(drug['name'], 'en', 'pt', hotproxy)

    hotproxy, drug['description_pt_br'] = translate(drug['description'], 'en', 'pt', hotproxy)

    print(drug)
    #print('{} - {} '.format(drug['name'], drug['name_pt_br']))

    drug_df = pd.DataFrame(drug, index=[0])

    drug_df.to_csv('/data/drugbank/processed/drugbank-interactions-translated.tsv', header=False, sep='\t', index=False, mode='a')

