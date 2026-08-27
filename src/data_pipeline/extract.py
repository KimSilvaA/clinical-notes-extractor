from config.clinical_data import * 
import json 
from pathlib import Path 
import base64
import warnings 

'''
Functions to extract data from a JSON report 
'''


def extract_data(report):
    '''
    Input:
    -----
    report_str (str): decoded clinical report in the JSON file
    
    Output:
    -----
    Dict with date, complaint, history, allergies, 
    medication(s), assessment, plan
    '''
    substr = [COMPLAINT_SUBSTR, 
              HISTORY_SUBSTR, 
              SOCIAL_HISTORY_SUBSTR,
              ALLERGIES_SUBSTR, 
              MEDICATIONS_SUBSTR, 
              ASSESSMENT_SUBSTR,
              PLAN_SUBSTR]

    # Array keys 
    output_keys = ['complaints', 'history', 'social_history', 
                   'allergies', 'medications', 'assessment', 'plan']

    # Initialize array to store data 
    data_output = {} 
    

    idx = [report.find(s) for s in substr]

    for i in range(len(substr)):
    # Not storing social history for now
        if substr[i] == SOCIAL_HISTORY_SUBSTR:
            continue
        # Start the slice at the end of the substring 
        start = idx[i] + len(substr[i])

        # If this is the last section, slice to end of report
        if i == len(substr) - 1:
            end = len(report)
        else:
            # Slice until the next keyword 
            end = idx[i + 1]

        data_output[output_keys[i]] = report[start:end].strip()
            
    return data_output 


def get_notes(patient_file):
    '''
    Input
    -----
    FHIR JSON file

    Output
    ------
    list where the first element is the id followed by a dict for each clinical note

    '''
    file_path = RAW_INPUT_DIR / patient_file

    with open(file_path) as file:
        data = json.load(file)
        data_list = [] # Store data entries in list
        try:
            # First entry should be Patient but if not 
            id = data['entry'][0]['resource']['id']
        except KeyError: 
            try:
                id = data['entry'][0]['resource']['subject']['reference']
            except Exception as e:
                warnings.warn(f"Could not get patient id for {patient_file}")
                id = None

        data_list.append(id)
        for entry in data['entry']:
            if entry['resource']['resourceType'] == 'DocumentReference':
                # Get clinical note
                encoded_str = entry['resource']['content'][0]['attachment']['data']
                report = base64.b64decode(encoded_str).decode('utf-8') # Decode note

                data_dict = extract_data(report)
                data_list.append(data_dict)
    return data_list



