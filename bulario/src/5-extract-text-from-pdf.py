import os
from tika import parser

path_from = '/data/bulario/bulas-pdf/'
path_to = '/data/bulario/bulas-txt/'


def list_files_from_path(path):
    files = os.listdir(path)
    f_list = []
    for name in files:
        f_list.append(path + '/' + name)
    return f_list


def parse_from_file(file):
    raw = parser.from_file(file, 'http://172.17.0.3:9998/tika')
    return raw['content']


def save_text(path, text):
    try:
        file = open(path, "w")
        file.write(text)
        file.close()
    except Exception:
        print("Can't save {} file".format(path))


def create_directory(path):
    try:
        os.mkdir(path)
    except OSError as e:
        print(e)


folder_list = list_files_from_path(path_from)

for i in range(1, 660):
    bulas_pdf = list_files_from_path(path_from + str(i))
    create_directory(path_to + str(i))
    for bula in bulas_pdf or []:
        filename = os.path.basename(bula).replace('pdf', 'txt')
        text = parse_from_file(bula)
        save_text(path_to + str(i) + '/' + filename, text)



# Can't save /data/bulario/bulas-txt/5/5-5032852017-5543506.txt file
# Can't save /data/bulario/bulas-txt/6/6-5032852017-5543506.txt file
# Can't save /data/bulario/bulas-txt/20/20-25943452016-4090727.txt file
# Can't save /data/bulario/bulas-txt/26/26-3966212013-1618062.txt file
# Can't save /data/bulario/bulas-txt/43/43-8004982017-6359797.txt file
# Can't save /data/bulario/bulas-txt/422/422-17594652017-8970699.txt file
# Can't save /data/bulario/bulas-txt/423/423-17594652017-8970699.txt file
# Can't save /data/bulario/bulas-txt/538/538-10558502018-10841468.txt file
# Can't save /data/bulario/bulas-txt/607/607-1293572019-11020139.txt file
