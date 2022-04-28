import json
import xmltodict


with open("BASCDM08100.xsql",'r',encoding='UTF8') as f:
    xmlString = f.read()
    
jsonString = json.dumps(xmltodict.parse(xmlString), indent=4)
data = json.loads(jsonString)
with open("BASCDM08100.json", 'w') as f:
    f.write(jsonString)


