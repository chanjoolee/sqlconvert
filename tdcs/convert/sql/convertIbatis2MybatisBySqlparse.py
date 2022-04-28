import pydash
import os
from fnmatch import fnmatch
import pandas
import json
import re
import sqlparse
from tdcs.convert.sql.lib import excel_pandas as ex2json
from tdcs.convert.sql.lib import xml_to_json as xml2json
from pathlib import Path
import datetime
from pandas.io.common import file_path_to_url
import pyperclip


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
    json_file_path = 'mapping_0422.json' 
    read_columnMapping_file(json_file_path)
    mappingJson1 = pydash.group_by(mappingJson, ['asisTableName'])

def main():
    make_mappingJson()

    # asisSqlPath=r'C:\dev\workspace\tdcs-batch\tdcs-batch\asis\SALSUI08300_001.xsql'
    asisSqlPath=r'C:\dev\workspace\tdcs-convert\tdcs\convert\sql\convert_files\TkpSwingWireRsalMapper.xml'
    date_format = get_date_format()
    # #### by file 
    # asisSqlPath = r'C:\dev\workapace_sql\tdcs-batch\sqlconvert\batch\java\com\sktps\batch\rmt\acc\db\RMTACC00200_TEMP.xsql'
    # convertByFile(asisSqlPath , None, date_format )
    
    
    ### by Folder
    # path_from = r'C:\dev\workapace_sql\tdcs-batch\sqlconvert\batch\java\com\sktps\batch\rmt\acc\db'
    # path_from = r'C:\dev\workapace_sql\tdcs-batch\sqlconvert\batch'
    path_from = r'C:\dev\workapace_sql\tdcs-batch\sqlconvert\dis'
    # path_from = r'C:\dev\workapace_sql\tdcs-batch\sqlconvert\acc'
    print("Start By Foler")
    print("Folder : " + path_from)
    print("DateFormat" + date_format)
    convertByFolder(path_from, date_format)

def convertByFolder(path_from , date_format):
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
    
    
    for idx,path_info in enumerate(file_list):
        print('file process' + str(idx+1) + '/' +   str(len(file_list)))
        print("<<<< " + path_info['full_path'] + ">>>>>")
        file_path = path_info['file_path']
        sub_path = file_path[len(path_from):]
        file_name = path_info['file_name']
        path_to = path_from +  '_' +  date_format + sub_path 
        make_dir_recursive(path_to)
        convertByFile(path_info['full_path'], os.path.join(path_to, file_name) , None )
         
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
        
def convertByFile(asisSqlPath , tobePath , date_format ):
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
                    if sqlList == 'procedure' : 
                        continue
                    if sqlId.startswith("call_") : 
                        continue
                    
                    for vToken in parse[0].tokens : 
                        if vToken.is_whitespace :
                            continue
                        if vToken._get_repr_name() == 'Comment':
                            continue
                        # table check
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
        write_to_xml( tobe_xml_path , sqlMap , vNamespace )           
        print("\t\tComplete")
    
    except Exception as e:
        print('Error')
        print(str(e))
        pass

def convertByInput(sql):
    # sql = '''
    #     SELECT  DEAL_CO_CD,  STL_PLC,   DIS_HLD_PLC, DEAL_CO_CL1, DEAL_CO_CL2, SALE_STOP_YN,  PAY_STOP_YN,  NEW_ORG_ID 
    #                        INTO  rc_SalePLC,  rc_StlPLC, rc_DisPLC,   rc_DealCl1,  rc_DealCl2,  rc_SaleStopYN, rc_PayStopYN, wk_NewOrg 
    #                        FROM  TBAS_DEAL_CO_MGMT 
    #                       WHERE  ukey_agency_cd   = iv_AgencyCd 
    #                         AND  ukey_sub_cd      = iv_SubCd 
    #                         AND  ukey_channel_cd IS NULL 
    #                         AND  deal_co_cl1     in ('A2', 'A3', 'AC', 'B1', 'B2', 'C1', 'A6') 
    #                         AND  deal_sta_dt     <=  rc_ProcDt 
    #                         AND  deal_end_dt     >=  rc_ProcDt 
    #                         AND  eff_sta_dtm     <=  iv_ProcDtm 
    #                         AND  eff_end_dtm     >=  iv_ProcDtm 
    #                         AND  del_yn           = 'N'; 
    # '''
    sqlTobe = []
    parse = sqlparse.parse(sql)
    for vToken in parse[0].tokens : 
        if vToken.is_whitespace :
            continue
        if vToken._get_repr_name() == 'Comment':
            continue
        # table check
        processColumnToken(vToken , "xxx" , "xxx")
        
    convert_sql_recursive( sqlTobe , parse[0] ) 
    print(pydash.join(sqlTobe))
    pyperclip.copy(pydash.join(sqlTobe))
    

def changeVariableTemplateDetail(match_obj):
    if match_obj.group(1) is not None:
        return "#{" + match_obj.group(1) + "}"
    
def changeVariableTemplate( vTxt):
    newTxt = re.sub(r'#(?P<varName>[\w]+)#', changeVariableTemplateDetail , vTxt)
    return newTxt
    # print(vTxt)

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
    
def get_date_format():
    now = datetime.datetime.now()
    formattedDate = now.strftime("%Y%m%d_%H%M%S")
    return formattedDate

def write_to_xml( tobe_xml_path, sqlMap , vNamespace ): 
    xmlFileTobe = []
    xmlFileTobe.append('<?xml version="1.0" encoding="UTF-8"?>\n')
    vDoctype = '''<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">\n'''
    
    xmlFileTobe.append(vDoctype)
    xmlFileTobe.append('<mapper namespace="'+ vNamespace +'">\n')
    for sqlList in sqlMap:
        if type(sqlMap[sqlList]) == str :
            continue
        if pydash.includes(['select','insert','update','delete','procedure'], sqlList) :
            for sqlObj in pydash.concat([],sqlMap.get(sqlList)):
                sqlId = (sqlObj['@id'])
                # print(sqlId)
                xmlFileTobe.append("\t<" + sqlList + " id=\""+sqlId + "\" parameterType=\"hashmap\" >\n")
                xmlFileTobe.append("\t<![CDATA[\n")
                xmlFileTobe.append("\t\t")
                # sql = sqlObj['#text']
                # parse = sqlparse.parse(sql)
                parse = sqlObj['parse']                    
                convert_sql_recursive( xmlFileTobe, parse[0] )  
                xmlFileTobe.append("\n\t]]>") 
                xmlFileTobe.append("\n\t</" + sqlList + ">\n")
    xmlFileTobe.append("</mapper>\n")
    
    # write file 
    f = open( tobe_xml_path , 'w',  encoding='utf8')
    for vStr in xmlFileTobe:
        f.write(vStr )
    f.close()


def convert_sql_recursive( xmlFileTobe , _token ) :
    if hasattr(_token, 'tokens') :
        for token in _token.tokens:                        
            convert_sql_recursive( xmlFileTobe , token)
    
    else :
        if ( _token.mapping_info is not None ) :
            m = _token.mapping_info
            xmlFileTobe.append( m['columnName'] + '\t/* ' + m['columnNameKor'] + ' */\t')
        else :
            xmlFileTobe.append(_token.value)
        

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
                    _token.mapping_info['mappingType'] = 'column'
                    # if v_find_map['columnName'] != v_column_name.strip().upper() :
                    #     _token.mapping_info = v_find_map
    
    # 다시 돌린다.
    if hasattr(_token, 'tokens') :
        for token in _token.tokens:
            if token.is_whitespace :
                continue
            if isinstance(token, sqlparse.sql.Comment):
                continue
            
            # '#{xxx}' 로 감싸인 것을 처리하기 위함 mybatis
            token_index = token.parent.token_index(token)
            if token_index > 0 :
                v_pre = token.parent.token_prev(token_index)
                if(v_pre is not None ) :
                    if( v_pre[1].ttype == sqlparse.tokens.Error ) :
                        continue 
            # '#' 로 시작하는 것을 처리하기 위함 ibatiss
            if hasattr(token, 'value') and type(token.value) == str and token.value.startswith('#') :
                continue
                
            
            processColumnToken(token, sqlId , sqltype)
        
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
    # convertByInput()                
