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
java_path = r'C:\dev\workspace\tdcs-batch\src\main\java\com\skt\tdcs\batch'
java_file_list = [] 
java_file_list1 = {} # 인덱스

java_package_file = r'C:\dev\workspace\tdcs-batch-sql\javaconvert\batch\batch_file_package_list.txt'


mappingJson = []
mappingJson1 = {}


def main():    
    # make_mappingJson()
    scan_asis_java()

    
def scan_asis_java():
    global java_file_list 
    global java_file_list1 
    
    
    file_pattern = "*.java"
    exclude = set(['asis-mybatis','common','base','file',''])
    for path, subdirs, files in os.walk(java_path):
        subdirs[:] = [d for d in subdirs if d not in exclude]
        for name in files:
            m_mapper = fnmatch(name,"*Mapper.java")
            m_java = fnmatch(name, file_pattern)
            if m_java and not m_mapper :
                java_file_list.append({
                    "full_path": os.path.join(path,name)
                    ,"file_path": path
                    , "file_name" : name
                })
                
    # java_file_list1 = pydash.group_by(java_file_list, ['file_name'])    
   
    f = open(java_package_file,'w' , encoding='utf8' )
    for file_info in java_file_list :
        file_path = file_info['file_path']
        
        m_file = re.search( r'C:\\dev\\workspace\\tdcs-batch\\src\\main\\java\\com\\skt\\tdcs\\batch' , file_path , re.IGNORECASE)
        
        package_split = file_path[m_file.regs[0][1]:].split("\\")
        package_pure = package_split[1:3]
        package_pure_str = pydash.join(package_pure,".")
        # v_file_name = pydash.pad_end(file_info['file_name'].split(".")[0],50,' ')
        # f.write(v_file_name + package_pure_str + '\n')
        v_file_name = file_info['file_name'].split(".")[0]        
        f.write(v_file_name +','+ package_pure_str + '\n')
        
    
    f.close();

    


        
if __name__ == '__main__':
    main() 
    # sql= ''
    # convertByInput(sql)    
