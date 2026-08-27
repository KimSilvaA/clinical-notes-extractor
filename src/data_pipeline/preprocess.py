from pathlib import Path 
from src.data_pipeline.extract import *

file_name = 'Zack583_Runte676_2b073598-a7c1-9d50-eb8e-7ffc816d2b91.json'
file_path = RAW_INPUT_DIR / file_name

data_list = get_notes(file_name)



def clean_data(data_list):
    '''
    Goes through the dict entries in the list and cleans up the newlines 
    '''
    dict_entries = data_list[1:]
    for d in dict_entries:
        for k,v in d.items():
            d[k] = v.replace("\n", "")
            if k == 'medications':
                d[k] = v.split(';')
    return data_list

clean_data_list = clean_data(data_list)
