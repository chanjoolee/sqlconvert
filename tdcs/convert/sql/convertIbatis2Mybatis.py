import pydash
import os
import pandas
import json
import re
from tdcs.convert.sql.lib import excel_pandas as ex2json
from tdcs.convert.sql.lib import xml_to_json as xml2json
from fileinput import filename

def changeVariableTemplateDetail(match_obj):
    if match_obj.group(1) is not None:
        return "#{" + match_obj.group(1) + "}"
    
def changeVariableTemplate( vTxt):
    newTxt = re.sub(r'#(?P<varName>[\w]+)#', changeVariableTemplateDetail , vTxt)
    return newTxt
    # print(vTxt)
    
    

excel_file_path = 'mapping1.xlsx'
sheet_name = 'sheet1'
make_file_path = 'mapping1.json'
filenameTobe = 'BASCDM08100.xml'
asisSqlPath = 'BASCDM08100.xsql'


# ex2json.make_mapping_json_file(excel_file_path, sheet_name,make_file_path)
mappingJson = ex2json.get_mapping_json(excel_file_path, sheet_name)
asisSqlJson = xml2json.get_xml_to_json(asisSqlPath)

sqlMap = asisSqlJson['sqlMap']
# for category in sqlMap:
#     print(category)
#     query = sqlMap[category]
#     for sqlid in query:
#         print(sqlid)

insertList = sqlMap.get("insert")
selectList = sqlMap.get("select")
updateList = sqlMap.get("update")
deleteList = sqlMap.get('delete')

# pattern_insert = re.compile(r'into\s+(?P<tableName>\w+)[\s\n]+\([\s\n]*((?P<columnName>[\w]+)\s*,?\s*([/\*\s\w\d]+)?)+\)', re.IGNORECASE)
pattern_insert = re.compile(r'into\s+(?P<tableName>\w+)[\s\n]+\(([\s\n]*)?   (?P<columns>((?P<column>[\w]+)([\s\n]+)?,?([\s\n]+)?)*)   \)([\s\n\*\/]*)?values', re.IGNORECASE)
pattern_table = re.compile(r'into\s+(?P<tableName>\w+)', re.IGNORECASE)
pattern_column = re.compile(r'(?P<columnName>\b[\w]+\b),?', re.IGNORECASE)

xmlFileTobe = []
xmlFileTobe.append('<?xml version="1.0" encoding="UTF-8"?>')
vDoctype = '''
<!DOCTYPE mapper
PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
"http://mybatis.org/dtd/mybatis-3-mapper.dtd">
'''
xmlFileTobe.append(vDoctype)

vNamespace = 'com.skt.tdcs.batch.xxx'
xmlFileTobe.append('<mapper namespace="'+ vNamespace +'">')

if insertList is not None:
    for sqlObj in insertList:
        
        sqlId = (sqlObj['@id'])
        sql = sqlObj['#text']
        sqlTobe = sql
        
        # change variable 
        sqlTobe = changeVariableTemplate( sqlTobe )
        
        xmlFileTobe.append("\t<insert id=\""+sqlId + "\" parameterType=\"hashmap\" >")
        
        print('\n****** sqlId: ' + sqlId + '******\n')
        
        # match_table = pattern_table.search(sql)
        # match_column = pattern_column.search(sql)
        match_insert = pattern_insert.search(sql)
        index_columns = match_insert.re.groupindex['columns']
        regs_columns = match_insert.regs[index_columns]
        mColumns = match_insert.groupdict()['columns']
    
        # 향후 수정할 값들
        print("<<< columns_asis >>>")
        print("\t\t" + mColumns )
        mColumnsTobe = mColumns ;
        
        columnList = re.split(r',', mColumns)
        vTableName = match_insert.groupdict()['tableName']
        
        for col in columnList:
            vCol = col.strip()
            vFindCol = pydash.find(mappingJson, {'asisTableName' :vTableName.strip().upper() , 'asisColumnName': vCol.strip().upper() })
            if vFindCol is not None : 
                matchCol = re.search(r'\b'+ vCol + r'\b', mColumnsTobe, re.IGNORECASE)        
                # mColumnsTobe[matchCol.regs[0][0] : matchCol.regs[0][1] ] = vFindCol['columnName']
                mColumnsTobe = mColumnsTobe[0 : matchCol.regs[0][0] ] + vFindCol['columnName'] + "\t/* "  + vFindCol['columnNameKor'] + " */ " + mColumnsTobe[matchCol.regs[0][1]: ]
                print('\t' + vTableName + ':' + vCol + "==> " + vFindCol['columnName'] )
            else:
                print('\t' + 'column not find : ' + vTableName + ': ' +  vCol )
        print("<<< columns_tobe >>>  : ")
        print("\t" + mColumnsTobe )
        
        sqlTobe = "\t\t" + sqlTobe[0:regs_columns[0]] + mColumnsTobe + sqlTobe[regs_columns[1]:]
        
        # New XML Mybatis File
        xmlFileTobe.append(sqlTobe)
        xmlFileTobe.append("\t</insert>")
   
if selectList is not None: 
    for sqlObj in selectList:    
        sqlId = (sqlObj['@id'])
        sql = sqlObj['#text']
        sqlTobe = sql
        sqlTobe = changeVariableTemplate( sqlTobe )
    
if deleteList is not None:    
    for sqlObj in deleteList:    
        sqlId = (sqlObj['@id'])
        sql = sqlObj['#text']
        sqlTobe = sql
        sqlTobe = changeVariableTemplate( sqlTobe )
            
            
if updateList is not None:            
    for sqlObj in updateList:    
        sqlId = (sqlObj['@id'])
        sql = sqlObj['#text']
        sqlTobe = sql
        sqlTobe = changeVariableTemplate( sqlTobe )
                
xmlFileTobe.append("</mapper>")

f = open( filenameTobe , 'w',  encoding='utf8')
for vStr in xmlFileTobe:
    f.write(vStr + '\n')
f.close()



print("\n\nComplete!")


