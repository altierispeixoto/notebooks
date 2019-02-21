import re
import pandas as pd
from fuzzywuzzy import fuzz

diseases = ['parkinson','diabetes', 'hipertensao', 'osteoporose', 'alzheimer']

diseases_df = []

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

    # pattern_br = re.compile(name_pt_br)
    # pattern_en = re.compile(name)
    #
    # if re.search(pattern_br, text):
    #    return row['drugbank_id']
    # elif re.search(pattern_en, text):
    #     return row['drugbank_id']
    # else:
    #     return ''


for disease in diseases:
    disease_df = bulas_df[(bulas_df['indicacao_keywords'].str.contains(disease) == True) & (bulas_df['contraindicacao_keywords'].str.contains(disease) == False)]
    for index_bula, row_bula in disease_df.iterrows():

        print(row_bula['principio_ativo_keywords'])

        for index_drugbank, drug in drugbank_translated.iterrows():

            drugbank = find_drug(drug, row_bula['principio_ativo_keywords'])
            if drugbank != '':
                drugbank['disease'] = disease
                drug_df = pd.DataFrame(drugbank, index=[0])

                drug_df.to_csv('/data/drugbank/processed/drugbank-indications.tsv', header=False, sep='\t', index=False, mode='a')

        print('----------------')


