import pydash
import os
import pandas
import json

print(os.getcwd())
filepath = 'mapping1.xlsx'
excel_data_df = pandas.read_excel(filepath, sheet_name='sheet1')

json_str = excel_data_df.to_json(orient='records')
with open('mapping.json' , 'w+') as f:
    f.write(json_str)
data = json.loads(json_str)
print("Complete!")




# print('Excel Sheet to JSON:\n', json_str)