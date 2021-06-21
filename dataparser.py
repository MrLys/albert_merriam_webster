import os
import requests
import re
import pickle

key = os.environ['WEBSTER_KEY']
search_url = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json/%s?key=' + key


def parse_data(data):
    if 'def' not in data[0]:
        return {'suggestions': data}
    _def = data[0]['def']
    if len(_def) == 1:
        _def = _def[0]
    sseq = _def['sseq']
    defs = []
    for arr in sseq:
        for innArr in arr:
            defs.extend(parse_inner_sseq_arr(innArr[1]))

    return {'defs': defs}


def parse_inner_sseq_arr(sense):
    res = []
    for elem in sense:
        if 'dt' in elem:
            res.append(parse_dt(sense[elem]))
        elif 'sense' in elem:
            res.extend(parse_inner_sseq_arr(sense[elem]))
    return res


def parse_dt(elem):
    elem = elem[0][1]
    data = elem
    data = re.sub(r'\{[a-zA-Z\_]+\|(\w+).*', r'\1', data)
    data = re.sub(r'\{\w+\}', '', data)
    data = re.sub(r'\{/\w+\}', '', data)
    return data


def get_data():
    if os.path.exists(".db"):
        infile = open(".db", 'rb')
        db = pickle.load(infile)
        infile.close()
    else:
        res = requests.get(search_url % 'voluminous');
        db = res.json()
        outfile = open('.db', 'wb')
        pickle.dump(db, outfile)
        outfile.close()
    return db


if __name__ == '__main__':
    db = get_data()
    parse_data(db)
