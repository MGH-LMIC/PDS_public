#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request
from flask_cors import CORS

import dataLoader
from featureExtractor import extract_feature_light

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def hello():
    return jsonify("Hello World!")

@app.route('/cervical_spine_cb')
def cervical_spine_cb():
    pid = request.args.get("Pid")
    print(pid)
    return jsonify(mock_cervical_spine_cb(patient_id=int(pid)))

@app.route('/find_feature')
def addr_find_feature():
    pid = request.args.get("Pid")
    f_list = request.args.get("F_list").split("__")
    start_date = request.args.get("Start_date")
    end_date = request.args.get("End_date")

    if f_list == None or start_date == None or end_date == None or pid == None:
        result = make_fail('This API need all following params : Pid, F_list, Start_date, End_date')
        return jsonify(result)

    return jsonify(find_feature(pid, f_list, start_date, end_date))


@app.route('/feature_extract', methods=['GET', 'POST'])
def addr_feature_extract():
    note = request.form["note"]
    pid = request.form['mrn']
    f_list = request.form["F_list"].split("__")

    if f_list == None or pid == None:
        result = make_fail('This API need all following params : Pid, F_list')
        return jsonify(result)

    print(note, pid, f_list)
    result = feature_extract_caller(note, f_list)
    result['pid'] = pid
    return jsonify(result)


@app.route('/patient_history')
def get_all_history():
    pid = request.args.get("Pid")

    if pid == None:
        result = make_fail('This API need all following params : Pid')
        return jsonify(result)
    else:
        return jsonify(get_all_patient_hx(pid))

def make_fail(reason):
    result = dict()
    result['result'] = 'Fail'
    result['reason'] = reason
    return result


def mock_find_feature(pid, f_list, start_date, end_date):
    # f_list : list
    # start_date : str (YYYY-MM-DD)
    # end_date :str (YYYY-MM-DD)
    # return dicionary

    patient_id = int(pid)
    mock_result = dict()
    mock_result['Pid'] = str(pid)
    if patient_id % 2:
        mock_result['Result'] = 'Success'
    else:
        mock_result['Result'] = "Fail"
        return mock_result

    sample_stings = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. \
    Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley\
     of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap \
     into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of \
     Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus Pag\
     eMaker including versions of Lorem Ipsum.".split(".")

    n_sample = len(sample_stings)

    info = dict()
    for i, feature in enumerate(f_list):
        info[feature] = dict()
        if (i + patient_id) % 2:
            info[feature]['result'] = True
            info[feature]['sentences'] = sample_stings[i % n_sample]
        else:
            info[feature]['result'] = False
            info[feature]['sentences'] = []
    mock_result['info'] = info
    return mock_result

def mock_cervical_spine_cb(patient_id):
    ## Get int patient_id
    ## return dictionary

    patient_id = int(patient_id)
    mock_result = dict()
    mock_result['Pid'] = str(patient_id)

    if patient_id % 2:
        mock_result['Result'] = 'Success'
    else:
        mock_result['Result'] = "Fail"
        return mock_result

    if patient_id % 3 == 1:
        mock_result['Target'] = 'Infection'
    else:
        mock_result['Target'] = 'Pseudoarthrosis'

    mock_result['Sentence'] = 'This patient have a {}.'.format(mock_result['Target'])
    return mock_result

def get_all_patient_hx(patient_id):

    ## Check parameter
    patient_id = str(patient_id)
    print("PatientID : ", patient_id)

    ## query all note_id
    note_list = dataLoader.load_all_data(patient_id)

    ## Check empty result
    if len(note_list) == 0:
        result = make_fail("No patient data with the patient number")
    else:
        result = {
            'Result': "Success",
            "Notes": note_list
        }

    return result


def feature_extract_caller(paragraph, feature_list):

    result_arr = extract_feature_light(paragraph, feature_list)
    if result_arr:
        result = {
            'Result': "Success",
            "Features": result_arr
        }
    else:
        result = {
            'Result': "Fail",
            "Reason": "No finding with the note."
        }
    return result

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)