import pydash
import excel2json
import os
import pandas

print(os.getcwd())
filepath = os.getcwd() + '\\mapping1.xlsx'
vJson = excel2json.convert_from_file(filepath)
print(vJson)