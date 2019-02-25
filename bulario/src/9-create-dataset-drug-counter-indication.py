import pandas as pd
import itertools
from fuzzywuzzy import fuzz



drugbank_translated = pd.read_csv('/data/drugbank/processed/drugbank_translated.tsv', sep='\t',names=['drugbank_id','name','decription','name_pt_br','description_pt_br'])
bulas_df = pd.read_csv("/data/bulario/cleansed/bulas-tagged.csv", sep=';')
bulas_df.fillna(value='---', inplace=True)

def find_drug(row, text):

    drug = dict()
    name_pt_br = row['name_pt_br'].replace('(', '').replace(')', '').lower()
    name = row['name'].replace('(', '').replace(')', '').lower()

    words = text.split(",")

    for word in words:
        if word == name_pt_br or word == name:
            drug['drugbank_id'] = row['drugbank_id'],
            drug['name_pt_br'] = row['name_pt_br']
            return drug

        elif fuzz.ratio(name_pt_br, word) >= 90:
            print('By fuzzy: {}'.format(word))
            drug['drugbank_id'] = row['drugbank_id'],
            drug['name_pt_br'] = row['name_pt_br']
            return drug
    return ''


def search_drug(df, counter_indication):

    for index_bula, row_bula in df.iterrows():

        print(row_bula['principio_ativo_keywords'])

        for index_drugbank, drug in drugbank_translated.iterrows():

            drugbank = find_drug(drug, row_bula['principio_ativo_keywords'])
            if drugbank != '':
                drugbank['disease'] = counter_indication
                drug_df = pd.DataFrame(drugbank, index=[0])

                drug_df.to_csv('/data/drugbank/processed/drugbank-counter-indications.tsv', header=False, sep='\t', index=False,mode='a')


def create_counter_indications_diseases(diseases):
    try:
        c = set(itertools.combinations(diseases, 2))
        for i in c:
            disease_df = bulas_df[(bulas_df['indicacao_keywords'].str.contains(i[0]) == True) & (bulas_df['contraindicacao_keywords'].str.contains(i[0]) == False)]
            counter_indications_df = disease_df[disease_df['contraindicacao_keywords'].str.contains(i[1]) == True]
            search_drug(counter_indications_df, i[1])

            disease_df = bulas_df[(bulas_df['indicacao_keywords'].str.contains(i[1]) == True) & (bulas_df['contraindicacao_keywords'].str.contains(i[1]) == False)]
            counter_indications_df = disease_df[disease_df['contraindicacao_keywords'].str.contains(i[0]) == True]

            search_drug(counter_indications_df, i[0])

    except Exception as err:
        print(err)

diseases = ['parkinson','diabetes', 'hipertensao', 'osteoporose', 'alzheimer']
create_counter_indications_diseases(diseases)

