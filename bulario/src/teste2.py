import pandas as pd

interactions_translated = pd.read_csv('/data/drugbank/processed/drugbank-interactions-translated.tsv',sep='\t',names=['drug_interaction_id','name','description','drugbank_id','name_pt_br','description_pt_br'])

print(interactions_translated.shape)
