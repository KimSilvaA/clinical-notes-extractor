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
            if k == 'current_medications':
                if d[k] == 'No Active Medications.':
                    d[k] = []
                else:
                    d[k] = [item.strip() for item in v.split(";") if item.strip()]
            elif k == 'complaints':
                if d[k] == 'No complaints.':
                    d[k] = []
                else:
                    d[k] = v.strip().lstrip("-").strip()

            elif k == 'allergies':
                if d[k] == 'No Known Allergies.':
                    d[k] = [] 
    return {
        "patient_id": data_list[0],
        "notes": data_list[1:]
}

# clean_data_list = clean_data(data_list)
# data_json = json.dumps(clean_data_list)

fhir_files = ['Abe604_Frami345_b8dd1798-beef-094d-1be4-f90ee0e6b7d5.json',
              'Abraham100_Stracke611_990db43c-4604-a27c-4153-bfa9ef42a9e2.json',
              'Zachary28_Ankunding277_5442450f-35c1-85e9-3b93-e7047cd9813e.json',
              'Zack583_Runte676_2b073598-a7c1-9d50-eb8e-7ffc816d2b91.json',
              'Zane918_Cruickshank494_1b88b604-43a9-dfcb-d0e3-f4fe47eac581.json'




              ]
def main():
    for file_name in fhir_files:
        print(f"Opening {file_name}")
        data_list = get_notes(file_name)
        clean_data_list = clean_data(data_list)
        output_name = f"output_{file_name}"
        file_path = OUTPUT_DIR / output_name
        with open(file_path, "w", encoding="utf-8") as file:
            print(f"Saving output")
            json.dump(clean_data_list, file, indent=4)

if __name__ == '__main__':
    main()
