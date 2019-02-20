import collections
import pandas as pd
import xml.etree.ElementTree as ET

with open('/data/drugbank/raw/drugbank.xml') as xml_file:
    tree = ET.parse(xml_file)
root = tree.getroot()


rows = list()
ns = '{http://www.drugbank.ca}'
for i, drug in enumerate(root):
    row = collections.OrderedDict()

    row['drugbank_id'] = drug.findtext(ns + "drugbank-id[@primary='true']")
    row['name'] = drug.findtext(ns + "name")

    for item in drug.findall("{ns}drug-interactions/{ns}drug-interaction".format(ns=ns)):

        interation = [''.join(chid.text) for chid in item]
        interation.append(row['drugbank_id'])

        rows.append(interation)

interations_df = pd.DataFrame(rows,columns=['drug_interation_id','name','description','drugbank_id'])


interations_df.to_csv('/data/drugbank/processed/drugbank_interations.tsv', sep='\t', index=False)
