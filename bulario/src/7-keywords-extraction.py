import pandas as pd
import nltk
from nltk import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re

#nltk.download('all')

bulas_df = pd.read_csv("/data/bulario/cleansed/bulas-topics.csv",sep=";")


def extract_words(text):
    try:
        tokens = word_tokenize(text)
        words = [word for word in tokens if word.isalpha()]
        stop_words = set(stopwords.words('portuguese'))
        words = [w for w in words if not w in stop_words]

        terms = list(set(words))
        return ",".join(terms)

    except Exception as ex:
        print(ex)
        pass


def extract_principio_ativo(text):


    print('RAW : {}'.format(text))

    text = re.sub(r'[0-9\.]+', ' ', text)
    text = re.sub('q.s.p', ' ', text)
    text = re.sub('d.c.b.', ' ', text)
    text = re.sub('equivalente', ' ', text)
    text = re.sub('informacoes ao paciente', ' ', text)

    text = text.replace('.', ' ').replace(',', ' ').replace('(', ' ').replace(')', ' ').replace(':', ' ').replace('*',' ')
    text = re.sub(' mg ', ' ', text)
    text = re.sub(' ml ', ' ', text)

    if text.find('contem') != -1:
        start_index = text.find('contem') + len('contem')
    elif text.find('composicao') != -1:
        start_index = text.find('composicao') + len('composicao')
    else:
        start_index = 0

    if text.find('excipientes') != -1:
        end_index = text.find('excipientes')

    elif text.find('excipiente') != -1:
        end_index = text.find('excipiente')

    elif text.find('exicipientes') != -1:
        end_index = text.find('exicipientes')
    elif text.find('exicipiente') != -1:
        end_index = text.find('exicipiente')
    elif text.find('veiculo') != -1:
        end_index = text.find('veiculo')
    else:
        end_index = len(text)

    print('PROCESSADO : {}'.format(text[start_index:end_index]))

    print('---------------------\n\n')
    return text[start_index:end_index]


def remove_character(text, character):
    return text.replace(character, "")

bulas_df['composicao'] = bulas_df['composicao'].map(lambda x : remove_character(x,'*'))

bulas_df['composicao_keywords'] = bulas_df['composicao'].map(lambda x : extract_words(x))
bulas_df['indicacao_keywords'] = bulas_df['indicacao'].map(lambda x : extract_words(x))
bulas_df['contraindicacao_keywords'] = bulas_df['contraindicacao'].map(lambda x : extract_words(x))

bulas_df['principio_ativo'] = bulas_df['composicao'].map(lambda x : extract_principio_ativo(x))

bulas_df['principio_ativo_keywords'] = bulas_df['principio_ativo'].map(lambda x : extract_words(x))


bulas_df.to_csv("/data/bulario/cleansed/bulas-tagged.csv", sep=';', index=False)



