import pandas as pd

drugbank = pd.read_csv('/data/drugbank/processed/drugbank.tsv',sep='\t')


approved_drugs = drugbank[(drugbank['groups'].str.contains('approved'))]

print('{}'.format(approved_drugs.shape[0]))


translated = pd.read_csv('/data/drugbank/processed/drugbank_translated.tsv',sep='\t')
print('{}'.format(translated.shape[0]))
