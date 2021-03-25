from django.conf import settings
from sqlalchemy import create_engine
from pandas import read_sql, isna
from ...models import LastVersion


def readTemp(load, cve_ori, cve_act):
    engine = create_engine(f'postgresql://{settings.TEMP_FILES_USER}:{settings.TEMP_FILES_PASS}@{settings.TEMP_FILES_HOST}:{settings.TEMP_FILES_PORT}/{settings.TEMP_FILES_DBNAME}')
    dfs = {}
    dfs['cat'] = read_sql(f'select * from {load.catTable} where "filesId"=\'{load.filesId}\'', engine)
    dfs['act'] = read_sql(f'select * from {load.actTable} where "filesId"=\'{load.filesId}\'', engine)
    dfs['eqv'] = read_sql(f'select * from {load.eqvTable} where "filesId"=\'{load.filesId}\'', engine)
    equivs = {}
    if not dfs['eqv'].empty:
        equivs['ori'] = {m[cve_ori]:m for m in dfs['eqv'][isna(dfs['eqv'][cve_ori])].to_dict('records')}
        equivs['act'] = {m[cve_act]:m for m in dfs['eqv'][~isna(dfs['eqv'][cve_ori])].to_dict('records')}
    keepFields = dfs['cat'].columns.values.tolist()
    return (dfs, keepFields, equivs)

def getCatActual(loadType):
    engine = create_engine(f'postgresql://{settings.TEMP_FILES_USER}:{settings.TEMP_FILES_PASS}@{settings.TEMP_FILES_HOST}:{settings.TEMP_FILES_PORT}/{settings.TEMP_FILES_DBNAME}')
    return read_sql(f'select * from catalogos_cat_{loadType} where es_activa is true', engine)

def checkFirstLoad(loadType):
    lastVersion = LastVersion.objects.get(filesType = loadType)
    firstLoad = True
    if lastVersion.filesVersion.year >= 2000:
        firstLoad = False
    return firstLoad
