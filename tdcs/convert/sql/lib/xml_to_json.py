import json
import xmltodict


# with open("BASCDM08100.xsql",'r',encoding='UTF8') as f:
#     xmlString = f.read()
#
# jsonString = json.dumps(xmltodict.parse(xmlString), indent=4)
# data = json.loads(jsonString)
# with open("BASCDM08100.json", 'w') as f:
#     f.write(jsonString)



def get_xml_to_json(_xml_file_path ):
    with open(_xml_file_path,'r',encoding='UTF8') as f:
        _xmlString = f.read()
        
    vJsonString = json.dumps(xmltodict.parse(_xmlString), indent=4)
    vJson = json.loads(vJsonString)
    return vJson