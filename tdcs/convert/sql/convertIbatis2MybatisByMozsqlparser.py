import pydash
import os
import pandas
from moz_sql_parser import parse
import json
import re
from tdcs.convert.sql.lib import excel_pandas as ex2json
from tdcs.convert.sql.lib import xml_to_json as xml2json



excel_file_path = 'mapping1.xlsx'
sheet_name = 'sheet1'
make_file_path = 'mapping1.json'

# asisSqlPath = 'BASCDM08100.xsql'
asisSqlPath = 'SALSUI08300.xsql'

# ex2json.make_mapping_json_file(excel_file_path, sheet_name,make_file_path)
mappingJson = ex2json.get_mapping_json(excel_file_path, sheet_name)
asisSqlJson = xml2json.get_xml_to_json(asisSqlPath)

sqlMap = asisSqlJson['sqlMap']


insertList = sqlMap.get("insert")
selectList = sqlMap.get("select")
updateList = sqlMap.get("update")
deleteList = sqlMap.get('delete')


for sqlObj in insertList:
    sqlId = (sqlObj['@id'])
    sql = sqlObj['#text']
    # parsedJson = json.dumps(parse(sql))
    
    print(sqlId)
for sqlObj in selectList:
    sqlId = (sqlObj['@id'])
    sql = sqlObj['#text']
    parsedJson = json.dumps(parse(sql))
print("Complete!")