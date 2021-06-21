# -*- coding: utf-8 -*-

"""This is a simple python template extension.

This extension should show the API in a comprehensible way. Use the module docstring to provide a \
description of the extension. The docstring should have three paragraphs: A brief description in \
the first line, an optional elaborate description of the plugin, and finally the synopsis of the \
extension.

Synopsis: <trigger> [delay|throw] <query>"""
from albert import *
import os
import requests
import json
import re
import pickle
import dataparser

__title__ = "Merriam-Webster Dictionary lookup"
__version__ = "0.0.2"
__triggers__ = "mw "
__authors__ = "mrlys"
__py_deps__ = ["requests", "json", "re", "pickle"]
#__exec_deps__ =

iconPath = iconLookup("albert")
db_file = '.webster_db'
key = os.environ['WEBSTER_KEY']
search_url = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json/%s?key='+key


# Can be omitted
def initialize():
    pass


# Can be omitted
def finalize():
    pass

def handleQuery(query):
    if not query.isTriggered:
        return

    # Note that when storing a reference to query, e.g. in a closure, you must not use
    # query.isValid. Apart from the query beeing invalid anyway it will crash the appplication.
    # The Python type holds a pointer to the C++ type used for isValid(). The C++ type will be
    # deleted when the query is finished. Therfore getting isValid will result in a SEGFAULT.

    if not len(query.string) > 2:
        item = Item()
        item.icon = iconPath
        item.text = '%s' % query.string
        item.subtext = 'At least 3 characters'
        return [item]
    db = {}
    if os.path.exists(db_file):
        debug("db file exists")
        infile = open(db_file, 'rb')
        db = pickle.load(infile)
        infile.close()
        debug("db: " + str(db))
    info(query.string)
    info(query.rawString)
    info(query.trigger)
    info(str(query.isTriggered))
    info(str(query.isValid))

    critical(query.string)
    warning(query.string)
    debug(query.string)
    debug(query.string)

    results = []
    if query.string in db:
        res = db[query.string]
    else:
        res = requests.get(search_url % query.string)
        json_result = res.json()

        info(json_result)
        data = dataparser.parse_data(json_result)
        db[query.string] = data
    data = db[query.string]
    if 'suggestions' in data:
        data = data['suggestions']
        for unit in data:
            item = Item(id=__title__,
                        icon=os.path.dirname(__file__) + "/uib_ordbok.png",
                        text='%s' % unit,
                        subtext='Suggestion',
                        completion=__triggers__ + '%s' % unit,
                        urgency=ItemBase.Notification,
                        actions=[])
            results.append(item)
    elif 'defs' in data:
        data = data['defs']
        for unit in data:
            item = Item(id=__title__,
                        icon=os.path.dirname(__file__) + "/uib_ordbok.png",
                        text='%s' % query.string,
                        subtext=unit,
                        completion=__triggers__ + '%s' % unit,
                        urgency=ItemBase.Notification,
                        actions=[])
            results.append(item)

    # Api v 0.2
    info(configLocation())
    info(cacheLocation())
    info(dataLocation())
    outfile = open(db_file, 'wb')
    pickle.dump(db, outfile)
    outfile.close()
    return results
