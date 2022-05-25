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




def main():
    
    path_from = r'C:\dev\workspace\tdcs-batch\src\main\java\com\skt\tdcs\batch\bas\bi\mapper'
    
    print("Start PackageComment")
    print("Folder : " + path_from)
    convertByFolder(path_from)
   

def convertByFolder(path_from):
    file_list = []
    file_pattern = "*.xml"
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
        path_to = path_from +  '_' +  'xxx' + sub_path 
        convertByFile(path_info['full_path'], path_info['full_path']  )
        # convertByFile( path_info['full_path'] , path_info['full_path'] , None )
         
    print("\n")      
    print("Convert convertByFolder Complete!")

def convertByFile(asisSqlPath , tobePath ):
    try: 
        asisSqlJson = make_asisSqlToJson(asisSqlPath)
        
        
        sqlMap = asisSqlJson.get('mapper')
        
        for sqlList in sqlMap:
            if type(sqlMap[sqlList]) == str :
                continue
            if pydash.includes(['select','insert','update','delete','procedure'], sqlList) :
                for sqlObj in pydash.concat([],sqlMap.get(sqlList)):
                    
                    sqlId = (sqlObj['@id'])
                    print('\t\t' + sqlId) 
                    
                    sql = sqlObj['#text']
                    
        
        tobe_xml_path = ""
        tobe_xml_path = make_tobe_filepath(tobePath)
        # vNamespace = 'com.skt.tdcs.batch.xxx'        
        vNamespace = sqlMap.get("@namespace")
        
        # print("\t\t<<<<<   write_to_xml >>>>>>\n")
        write_to_xml( tobe_xml_path , sqlMap , vNamespace )           
        print("\t\tComplete")
    
    except Exception as e:
        print('Error')
        print(str(e))
        pass
    
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
                parameterType = sqlObj.get('@parameterType')
                parameterTypeStr = ""
                if parameterType is not None:
                    parameterTypeStr = "parameterType=\"" + sqlObj['@parameterType'] + "\""
                    
                resultType = sqlObj.get('@resultType')
                resultTypeStr = ""
                if resultType is not None:
                    resultTypeStr = "resultType=\"" + sqlObj['@resultType'] + "\""
                # origin 
                sql = sqlObj['#text']
                
                xmlFileTobe.append("\t<" + sqlList + " id=\""+sqlId + "\" " + parameterTypeStr + "  " + resultTypeStr +" >\n")
                if not re.search(r'업무로직\s:', sql , re.IGNORECASE) :
                    xmlFileTobe.append("/*\n")
                    xmlFileTobe.append(vNamespace + "." + sqlId + "(P179230)\n")
                    xmlFileTobe.append("업무로직 : \n")
                    xmlFileTobe.append("*/\n")
                xmlFileTobe.append("\t<![CDATA[\n")
                xmlFileTobe.append("\t\t")
                xmlFileTobe.append(sql)
                xmlFileTobe.append("\n\t]]>") 
                xmlFileTobe.append("\n\t</" + sqlList + ">\n")
                # end origin
                
                
    xmlFileTobe.append("</mapper>\n")
    xmlFileTobe_mapping.append("</mapper>\n")
    
    # write file sqllines
    f = open( tobe_xml_path , 'w',  encoding='utf8')
    for vStr in xmlFileTobe:
        f.write(vStr )
    f.close()
    
   
def make_asisSqlToJson( _asisSqlPath ):
    _asisSqlJson = xml2json.get_xml_to_json(_asisSqlPath)
    return _asisSqlJson

def make_tobe_filepath(from_path):
    from_filename =  Path(from_path).stem
    dir_path = os.path.dirname(from_path)
    # now = datetime.datetime.now()
    # formattedDate = now.strftime("%Y%m%d_%H%M%S")
    to_filepath = ""
    # to_filepath = os.path.join(dir_path , from_filename + '_xxx.xml')
    to_filepath = os.path.join(dir_path , from_filename + '.xml')
    return to_filepath       
if __name__ == '__main__':
    main() 
    # sql= ''
    # convertByInput(sql)                
