import os
from unicodedata import normalize
import pandas as pd


def read_file(textfile):
    temp = open(textfile, 'r').read().split('\n')
    file = []
    for line in temp:
        if line != '':
            file.append(line)
    return file


def remover_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')


def get_files(path):
    f_list = []
    for r, d, f in os.walk(path):
        for file in f:
            if ".txt" in file:
                f_list.append(os.path.join(r, file))
    return f_list


def find_topic(file, topic):
    for i in range(0, len(file)):
        line = remover_acentos(file[i].lower())
        if line.find(topic) != -1:
            return True
    return False


def find_topic_line(file, topic):
    for i in range(0, len(file)):
        line = remover_acentos(file[i].lower())
        if line.find(topic) != -1:
            return i
    return -1


def cleanse_text(text):
    new_text = text.lower()

    return remover_acentos(new_text)


def extract_topics(bulas):
    bulas_padrao = []
    cnt_topic = 0
    for bula in bulas:
        text = read_file(bula)

        comp = find_topic(text, 'composicao')  # or find_topic(text,'composicoes')
        topic1 = find_topic(text,
                            'para que este medicamento e indicado')  # or find_topic(text,'para que este medicamento foi indicado') or find_topic(text,'1. indicacoes')
        topic2 = find_topic(text, 'como este medicamento funciona')
        topic3 = find_topic(text,
                            'quando nao devo usar este medicamento')  # or find_topic(text,'quando nao devo utilizar este medicamento') or find_topic(text,'quando nao devo tomar este medicamento')
        topic4 = find_topic(text,
                            'o que devo saber antes de usar este medicamento')  # or find_topic(text,'quando nao devo utilizar este medicamento') or find_topic(text,'quando nao devo tomar este medicamento')

        if comp and topic1 and topic2 and topic3 and topic4:
            cnt_topic = cnt_topic + 1

            index_composicao = find_topic(text, 'composicao')  # or find_topic_line(text,'composicoes')
            index_topic1 = find_topic_line(text,
                                           'para que este medicamento e indicado')  # or find_topic(text,'para que este medicamento foi indicado') or find_topic(text,'1. indicacoes')
            index_topic2 = find_topic_line(text, 'como este medicamento funciona')
            index_topic3 = find_topic_line(text,
                                           'quando nao devo usar este medicamento')  # or find_topic(text,'quando nao devo utilizar este medicamento') or find_topic(text,'quando nao devo tomar este medicamento')
            index_topic4 = find_topic_line(text,
                                           'o que devo saber antes de usar este medicamento')  # or find_topic(text,'quando nao devo utilizar este medicamento') or find_topic(text,'quando nao devo tomar este medicamento')

            composicao = cleanse_text(''.join(text[index_composicao + 1:index_topic1]))
            indicacao = cleanse_text(''.join(text[index_topic1 + 1:index_topic2]))
            contra_indicacao = cleanse_text(''.join(text[index_topic3 + 1:index_topic4]))

            bulas_padrao.append((bula, composicao, indicacao, contra_indicacao))

    bulas_df = pd.DataFrame(bulas_padrao, columns=['filename', 'composicao', 'indicacao', 'contraindicacao'])
    print("Total de bulas cotendo os tópicos : {}".format(cnt_topic))
    return bulas_df



path='/data/bulario/bulas-txt/'
files = get_files(path)
df = extract_topics(files)
df.to_csv("/data/bulario/cleansed/bulas-topics.csv",sep=";",index=False)

# Total de bulas cotendo os tópicos : 6112