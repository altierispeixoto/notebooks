from Neo4JConnection import Neo4JConnection
import pandas as pd


uri = "bolt://172.17.0.2:7687"
user='neo4j'
password='neo4j2018'


neo = Neo4JConnection(uri,user,password)

#neo.delete_all()


def create_disease(dfm):
    """create diseases"""
    [neo.create_patology(name) for name in dfm['disease'].unique()] #drug_indications


def create_drugs(dfm):
    """create drugs"""
    [neo.create_principio_ativo(row['name_pt_br'], row['name'], row['drugbank_id'], row['description'], row['description_pt_br']) for index, row in dfm.iterrows()] #drug_indications_translated


def create_relationship_drug_disease(dfm):
    """create relationship between drug and disease"""
    [neo.create_relationship_drug_disease(row['drugbank_id'], row['disease']) for index, row in dfm.iterrows()] #drug_indications


def create_relationship_counter_indication_drug_disease(dfm):
    """create relationship between counter indications of drugs and diseases"""
    [neo.create_relationship_counter_indication_drug_disease(row['drugbank_id'], row['disease']) for index, row in dfm.iterrows()] #drug_counter_indications


# drug_indications = pd.read_csv('/data/drugbank/processed/drugbank-indications.tsv', sep='\t', names=['drugbank_id','name_pt_br','disease'])
# drug_indications.drop_duplicates(inplace=True)
#
# translated = pd.read_csv('/data/drugbank/processed/drugbank_translated.tsv',sep='\t',names=['drugbank_id','name','description','name_pt_br','description_pt_br'])
#
# drug_indications_translated = translated[translated['drugbank_id'].isin(drug_indications['drugbank_id'].values)]


# drug_counter_indications = pd.read_csv('/data/drugbank/processed/drugbank-counter-indications.tsv', sep='\t', names=['drugbank_id','name_pt_br','disease'])
# drug_counter_indications.drop_duplicates(inplace=True)


drug_interactions = pd.read_csv('/data/drugbank/processed/drugbank-interactions-translated.tsv', sep='\t', names=['drug_interaction_id','name','description','drugbank_id','name_pt_br','description_pt_br'])


[neo.create_drug_interaction_relationship(row['drug_interaction_id'],row['drugbank_id'], row['description_pt_br']) for index, row in drug_interactions.iterrows()]