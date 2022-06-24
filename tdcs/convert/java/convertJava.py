import pydash
import os
import subprocess
from fnmatch import fnmatch
import pandas
import json
import re
from tdcs.convert.sql.lib import excel_pandas as ex2json
from tdcs.convert.sql.lib import xml_to_json as xml2json
from fileinput import filename
import codecs


# asis java file list
java_path_asis = r'C:\dev\workspace\tdcs-batch-sql\javaconvert\com'
java_file_list = []
java_file_list1 = {} # 인덱스

root_tobe_java_path = r"C:\dev\workspace\tdcs-batch-sql\javaconvert\convert"
root_tobe_java_package = "com.skt.tdcs.batch"
# 엑셀에서 작업할 파일을 정의한다.v
excel_file_path = r'C:\dev\workspace\tdcs-batch-sql\javaconvert\java_mapping.xlsx'
sheet_name = '2022.06.23'
ex = {
    'asis_file_nm' : '',
    'tobe_file_nm' : '',
    'tobe_package' : ''
}    
mappingJson = []
mappingJson1 = {}

# patterns
pt_import = re.compile(r"import\s", re.IGNORECASE)
pt_package = re.compile(r"package\s", re.IGNORECASE)
pt_author = re.compile(r"^\s\*\s@author\b", re.IGNORECASE)
pt_execute = re.compile(r"public\s+int\s+execute", re.IGNORECASE)
# sqlMap선언부
pt_decl_sqlMap = re.compile(r"^\s+SqlMapClient\s+(?P<sqlMapName>[\w]+)" , re.IGNORECASE)
# sqlMap 사용분
pt_sqlMap = re.compile(r"^(?P<space>\s+)sqlMap(?P<sqlMapEx>[\w]+)?\.(?P<action>[\w]+)", re.IGNORECASE)

# sqlMapper 수정==> sqlSession
pt_sqlmapper = re.compile(r"(?P<type>\([\w]+\)\s?)?sqlMap(?P<sqlMapEx>[\w]+)?\.[\w]+\(\"(?P<namespace>[\w]+)\.(?P<sqlId>[\w]+)\"\s?,?\s?(?P<parameter>[\w\"]+)?\)", re.IGNORECASE )


# 엑셀에서 작업할 파일을 정의한다.v
def make_mappingJson():
    global mappingJson
    global mappingJson1
    global excel_file_path
    global sheet_name
    
    mappingJson = ex2json.get_mapping_json(excel_file_path, sheet_name)
    mappingJson1 = pydash.group_by(mappingJson, ['asis_file_nm'])
    
def scan_asis_java():
    global java_file_list 
    global java_file_list1 
    
    file_pattern = "*.java"
    for path, subdirs, files in os.walk(java_path_asis):
        for name in files:
            if fnmatch(name, file_pattern):
                java_file_list.append({
                    "full_path": os.path.join(path,name)
                    ,"file_path": path
                    , "file_name" : name
                })
                
    java_file_list1 = pydash.group_by(java_file_list, ['file_name'])
    
def process_list():
    for file_info in mappingJson:
        convert_file(file_info)
    

def convert_file(mapping_info):
    pt_asis_class = re.compile(r"public\s+class")
    asis_java_info = java_file_list1.get(mapping_info["asis_file_nm"].strip() + ".java")
    if asis_java_info is None :
        print("Not Found " + mapping_info["asis_file_nm"].strip() + ".java")
        return
    else:
        asis_java_info = asis_java_info[0]
    read_file = codecs.open(asis_java_info["full_path"], 'r', encoding='utf-8',errors='ignore')
    asis_lines = read_file.readlines()
    read_file.close()
      
    tobe_package_split = mapping_info["tobe_package"].split(".");
    tobe_package_java = root_tobe_java_package + "." + mapping_info["tobe_package"] + ".biz" 
    tobe_package_mapper = root_tobe_java_package + "." + mapping_info["tobe_package"] + ".mapper"
    tobe_path_java = root_tobe_java_path + "\\" + pydash.join(tobe_package_split,"\\") + "\\biz"
    tobe_path_mapper = root_tobe_java_path + "\\" + pydash.join(tobe_package_split,"\\") + "\\mapper"
    make_dir_recursive(tobe_path_java)
    make_dir_recursive(tobe_path_mapper)
    
    file_new = []
    file_new.append("package " + tobe_package_java + ";")
    file_new.append('''
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.io.Reader;
import java.nio.charset.Charset;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

import org.apache.ibatis.session.SqlSession;
import com.skt.tdcs.batch.common.config.MasterConnectionFactory;
import com.skt.tdcs.batch.base.AbsBatchJobBiz;
import lombok.extern.slf4j.Slf4j;    
''')
    file_new.append("import " + tobe_package_mapper + ";")
    for line in asis_lines:
        line1 = deleteCarageReturn(line)
        str_tobe = ""
        match_package = pt_package.search(line1)
        if match_package is not None: 
            continue
        
        match_import = pt_import.search(line1)
        if match_import is not None: 
            continue
        
        
        match_asis_class = pt_asis_class.search(line1)
        if match_asis_class is not None:
            str_tobe = change_class_tobe(line1,mapping_info )
            file_new.append("@Slf4j\n")
            file_new.append(str_tobe)
            
            # main 함수 추가
            str_tobe = '''
        // 추가
        private SqlSession sqlSession = MasterConnectionFactory.getSqlSessionFactory().openSession(false);
        private BasBibBDealcoTrgtMgmtMapper mapper = sqlSession.getMapper(BasBibBDealcoTrgtMgmtMapper.class);
    
        // 추가
        public static void main(String[] args) throws Exception {{    
            Map<String, String> request = new HashMap<String, String>();
            for( int i = 1 ; i < args.length ; i++) {{
                request.put("args" + i  , args[i]);
            }}
            {tobe_file_nm} instance = new {tobe_file_nm}();
            // hahs convert
           
            instance.execute(request);
        }}
           \n'''.format(tobe_file_nm=mapping_info["tobe_file_nm"])
            
            file_new.append(str_tobe)
            continue
        
        match_author = pt_author.search(line1)
        if match_author is not None :
            str_tobe = " * @AS-IS " + mapping_info["asis_file_nm"].strip() + '\n'
            str_tobe = str_tobe + line1 
            str_tobe = str_tobe + " * @author 이찬주 (P179230)\n"
            file_new.append(str_tobe)
            continue
        
        match_execute = pt_execute.search(line1)
        if ( match_execute is not None ):
            # 주석관계로 main을 맨 위로 한다.
            aaa = ''
        
        # sqlMap 주석달기
        match_decl_sqlMap =  pt_decl_sqlMap.search(line1)
        if match_decl_sqlMap is not None :
            str_tobe = setComment(line1)
            file_new.append(str_tobe)
            continue
        # sqlMap 사용분 주석달기
        match_sqlMap =  pt_sqlMap.search(line1)
        if match_sqlMap is not None :
            str_tobe = setComment(line1)
            file_new.append(str_tobe)
            # 커밋한 부분은 
            if match_sqlMap.group() is not None and match_sqlMap.groupdict()['action'] is not None:
                action =  match_sqlMap.groupdict()['action']
                sqlEx = ''
                if match_sqlMap.groupdict()['sqlMapEx'] is not None:
                    sqlEx = match_sqlMap.groupdict()['sqlMapEx']
                    
                if action == 'commitTransaction' :
                    str1 = match_sqlMap.groupdict()['space'] + "mapper" + sqlEx +  ".commit();\n"
                    file_new.append(str1)
                
                if action == 'endTransaction' :
                    str1 = match_sqlMap.groupdict()['space'] + "mapper" + sqlEx +  ".close();\n"
                    file_new.append(str1)
            continue
        
        # prog_id pt_
        pt_prog_id = re.compile(r"PROG_ID\s+=\s+\"" + mapping_info["asis_file_nm"].strip() + r"\"", re.IGNORECASE)
        match_prog_id = pt_prog_id.search(line1)
        if match_prog_id is not None :
            str_tobe = change_progid_tobe(line1 ,mapping_info )
            file_new.append(str_tobe)
            continue
        
        # prog_id pt_
        pt_user_id = re.compile(r"USER_ID\s+=\s+\"[\w]+\"", re.IGNORECASE)
        match_user_id = pt_user_id.search(line1)
        if match_user_id is not None :
            str_tobe = change_userid_tobe(line1 ,mapping_info )
            file_new.append(str_tobe)
            continue
        
        
        # sqlMapper
        match_sqlmapper  = pt_sqlmapper.search(line1)
        if match_sqlmapper is not None :
            str_comment = setComment(line1)
            file_new.append(str_comment)
            
            str_tobe = change_sqlmapper(line1 , mapping_info)            
            file_new.append(str_tobe)
            continue
        
        file_new.append(line1)
        # print(pydash.join(file_new, ''))
     
    # 자바파일   
    tobe_full_path = tobe_path_java + "\\" + mapping_info['tobe_file_nm'] + ".java"
    #if not os.path.exists(tobe_full_path) :
    f = open( tobe_full_path , 'w',  encoding='utf8')
    for line in file_new:
        f.write(line + '\n')    
    f.close()
    
    # Mapper 자바파일
    tobe_full_path = tobe_path_mapper + "\\" + mapping_info['tobe_file_nm'] + "Mapper.java"
    #if not os.path.exists(tobe_full_path) :
    f = open( tobe_full_path , 'w',  encoding='utf8')    
    f.write("package " + tobe_package_mapper +";\n")
    str_import = '''import java.util.List;
import java.util.Map;
public interface {tobe_file_nm} {{

}}
'''.format(tobe_file_nm=mapping_info["tobe_file_nm"])

    f.write(str_import)
    f.close()
    
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
    
def main():    
    make_mappingJson()
    scan_asis_java()
    process_list()

def change_class_tobe(vTxt, mapping_info):
    newTxt = re.sub(r"public\s+class\s+(?P<asis_nm>" + mapping_info["asis_file_nm"].strip() + r")\s+extends", 
                    lambda x : change_class_tobe_detail(x , mapping_info) ,
                    # change_class_tobe_detail ,
                    vTxt)
    return newTxt

def change_class_tobe_detail(match_obj,mapping_info):
    if match_obj.group() is not None:
        return 'public class ' + mapping_info["tobe_file_nm"] + " extends" 
    
  
def change_progid_tobe(vTxt, mapping_info):
    newTxt = re.sub(mapping_info["asis_file_nm"].strip(), 
                    lambda x : change_progid_tobe_detail(x , mapping_info) ,
                    # change_class_tobe_detail ,
                    vTxt)
    return newTxt

def change_progid_tobe_detail(match_obj,mapping_info):
    if match_obj.group() is not None:
        return mapping_info["tobe_file_nm"]
    
def change_userid_tobe(vTxt, mapping_info):
    newTxt = re.sub(r"USER_ID\s+=\s+\"(?P<userid>[\w]+)\"", 
                    lambda x : change_userid_tobe_detail(x , mapping_info) ,
                    # change_class_tobe_detail ,
                    vTxt)
    return newTxt

def change_userid_tobe_detail(match_obj,mapping_info):
    if match_obj.group() is not None:
        return  "USER_ID = \"" + mapping_info["tobe_file_nm"][:30] + "\""
    

def change_sqlmapper(vTxt, mapping_info):
    newTxt = re.sub(r"(?P<type>\([\w]+\)\s?)?sqlMap(?P<sqlMapEx>[\w]+)?\.[\w]+\(\"(?P<namespace>[\w]+)\.(?P<sqlId>[\w]+)\"\s?,?\s?(?P<parameter>[\w\"]+)?\)", 
                    lambda x : change_sqlmapper_detail(x , mapping_info) ,
                    # change_class_tobe_detail ,
                    vTxt)
    return newTxt

def change_sqlmapper_detail(match_obj,mapping_info):
    if match_obj.group() is not None:
        type = ''
        if match_obj.groupdict()['type'] is not None :
            type = match_obj.groupdict()['type']
        
        sqlMapEx = ''
        if match_obj.groupdict()['sqlMapEx'] is not None :
            sqlMapEx = match_obj.groupdict()['sqlMapEx']
            
        sqlId = match_obj.groupdict()['sqlId'] ;
        
        parameter = '' 
        if match_obj.groupdict()['parameter'] is not None :
            parameter = match_obj.groupdict()['parameter']
        
        return  type + "mapper" + sqlMapEx + "." + sqlId + "(" + parameter + ")"
        # \1mapper\2.\4(\5)
    

            
def deleteCarageReturn(vTxt):
    newTxt = re.sub(r'\r\n', deleteCarageReturnDetail , vTxt)
    return newTxt

def deleteCarageReturnDetail(match_obj):
    if match_obj.group() is not None:
        return "\n"
    
def setComment(vTxt):
    newTxt = re.sub(r'^(?P<space>\s+)(?P<first>[\w]+)', setCommentDetail , vTxt)
    return newTxt

def setCommentDetail(match_obj):
    if match_obj.group() is not None:
        return  match_obj.groupdict()['space'] + "// "  + match_obj.groupdict()['first']
    

        
if __name__ == '__main__':
    main() 
    # sql= ''
    # convertByInput(sql)    
