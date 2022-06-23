import pydash
import os
import subprocess
from fnmatch import fnmatch
import pandas
import requests
import json
import re
import sqlparse
from tdcs.convert.sql.lib import excel_pandas as ex2json
from tdcs.convert.sql.lib import xml_to_json as xml2json
from pathlib import Path
import datetime
from pandas.io.common import file_path_to_url
import pyperclip
import codecs


g_keyword = [
    'Count',
    'SELECT',
    'UPDATE',
    'DELETE',
    'SUBSTR',
    'DECODE',
    'sysdate',
    'SYSDATE'
]

mappingJson = []
mappingJson1 = {}
mode ='bat' # bat dis acc

def get_query_columns(_sql):
    stmt = sqlparse.parse(_sql)[0]
    columns = []
    column_identifiers = []

    # get column_identifieres
    in_select = False
    for token in stmt.tokens:
        if isinstance(token, sqlparse.sql.Comment):
            continue
        if str(token).lower() == 'select':
            in_select = True
        elif in_select and token.ttype is None:
            for identifier in token.get_identifiers():
                column_identifiers.append(identifier)
            break

    # get column names
    for column_identifier in column_identifiers:
        columns.append(column_identifier.get_name())

    return columns

def get_columns(_token):
    v_columns = []
    if _token.tokens is not None :
        for token in _token.tokens:
            if type(token) == sqlparse.sql.IdentifierList :
                for token1 in token.tokens:
                    if type(token1) == sqlparse.sql.Identifier :
                        v_columns.append(token1.get_name())
    return v_columns


def replace_columns(_subParenthesToken):
    v_columns = []
    vTableName = ''
    if _subParenthesToken.tokens is not None :
        for token in _subParenthesToken.tokens:
            if type(token) == sqlparse.sql.IdentifierList :
                for token1 in token.tokens:
                    if type(token1) == sqlparse.sql.Identifier :
                        v_columns.append(token1.get_name())
                        # replace
                        vCol = token1.get_name()
                        
                        # vFindCol = pydash.find(mappingJson, {'asisTableName' : vTableName.strip().upper() , 'asisColumnName': vCol.strip().upper() })
                        v_find_table = mappingJson1.get(vTableName.strip().upper())
                        if ( v_find_table is not None) :
                            vFindCol = pydash.find(v_find_table, { 'asisColumnName': vCol.strip().upper() })
                        
                        vColComent = vFindCol['columnName']
                        vTableName = get_table_name(token1)
                        
                        
         
def get_table_token( _token ):
    aaaTTT = ""
    
def get_table_name( _token ):
    v_rtn = ''
    v_rtn = _token.get_name()
    return v_rtn
    
def getSubParenthesis(_token):
    rtnToken = None
    if _token.tokens is not None :
        for token in _token.tokens:
            if token._get_repr_name() == 'Parenthesis':
                rtnToken = token
                break
    return rtnToken

def make_columnMaping_file(_excel_file_path , _sheet_name , _to_file_path):
    _mappingJson = ex2json.make_mapping_json_file(_excel_file_path, _sheet_name, _to_file_path)
    
def make_columnMaping(_excel_file_path , _sheet_name):
    _mappingJson = ex2json.get_mapping_json(_excel_file_path, _sheet_name)
    return _mappingJson
    
def read_columnMapping_file(_json_file_path):
    global mappingJson
    with open(_json_file_path , 'r' ,encoding="UTF-8" ) as file:
        mappingJson = json.load(file)
    
def make_asisSqlToJson( _asisSqlPath ):
    _asisSqlJson = xml2json.get_xml_to_json(_asisSqlPath)
    return _asisSqlJson

def make_mappingJson():
    global mappingJson
    global mappingJson1
    excel_file_path = 'mapping1.xlsx'
    sheet_name = 'sheet1'
    
    # mappingJson = make_columnMaping(excel_file_path, sheet_name)
    # json_file_path = 'mapping1.json'
    # json_file_path = 'table_mapping_202204211336.json' 
    json_file_path = 'mapping_0520.json' 
    read_columnMapping_file(json_file_path)
    mappingJson1 = pydash.group_by(mappingJson, ['asisTableName'])

def main():
    global mode
    make_mappingJson()

    date_format = get_date_format()
    # # #### by file 
    # # asisSqlPath=r'C:\dev\workapace_sql\tdcs-batch\sqlconvert\batch\java\com\sktps\batch\bas\bi\db\BASBIB06.xsql'
    # asisSqlPath=r'C:\dev\workspace\tdcs-batch-sql\sqlconvert\batch\java\com\sktps\batch\vrf\sui\db\VRFSUI08700.xsql'
    # convertByFile(asisSqlPath , None, date_format )
    
    
    ### by Folder
    # 배치
    path_from = r'C:\dev\workspace\tdcs-batch-sql\sqlconvert\batch'
    mode = 'batch'
    # 재고
    # path_from = r'C:\dev\workspace\tdcs-batch-sql\sqlconvert\dis'
    # mode = 'dis'
    # 정산
    # path_from = r'C:\dev\workspace\tdcs-batch-sql\sqlconvert\acc'
    # mode = 'acc'
    print("Start By Foler")
    print("Folder : " + path_from)
    print("DateFormat" + date_format)
    # convertByFolder(path_from, date_format)
    # report 
    report_info = {'asisTableName':'TBAS_DEAL_CO_MGMT', 'asisColumnName': 'ORG_ID2' }
    convertByFolder(path_from, date_format, report_info)
    

def convertByFolder(path_from , date_format , report_info=None):
    file_list = []
    file_pattern = "*.xsql"
    for path, subdirs, files in os.walk(path_from):
        for name in files:
            if fnmatch(name, file_pattern):
                file_list.append({
                    "full_path": os.path.join(path,name)
                    ,"file_path": path
                    , "file_name" : name
                })
    
    if report_info is not None:
        report_info['report_file_path'] = path_from +  '_report_column_' +  '_' + report_info['asisTableName'] +'_' + report_info['asisColumnName'] + '_' + date_format + '.yml'
        report_info['report_file_count'] = 0
        report_info['report_used_count'] = 0
        f = open( report_info['report_file_path'] , 'w',  encoding='utf8')
        f.write('asisTableName:\t' + report_info['asisTableName'] + '\n' )
        f.write('asisColumnName:\t' + report_info['asisColumnName'] + '\n' )
        f.close()
        
    for idx,path_info in enumerate(file_list):
        print('file process' + str(idx+1) + '/' +   str(len(file_list)))
        print("<<<< " + path_info['full_path'] + ">>>>>")
        file_path = path_info['file_path']
        sub_path = file_path[len(path_from):]
        file_name = path_info['file_name']
        path_to = path_from +  '_' +  date_format + sub_path 
        if report_info is None :
            make_dir_recursive(path_to)
        convertByFile(path_info['full_path'], os.path.join(path_to, file_name) , None , report_info )
    
    if report_info is not None:
        f = open( report_info['report_file_path'] , 'a',  encoding='utf8')
        f.write('Total ' + str(report_info['report_file_count'] ) + ' File Used\n')
        f.write('Total ' + str(report_info['report_used_count'] ) + ' Count Used')
        f.close()
       
    print("\n")      
    print("Convert convertByFolder Complete!")

def make_dir_recursive( full_path ):
    path_split = full_path.split('\\')
    cur_path = ""
    for idx, path in enumerate(path_split):
        if idx == 1:
            #  C: 드라이브에서는 에러
            cur_path = os.path.join(cur_path + "\\" , path)
        else:
            cur_path = os.path.join(cur_path , path)
        if not os.path.exists(cur_path) :
            os.mkdir(cur_path)
        
def convertByFile(asisSqlPath , tobePath , date_format , report_info=None  ):
    try: 
        asisSqlJson = make_asisSqlToJson(asisSqlPath)
        
        
        sqlMap = asisSqlJson.get('sqlMap')
        if sqlMap is None : 
            sqlMap = asisSqlJson.get('mapper')
        
        for sqlList in sqlMap:
            if type(sqlMap[sqlList]) == str :
                continue
            if pydash.includes(['select','insert','update','delete','procedure'], sqlList) :
                for sqlObj in pydash.concat([],sqlMap.get(sqlList)):
                    
                    sqlId = (sqlObj['@id'])
                    print('\t\t' + sqlId) 
                    print('\t\tStart : ' + get_date_format())
                    sql = sqlObj['#text']
                    sqlTobe = sql                    
                    # change variable 
                    sqlTobe = changeVariableTemplate( sqlTobe )
                    
                    parse = sqlparse.parse(sqlTobe)
                    sqlObj['parse'] = parse
                    sqlObj['sqlOrigin'] = sql
                    if sqlList == 'procedure' : 
                        continue
                    if sqlId.startswith("call_") : 
                        continue
                    
                    for vToken in parse[0].tokens : 
                        if vToken.is_whitespace :
                            continue
                        if vToken._get_repr_name() == 'Comment':
                            # vToken.value = setCommentCj(vToken.value)
                            continue
                        # table check
                        if is_pre_error(vToken) :
                            continue
                        
                        processColumnToken(vToken , sqlId , sqlList)
                    print('\t\tEnd : ' + get_date_format())
        
        tobe_xml_path = ""
        if tobePath is not None: 
            tobe_xml_path = make_tobe_filepath(tobePath , None)
        else:
            tobe_xml_path = make_tobe_filepath(asisSqlPath , date_format)
        vNamespace = 'com.skt.tdcs.batch.xxx'        
        vNamespace = sqlMap.get("@namespace")
        
        # print("\t\t<<<<<   write_to_xml >>>>>>\n")
        if report_info is not None:
            reportInfos = reportForColumnChangeByFile(sqlMap , vNamespace , report_info['asisTableName'] , report_info['asisColumnName'])
            if len(reportInfos) > 0 :
                report_info['report_file_count'] = report_info['report_file_count'] + 1
                f = open( report_info['report_file_path'] , 'a',  encoding='utf8')
                f.write('\t' + vNamespace + '\n' )
                for info in reportInfos:
                    report_info['report_used_count'] = report_info['report_used_count'] + len(info['report_infos'])
                    f.write('\t\t' + info['sqlId'] + ': ' + str(len(info['report_infos'])) + ' Used' + '\n' )
                    # for map_info in info['report_infos'] : 
                    #     f.write('\t\t\tasisTableName:\t' + map_info['mapping_info']['asisTableName'] + '\n' )
                    #     f.write('\t\t\tasisColumnName:\t' + map_info['mapping_info']['asisColumnName'] + '\n' )
                    #     f.write('\t\t\ttableName:\t' + map_info['mapping_info']['tableName'] + '\n' )
                    #     f.write('\t\t\ttableNameKor:\t' + map_info['mapping_info']['tableNameKor'] + '\n' )
                    #     f.write('\t\t\t\t' + map_info['sql'] + '\n' )
                f.write('\n' )
                f.close()
        else:
            write_to_xml( tobe_xml_path , sqlMap , vNamespace )           
        print("\t\tComplete")
    
    except Exception as e:
        print('Error')
        print(str(e))
        pass

def convertByInput(sql):
    # sql = '''
    #     UPDATE TBAS_BAT_LOG SET 
    #         END_DTM = TO_CHAR(SYSDATE, 'YYYYMMDDHH24MISS')
    #     ,   RMKS= #RMKS#
    #     ,   UPD_CNT = UPD_CNT+1
    #     ,   MOD_DTM = TO_CHAR(SYSDATE, 'YYYYMMDDHH24MISS')
    #     ,   OP_RSLT = 'S'
    #     WHERE  PROG_ID = 'BASBIB28' 
    #       AND OP_DT= #OP_DT#       
    # 
    # '''
    
    sql1 = changeVariableTemplate( sql )
    sqlTobe = []
    parse = sqlparse.parse(sql1)
    for vToken in parse[0].tokens : 
        if vToken.is_whitespace :
            continue
        if vToken._get_repr_name() == 'Comment':
            continue
        # table check
                
        if is_pre_error(vToken) :
            continue
        
        processColumnToken(vToken , "xxx" , "xxx")
        
    convert_sql_recursive( sqlTobe , parse[0] ) 
    print(pydash.join(sqlTobe))
    pyperclip.copy(pydash.join(sqlTobe))
    

def changeVariableTemplateDetail(match_obj):
    global mode
    if match_obj.group(1) is not None:
        # batch
        if mode == 'batch':
            return "#{" + match_obj.group(1) + "}"
        else :
        # batch 이외
            return "#{" + pydash.camel_case(match_obj.group(1)) + "}"
    
def changeVariableTemplate( vTxt):
    newTxt = re.sub(r'#(?P<varName>[\w]+)#', changeVariableTemplateDetail , vTxt)
    return newTxt



def deleteEmptyLine( vTxt):
    newTxt = re.sub(r'^[\s\t]*$\r\n', deleteEmptyLineDetail , vTxt)
    return newTxt

def deleteEmptyLineDetail(match_obj):
    if match_obj.group() is not None:
        return ""
def setCommentCj(vTxt):
    newTxt = re.sub(r'\/\*', setCommentCjDetail , vTxt)
    return newTxt

def setCommentCjDetail(match_obj):
    if match_obj.group() is not None:
        return "/*+cj"
        
def deleteCommentCj(vTxt):
    newTxt = re.sub(r'\+cj', deleteCommentCjDetail , vTxt)
    return newTxt

def deleteCommentCjDetail(match_obj):
    if match_obj.group() is not None:
        return ""
def deleteCommentAll(vTxt):
    newTxt = re.sub(r'\/\*[\s\w가-힣\(\)\.:\<\>\-\*\[\]\{\}=,%\$]+\*\/', deleteCommentAllDetail , vTxt)
    return newTxt

def deleteCommentAllDetail(match_obj):
    if match_obj.group() is not None:
        return ""    
def deleteCarageReturn(vTxt):
    newTxt = re.sub(r'\r\n', deleteCarageReturnDetail , vTxt)
    return newTxt

def deleteCarageReturnDetail(match_obj):
    if match_obj.group() is not None:
        return "\n"

def make_tobe_filepath(from_path, date_format):
    from_filename =  Path(from_path).stem
    dir_path = os.path.dirname(from_path)
    # now = datetime.datetime.now()
    # formattedDate = now.strftime("%Y%m%d_%H%M%S")
    to_filepath = ""
    if date_format is not None:
        to_filepath = os.path.join(dir_path , from_filename + '_' + date_format + '.xml')
    else:
        to_filepath = os.path.join(dir_path , from_filename + '.xml')
    return to_filepath

def make_tobe_filepath_nocomment(from_path):
    from_filename =  Path(from_path).stem
    dir_path = os.path.dirname(from_path)
    # now = datetime.datetime.now()
    # formattedDate = now.strftime("%Y%m%d_%H%M%S")
    to_filepath = ""
    to_filepath = os.path.join(dir_path , from_filename + '_noComment.xml')
    return to_filepath
 
def make_tobe_filepath_before_sqllines(from_path):
    from_filename =  Path(from_path).stem
    dir_path = os.path.dirname(from_path)
    # now = datetime.datetime.now()
    # formattedDate = now.strftime("%Y%m%d_%H%M%S")
    to_filepath = ""
    to_filepath = os.path.join(dir_path , from_filename + '_oracle.xml')
    return to_filepath
   
def get_date_format():
    now = datetime.datetime.now()
    formattedDate = now.strftime("%Y%m%d_%H%M%S")
    return formattedDate

def write_to_xml( tobe_xml_path, sqlMap , vNamespace ): 
    xmlFileTobe = []
    # 번역만 한것.
    xmlFileTobe_mapping = []
    before_sqllines = []
    xmlFileTobe.append('<?xml version="1.0" encoding="UTF-8"?>\n')
    xmlFileTobe_mapping.append('<?xml version="1.0" encoding="UTF-8"?>\n')
    vDoctype = '''<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">\n'''
    
    xmlFileTobe.append(vDoctype)
    xmlFileTobe.append('<mapper namespace="'+ vNamespace +'">\n')
    xmlFileTobe_mapping.append(vDoctype)
    xmlFileTobe_mapping.append('<mapper namespace="'+ vNamespace +'">\n')
    for sqlList in sqlMap:
        if type(sqlMap[sqlList]) == str :
            continue
        if pydash.includes(['select','insert','update','delete','procedure'], sqlList) :
            for sqlObj in pydash.concat([],sqlMap.get(sqlList)):
                sqlId = (sqlObj['@id'])
                
                
                
                # # origin 
                # sql = sqlObj['#text']
                # sqlOrigin = sqlObj['sqlOrigin'] 
                # xmlFileTobe.append("\t<" + sqlList + " id=\""+sqlId + "_asis\" parameterType=\"hashmap\" >\n")
                # xmlFileTobe.append("\t<![CDATA[\n")
                # xmlFileTobe.append("\t\t")
                # xmlFileTobe.append(sqlOrigin)
                # xmlFileTobe.append("\n\t]]>") 
                # xmlFileTobe.append("\n\t</" + sqlList + ">\n")
                # # end origin
                
                
                parse = sqlObj['parse']     
                before_sqllines = []   
                convert_sql_recursive( before_sqllines, parse[0] )
                
                resultType = ""
                if sqlList == 'select' :
                    resultType = "resultType=\"hashmap\""
                    
                ## before sqllines
                xmlFileTobe_mapping.append("\t<" + sqlList + " id=\""+sqlId + "\" parameterType=\"hashmap\"" + resultType + " >\n")
                xmlFileTobe_mapping.append("\t<![CDATA[\n")
                xmlFileTobe_mapping.append("\t\t")
                xmlFileTobe_mapping = pydash.concat(xmlFileTobe_mapping , before_sqllines )
                xmlFileTobe_mapping.append("\n\t]]>") 
                xmlFileTobe_mapping.append("\n\t</" + sqlList + ">\n")
                ## End before sqllines
                
                # # sqlLine online
                # # online
                # data = {'source': pydash.join(before_sqllines), 'source_type': 'Oracle', 'target_type': 'MySQL'} 
                # headers = {'Content-Type': 'application/x-www-form-urlencoded; chearset=UTF-8'}
                # res = requests.post('https://www.sqlines.com/sqlines_run.php', data=json.dumps(data), headers=headers)
                # print(res.text)
                #
                # xmlFileTobe.append("\t<" + sqlList + " id=\""+sqlId + "\" parameterType=\"hashmap\" >\n")
                # xmlFileTobe.append("\t<![CDATA[\n")
                # xmlFileTobe.append("\t\t")
                # parse = sqlObj['parse']     
                # xmlFileTobe.append("\n\t]]>") 
                # xmlFileTobe.append("res.text") 
                # xmlFileTobe.append("\n\t</" + sqlList + ">\n")
                # # End sqlLine
                
                # sqlLine Offline
                tempFileName = 'tempSqlConvert.sql'
                tempFileNameOut = 'tempSqlConvert_out.sql'
                f1 = open( tempFileName , 'w',  encoding='UTF8') 
                f1.write(pydash.join(before_sqllines))
                f1.close()
                f2 = open( tempFileNameOut , 'w',  encoding='UTF8') 
                f2.close()
                # text = subprocess.check_output('dir', shell = True)
                # sql_command = "sqlines -s=oracle -t=mysql -in="+ tempFileName + " -out="+ tempFileNameOut 
                # os.system(sql_command)
                # sql_command = ["sqlines", "-s=oracle", "-t=mysql", "-in="+ tempFileName , "-out="+ tempFileNameOut]
                # sql_command = [r"C:\tkeyTool\tools\sqlines-3.1.771\sqlines-3.1.771\sqlines", "-s=oracle", "-t=mysql", "-in="+ os.path.join(os.getcwd(),tempFileName) , "-out="+ os.path.join(os.getcwd(),tempFileNameOut)]
                sql_command = [r"C:\tkeyTool\tools\sqlines-3.1.771\sqlines-3.1.771\sqlines", "-s=oracle", "-t=mysql", "-in="+ tempFileName , "-out="+ tempFileNameOut]
                # cmd_respond = subprocess.check_output(sql_command , shell=True)
                sqlAfterSqllines = ""
                try:
                    CREATE_NO_WINDOW = 0x08000000
                    subprocess.call(sql_command , shell=True , creationflags=CREATE_NO_WINDOW)
                    # cmd_respond = subprocess.check_output(sql_command , shell=True)
                    # ft = open(tempFileNameOut ,'r',encoding='UTF8')
                    ft = codecs.open(tempFileNameOut, 'r', encoding='utf-8',errors='ignore')
                    sqlAfterSqllines = ft.read()
                    ft.close()
                except Exception as e:
                    print('Error subprocess.call')
                    print(str(e))
                    pass
                # process = subprocess.Popen(sql_command, shell=True , stdout=subprocess.PIPE , stderr=subprocess.PIPE )
                
                # with open(tempFileNameOut ,'r',encoding='UTF8') as f:
                #     sqlAfterSqllines = f.read()
                
                sqlAfterSqllines = deleteEmptyLine(sqlAfterSqllines)
                sqlAfterSqllines = deleteCommentCj(sqlAfterSqllines)
                sqlAfterSqllines = deleteCarageReturn(sqlAfterSqllines)
                
                xmlFileTobe.append("\t<" + sqlList + " id=\""+sqlId + "\" parameterType=\"hashmap\" " + resultType + ">\n")
                xmlFileTobe.append("\t<![CDATA[\n")
                xmlFileTobe.append("\t\t" + sqlAfterSqllines)
                xmlFileTobe.append("\n\t]]>") 
                xmlFileTobe.append("\n\t</" + sqlList + ">\n")
                
                
                
                # os.remove(tempFileName, dir_fd=None)
                # os.remove(tempFileNameOut, dir_fd=None)
                
                
    xmlFileTobe.append("</mapper>\n")
    xmlFileTobe_mapping.append("</mapper>\n")
    
    # write file sqllines
    f = open( tobe_xml_path , 'w',  encoding='utf8')
    for vStr in xmlFileTobe:
        f.write(vStr )
    f.close()
    
    # write file only mapping before sqllines
    tobe_xml_path_only_mapping = make_tobe_filepath_before_sqllines(tobe_xml_path)
    f = open( tobe_xml_path_only_mapping , 'w',  encoding='utf8')
    for vStr in xmlFileTobe_mapping:
        f.write(vStr)
    f.close()
    
    # write file no comment
    f_nocomment = codecs.open(tobe_xml_path, 'r', encoding='utf-8',errors='ignore')
    str_nocomment = f_nocomment.read()
    f_nocomment.close()
    str_nocomment = deleteCommentAll(str_nocomment)
    str_nocomment = deleteCarageReturn(str_nocomment)
    tobe_xml_path_nocomment = make_tobe_filepath_nocomment(tobe_xml_path)
    f = open( tobe_xml_path_nocomment , 'w',  encoding='utf8')
    f.write(str_nocomment)
    f.close()
  

  
def reportForColumnChangeByFile(sqlMap , vNamespace , tableName , columnName):
    # ddddd
    reportInfos = []
    for sqlList in sqlMap:
        if type(sqlMap[sqlList]) == str :
            continue
        if pydash.includes(['select','insert','update','delete','procedure'], sqlList) :
            for sqlObj in pydash.concat([],sqlMap.get(sqlList)):
                sqlId = (sqlObj['@id'])
                parse = sqlObj['parse']     
                findInfos = []   
                find_asis_column(findInfos , tableName , columnName , parse[0]  )
                if ( len(findInfos) > 0 ) :
                    reportInfos.append({
                        'namespace' : vNamespace ,
                        'sqlId' : sqlId ,
                        'report_infos' : findInfos
                    })
                    # reportInfos = pydash.concat(reportInfos,findInfos)
    return reportInfos
    
def convert_sql_recursive( xmlFileTobe , _token ) :
    if hasattr(_token, 'tokens') :
        for token in _token.tokens:                        
            convert_sql_recursive( xmlFileTobe , token)
    
    else :
        if ( _token.mapping_info is not None ) :
            m = _token.mapping_info
            if (_token.mappingType == 'column') :
                if m['columnName'] != m['asisColumnName'] :
                    xmlFileTobe.append( m['columnName'] + '\t/*+cj ' + m['columnNameKor'] + ' changeFrom ' +  m['asisColumnName'] + ' */\t')
                else:
                    xmlFileTobe.append( m['columnName'] + '\t/*+cj ' + m['columnNameKor'] + ' */\t')
            elif (_token.mappingType == 'table') :
                if m['tableName'] != m['asisTableName'] :
                    xmlFileTobe.append( m['tableName'] + '\t/*+cj ' + m['tableNameKor'] + ' changeFrom ' +  m['asisTableName'] +' */\t')
                else:
                    xmlFileTobe.append( m['tableName'] + '\t/*+cj ' + m['tableNameKor'] + ' */\t')
        else :
            if _token.ttype[0] == 'Comment':
                xmlFileTobe.append(setCommentCj(_token.value))
            else :
                xmlFileTobe.append(_token.value)
        

def find_asis_column( findInfos  ,  tableName , columnName, _token ) :
    if hasattr(_token, 'tokens') :
        for token in _token.tokens:                        
            find_asis_column( findInfos , tableName , columnName, token)
    
    else :
        if ( _token.mapping_info is not None ) :
            m = _token.mapping_info
            if (_token.mappingType == 'column') :
                if ( m['asisTableName'] == tableName.upper() and m['asisColumnName'] == columnName.upper()   ) :
                    sql = ''
                    if hasattr(_token , 'parent') :
                        sql = _token.parent.value
                    findInfos.append( {'mapping_info': _token.mapping_info , 'sql': sql } )
       

def processColumnToken(_token , sqlId , sqltype):
    # 일단 본업무를 처리하고
    
    if ( type(_token) == sqlparse.sql.Token 
         and type(_token.ttype) == sqlparse.tokens._TokenType 
         and _token.ttype == sqlparse.tokens.Name
         and not pydash.includes(g_keyword, _token.value)
        # and sqlparse.tokens.Keyword.DML
    ):
        is_ibatis_var = False        
        token_index_1  = _token.parent.token_index(_token)
        if token_index_1 > 0 :
            v_pre = _token.parent.token_prev(token_index_1)
            if(v_pre is not None ) :
                if( v_pre[1].ttype == sqlparse.tokens.Error ) :
                    is_ibatis_var = True 
        if is_ibatis_var == False and hasattr(_token, 'value') and type(_token.value) == str and _token.value.startswith('#') :
            is_ibatis_var = True
         
           
        if is_ibatis_var == False :
            is_alias = False
            if isinstance(_token.parent, sqlparse.sql.Identifier) and isinstance(_token.parent.parent, sqlparse.sql.Identifier) :
                # if ( _token.parent.parent.get_real_name() != _token.parent.parent.get_alias() 
                #     and _token.parent.get_alias() is None 
                #     and _token.parent.get_name() == _token.parent.parent.get_alias() 
                #     ):
                #     is_alias = True
                if ( _token.parent.get_name() == _token.parent.parent.get_alias()) :
                    is_alias = True
            if is_alias == False :
                # 전체 statement에서 가져오면 범위가 너무 크다.
                # v_statement = get_parent_statement(_token)
                # v_table_tokens = extract_table_identifiers(v_statement)
                
                # 해당 쿼러기 있는 문장에서만 token들을 가져온다.
                v_statement_tokens = get_parent_tokens(_token)
                v_table_tokens = extract_table_identifiers(v_statement_tokens , sqlId , _token , sqltype)
                
                # v_table_token = get_table_name(_token)        
                # v_table_name = v_table_token.get_name()
                for table_token in v_table_tokens:
                     # get_name 은 alias 임
                    v_table_name = table_token.get_real_name()
                    v_table_alias = table_token.get_name()
                    v_column_name = _token.value
                    v_find_map = None
                    v_find_table = None
                    parent_token = _token.parent                
                    if (isinstance(parent_token , sqlparse.sql.Identifier ) 
                        and len(parent_token.tokens) == 3 
                        and parent_token.tokens[1].value == '.'  
                    ): 
                        v_col_tab_alias = parent_token.tokens[0].value
                        if v_col_tab_alias.strip().upper() ==  v_table_alias.strip().upper() :
                            # v_find_map = pydash.find(mappingJson, {'asisTableName' : v_table_name.strip().upper() , 'asisColumnName': v_column_name.strip().upper() })
                            v_find_table = mappingJson1.get(v_table_name.strip().upper())
                            if ( v_find_table is not None) :
                                v_find_map = pydash.find(v_find_table, { 'asisColumnName': v_column_name.strip().upper() })
                        
                    else :
                        # v_find_map = pydash.find(mappingJson, {'asisTableName' : v_table_name.strip().upper() , 'asisColumnName': v_column_name.strip().upper() })
                        v_find_table = mappingJson1.get(v_table_name.strip().upper())
                        if ( v_find_table is not None) :
                            v_find_map = pydash.find(v_find_table, { 'asisColumnName': v_column_name.strip().upper() })
                            
                    
                    if v_find_map is not None:
                        _token.mapping_info = v_find_map
                        _token.mappingType = 'column'
                        # if v_find_map['asisColumnName'] != v_column_name.strip().upper() :
                        #     _token.mapping_info = v_find_map
                        #     _token.mapping_info['mappingType'] = 'column'
                        
                        # if v_find_table is not None :
                        set_table_mapping(table_token, v_find_table[0])
                
    # 다시 돌린다.
    if hasattr(_token, 'tokens') :
        for token in _token.tokens:
            if token.is_whitespace :
                continue
            if isinstance(token, sqlparse.sql.Comment):
                # token.value = setCommentCj(token.value)
                continue
            
            # # '#{xxx}' 로 감싸인 것을 처리하기 위함 mybatis
            # token_index = token.parent.token_index(token)
            # if token_index > 0 :
            #     v_pre = token.parent.token_prev(token_index)
            #     if(v_pre is not None ) :
            #         if( v_pre[1].ttype == sqlparse.tokens.Error ) :
            #             continue 
            
            # # '#' 로 시작하는 것을 처리하기 위함 ibatiss
            # if hasattr(token, 'value') and type(token.value) == str and token.value.startswith('#') :
            #     continue
            if is_pre_error(token) :
                continue
            
            processColumnToken(token, sqlId , sqltype)

# '#{xxx}' 로 감싸인 것을 처리하기 위함 mybatis
def is_pre_error(token):
    token_index = token.parent.token_index(token)
    if token_index > 0 :
        v_pre = token.parent.token_prev(token_index)
        if(v_pre is not None) :
            if(  hasattr(v_pre[1], 'ttype') and v_pre[1].ttype == sqlparse.tokens.Error ) :
                return True 
    # '#' 로 시작하는 것을 처리하기 위함 ibatiss       
    if hasattr(token, 'value') and type(token.value) == str and token.value.startswith('#') :
        return True
   
def set_table_mapping(_table_token , _find_table_map):
    # table_value = _table_token._get_repr_value()
    if( type(_table_token) == sqlparse.sql.Token 
        and type(_table_token.ttype) == sqlparse.tokens._TokenType 
        and _table_token.ttype == sqlparse.tokens.Name
        and (not pydash.includes(g_keyword, _table_token.value))
        and _table_token.mapping_info is None
    ):        
        table_value = _table_token.value
        table_value_map = _find_table_map['asisTableName']
        if table_value_map.strip().upper() == table_value.strip().upper() :
            _table_token.mapping_info = _find_table_map
            _table_token.mappingType = 'table'
            
            
    
    if hasattr(_table_token, 'tokens'):        
        for token in _table_token.tokens:
            if token.is_whitespace :
                continue
            if isinstance(token, sqlparse.sql.Comment):
                continue
            
            set_table_mapping(token , _find_table_map)
        
def get_parent_statement(_token):
    if ( type(_token.parent) == sqlparse.sql.Statement ):
        return _token.parent
    else :
        return get_parent_statement(_token.parent)
 
def get_parent_tokens(_token):
    # 상위 dml 이 있는 token을 찾는다.
    # 나의 인덱스를 찾늗다.
    # union all 이 있는 index를 찾는다. 해당 인덱스 까지만 리턴한다.
    
    statement_token = get_parent_token_have_dml(_token)
    v_unions = get_unionall(statement_token)
    indexof_token = get_indexof_token(_token , statement_token)
    
    if len(v_unions) == 0:
        return statement_token.tokens
    elif len(v_unions) == 1:
        v_union = v_unions[0]
        indexof_union = get_indexof_token(v_union , statement_token)
        if indexof_union > indexof_token :            
            return statement_token.tokens[0 : indexof_union  ]
        else :
            return statement_token.tokens[indexof_union :]
    else:
        # union 이 여러개 있는 경우 . 드문경우지만.
        indexof_unions = [0]
        # union 의 인덱스를 구한다.
        for union in v_unions:
            v_index = get_indexof_token(union,statement_token)
            indexof_unions.append(v_index)
        indexof_unions.append(len(statement_token.tokens) - 1)  
         
        for idx, val in enumerate(indexof_unions):
            min_idx = min ( len(indexof_unions) -1 , idx + 1  )
            if indexof_token >= val and indexof_token <= indexof_unions[min_idx] :
                return statement_token.tokens[val : indexof_unions[min_idx] +1 ]
            
def get_indexof_token(_token , statement_token ):
    if _token.is_child_of(statement_token) :
        return statement_token.token_index(_token)
    else :
        return get_indexof_token( _token.parent, statement_token)
    
def get_parent_token_have_dml(_token):
    if _token.parent is None and type(_token) == sqlparse.sql.Statement :
        return _token
    elif  _token.parent is None : 
        return None
    
    parent_dml_token = pydash.find(_token.parent.tokens, lambda x: x.ttype == sqlparse.tokens.DML )
    if parent_dml_token is not None : 
        return parent_dml_token.parent
    else :
        return get_parent_token_have_dml(_token.parent)

def get_unionall(_token):
    v_unions = []
    if hasattr(_token, 'tokens'):        
        v_unions = pydash.filter_(_token.tokens, 
            lambda x: 
                ( x.ttype == sqlparse.tokens.Keyword and re.search(r'\bunion\b', x.value, re.IGNORECASE))
                or ( x.ttype ==  sqlparse.tokens.Keyword.DML )
        )
    return v_unions
      
def extract_table_identifiers(token_stream , sqlId , _token , sqltype ):
    v_rtn = []
    token_stream_reduced = None
    if ( sqltype == 'update'):
        indexof_set = pydash.find_index(token_stream , lambda x : x.ttype == sqlparse.tokens.Keyword and re.search(r'\bset\b', x.value, re.IGNORECASE))
        if indexof_set > -1 :
            token_stream_reduced = token_stream[:indexof_set] 
            # 검색조건 고려 : 테이블을 찾을 때 
            indexof_where = pydash.find_index(token_stream_reduced , lambda x : x.ttype == sqlparse.tokens.Keyword and re.search(r'\bwhere\b', x.value, re.IGNORECASE))
            if indexof_where > -1 :
                token_stream_reduced = token_stream_reduced[:indexof_where] 
    elif ( pydash.includes(['select','delete'],sqltype)):
        indexof_from = pydash.find_index(token_stream , lambda x : x.ttype == sqlparse.tokens.Keyword and re.search(r'\bfrom\b', x.value, re.IGNORECASE))
        if indexof_from > -1 :
            token_stream_reduced = token_stream[indexof_from : ] 
            # 검색조건 고려 : 테이블을 찾을 때 
            indexof_where = pydash.find_index(token_stream_reduced , lambda x : x.ttype == sqlparse.tokens.Keyword and re.search(r'\bwhere\b', x.value, re.IGNORECASE))
            if indexof_where > -1 :
                token_stream_reduced = token_stream_reduced[:indexof_where]
    
    elif ( sqltype == 'insert'):
        indexof_values = pydash.find_index(token_stream , lambda x : x.ttype == sqlparse.tokens.Keyword and re.search(r'\bvalues\b', x.value, re.IGNORECASE))
        if indexof_values > -1 :
            token_stream_reduced = token_stream[ : indexof_values ]        
            
    if token_stream_reduced is None :
        token_stream_reduced = token_stream   
        
    v_identifier_tokens = pydash.filter_(token_stream_reduced, 
        lambda x,i : 
            # token_index = x.parent.token_index(x)
            # v_pre = x.parent.token_prev(token_index)            
            (isinstance(x, sqlparse.sql.Identifier) 
             or isinstance(x, sqlparse.sql.Function)
             or isinstance(x, sqlparse.sql.IdentifierList )
            )
            
        )
    v_identifier_tokens_1 = get_identifier_from_identifierList(v_identifier_tokens)
    # if ( sqlId == 'saveBLineMgmt') :
    #     print('==========================================================\n')
    
    for item in v_identifier_tokens_1:

        # if ( sqlId == 'saveBLineMgmt') :
        #     print(sqlId + ', ' + item.get_real_name() + ' , token_value : ' + _token.value )
               
        # get_name 은 alias 임
        v_find_str = item.get_real_name()
        if v_find_str is None :
            continue
        # v_find_map = pydash.find(mappingJson, {'asisTableName' : v_find_str.strip().upper()  })
        v_find_table = mappingJson1.get(v_find_str.strip().upper())
        v_find_map = None
        if ( v_find_table is not None) :
            v_find_map = v_find_table[0]
            
        if v_find_map is not None : 
            # yield item.get_name()
            v_rtn.append(item)
            # put_mapping_tableinfo(item , item , v_find_map)               
       
    return v_rtn

def get_identifier_from_identifierList(_tokenList):
    v_rtn = []
    for token in _tokenList :
        if isinstance(token, sqlparse.sql.IdentifierList ) : 
            v_list = pydash.filter_(token.tokens , lambda x : isinstance(x, sqlparse.sql.Identifier))
            v_rtn = pydash.concat(v_rtn , v_list)
        else: 
            v_rtn.append(token)
    return v_rtn 

def put_mapping_tableinfo( token , token_0, find_map):
    v_table_name = token.get_real_name()
    
    

def prototype():
    asisSqlPath=r'C:\dev\workspace\tdcs-batch\tdcs-batch\asis\SALSUI08300.xsql'
    excel_file_path = 'mapping1.xlsx'
    sheet_name = 'sheet1'
    make_file_path = 'mapping1.json'
    
    # asisSqlPath = 'BASCDM08100.xsql'
    # asisSqlPath = 'SALSUI08300.xsql'
    asisSqlPath=r'C:\dev\workspace\tdcs-batch\tdcs-batch\asis\ACCSSS08100.xsql'
    # asisSqlPath=r'C:\dev\workspace\tdcs-batch\tdcs-batch\asis\SALSUI08300.xsql'
    
    # ex2json.make_mapping_json_file(excel_file_path, sheet_name,make_file_path)
    mappingJson = ex2json.get_mapping_json(excel_file_path, sheet_name)
    asisSqlJson = xml2json.get_xml_to_json(asisSqlPath)
    
    sqlMap = asisSqlJson['sqlMap']
    
    insertList = sqlMap.get("insert")
    selectList = sqlMap.get("select")
    updateList = sqlMap.get("update")
    deleteList = sqlMap.get('delete')
    
    if insertList is not None:
        for sqlObj in insertList:
            sqlId = (sqlObj['@id'])
            sql = sqlObj['#text']
            parse = sqlparse.parse(sql)
            t01 = parse[0].tokens[0]
            cur_keyword = ''
            cur_tableName = ''
            for vToken in parse[0].tokens : 
                if vToken.is_whitespace :
                    continue
                if vToken._get_repr_name() == 'Comment':
                    continue
                # table check
                if vToken.is_keyword == False and  vToken._get_repr_name() == 'Function' and vToken.is_group == True: 
                    cur_tableName = vToken.get_name()
                    cur_keyword = vToken._get_repr_value()
                    subParenthesToken = getSubParenthesis(vToken)
                    columns = get_columns(subParenthesToken)
                    
                    print(columns)
                    
                if vToken._get_repr_name() == 'Values' and vToken.tokens is not None:
                    # get sub
                    subToken = getSubParenthesis(vToken)
                    
            
            print(sqlId)
    if selectList is not None:    
        for sqlObj in selectList:
            sqlId = (sqlObj['@id'])
            sql = sqlObj['#text']
            parse = sqlparse.parse(sql)
            
            print(sqlId)    
            
    if updateList is not None:    
        for sqlObj in updateList:
            sqlId = (sqlObj['@id'])
            sql = sqlObj['#text']
            parse = sqlparse.parse(sql)
            
            print(sqlId)    
            
    if deleteList is not None:    
        for sqlObj in deleteList:
            sqlId = (sqlObj['@id'])
            sql = sqlObj['#text']
            parse = sqlparse.parse(sql)
            
            print(sqlId) 
        
if __name__ == '__main__':
    make_mappingJson()
    main() 
    # sql= ''
    # convertByInput(sql)                
