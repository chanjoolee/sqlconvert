import pydash
import os
import pandas
import json

# print(os.getcwd())
# filepath = 'mapping1.xlsx'
# excel_data_df = pandas.read_excel(filepath, sheet_name='sheet1')
#
# json_str = excel_data_df.to_json(orient='records')
# with open('mapping.json' , 'w+') as f:
#     f.write(json_str)
# data = json.loads(json_str)
# print("Complete!")k


def make_mapping_json_file(_excel_file_path, _sheet_name , _make_file_path):
    v_excel_data_df = pandas.read_excel(_excel_file_path, sheet_name=_sheet_name)
    v_json_str = v_excel_data_df.to_json(orient='records')
    with open(_make_file_path , 'w', encoding='utf-8') as f:
    # with open(_make_file_path , 'w') as f:
        # f.write(v_json_str)
        json.dump(json.loads(v_json_str), f , indent="\t")  
    print("Make json File Completed! : "  + _make_file_path)
    
def make_mapping_json_file_1(_excel_file_path, _sheet_name , _make_file_path):
    v_excel_data_df = pandas.read_excel(_excel_file_path, sheet_name=_sheet_name)
    v_json_str = v_excel_data_df.to_json(orient='records')
    with open(_make_file_path , 'w', encoding='utf-8') as f:
        f.write(v_json_str)
        # json.dump(json.loads(v_json_str), f , indent="\t")  
    print("Make json File Completed! : "  + _make_file_path)
def get_mapping_json(_excel_file_path, _sheet_name):
    v_excel_data_df = pandas.read_excel(_excel_file_path, sheet_name=_sheet_name)
    v_json_str = v_excel_data_df.to_json(orient='records')
    v_return_json = json.loads(v_json_str)
    
    return v_return_json

# print('Excel Sheet to JSON:\n', json_str)

if __name__ == '__main__':
    _excel_file_path = r'C:\dev\workspace\tdcs-convert\tdcs\convert\sql\mapping_0422.xlsx'
    _sheet_name = 'Sheet1'
    _make_file_path = r'C:\dev\workspace\tdcs-convert\tdcs\convert\sql\mapping_0422.json' 
    make_mapping_json_file(_excel_file_path, _sheet_name , _make_file_path)
    
    #_make_file_path1 = r'C:\dev\workspace\tdcs-convert\tdcs\convert\sql\mapping1_1.json'   
    # make_mapping_json_file_1(_excel_file_path, _sheet_name , _make_file_path1)   