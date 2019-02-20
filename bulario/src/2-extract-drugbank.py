import collections
import pandas as pd
import xml.etree.ElementTree as ET

def collapse_list_values(row):
    for key, value in row.items():
        if isinstance(value, list):
            row[key] = '|'.join(value)
    return row

with open('/data/drugbank/raw/drugbank.xml') as xml_file:
    tree = ET.parse(xml_file)
root = tree.getroot()

ns = '{http://www.drugbank.ca}'
inchikey_template = "{ns}calculated-properties/{ns}property[{ns}kind='InChIKey']/{ns}value"
inchi_template = "{ns}calculated-properties/{ns}property[{ns}kind='InChI']/{ns}value"

rows = list()
for i, drug in enumerate(root):
    row = collections.OrderedDict()

    assert drug.tag == ns + 'drug'
    row['type'] = drug.get('type')
    row['drugbank_id'] = drug.findtext(ns + "drugbank-id[@primary='true']")
    row['name'] = drug.findtext(ns + "name")
    row['description'] = drug.findtext(ns + "description")
    # row['drug-interactions'] = [interaction.findtext(ns + 'drug-interaction') for interaction in
    #                             drug.findall("{ns}drug-interactions".format(ns=ns))]

    row['groups'] = [group.text for group in drug.findall("{ns}groups/{ns}group".format(ns=ns))]

    row['atc_codes'] = [code.get('code') for code in drug.findall("{ns}atc-codes/{ns}atc-code".format(ns=ns))]

    row['categories'] = [x.findtext(ns + 'category') for x in drug.findall("{ns}categories/{ns}category".format(ns=ns))]

    # row['inchi'] = drug.findtext(inchi_template.format(ns=ns))
    # row['inchikey'] = drug.findtext(inchikey_template.format(ns=ns))

    # Add drug aliases
    # aliases = {
    #     elem.text for elem in
    #     drug.findall("{ns}international-brands/{ns}international-brand".format(ns=ns)) +
    #     drug.findall("{ns}synonyms/{ns}synonym[@language='English']".format(ns=ns)) +
    #     drug.findall("{ns}international-brands/{ns}international-brand".format(ns=ns)) +
    #     drug.findall("{ns}products/{ns}product/{ns}name".format(ns=ns))
    #
    # }
    # aliases.add(row['name'])
    # row['aliases'] = sorted(aliases)

    rows.append(row)


columns = ['drugbank_id', 'name', 'type', 'groups', 'atc_codes', 'categories', 'description']
drugbank_df = pd.DataFrame.from_dict(rows)[columns]


drugbank_df.to_csv('/data/drugbank/processed/drugbank.tsv', sep='\t', index=False)
