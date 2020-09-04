# -*- coding: utf-8 -*-

def process_data(processName):
    from json import load
    from os.path import join, dirname, abspath
    thisPath = dirname(abspath(__file__))
    with open(join(thisPath,'process.json'),mode="r", encoding='utf-8') as jf:
        data = load(jf)[processName]
    return data