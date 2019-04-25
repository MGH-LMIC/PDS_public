#!/usr/bin/python
# -*- coding: utf-8 -*-

import time

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def hello():
    ## Realistic
    time.sleep(0.5)
    return jsonify("Hello World!")

@app.route('/cervical_spine_cb')
def cervical_spine_cb():
    pid = request.args.get("Pid")
    print(pid)

    ## Realistic
    time.sleep(0.5)

    return jsonify(mock_cervical_spine_cb(patient_id=int(pid)))

@app.route('/find_feature')
def find_feature():
    pid = request.args.get("Pid")
    f_list = request.args.get("F_list").split("__")
    start_date = request.args.get("Start_date")
    end_date = request.args.get("End_date")

    ## Realistic
    time.sleep(0.5)
    if f_list == None or start_date == None or end_date == None or pid == None:
        result = dict()
        result['Result'] = 'Fail'
        result['Reason'] = 'This API need all params : Pid, F_list, Start_date, End_date'
        return jsonify(result)

    return jsonify(mock_find_feature(pid, f_list, start_date, end_date))


@app.route('/patient_history')
def get_all_history():
    pid = request.args.get("Pid")

    ## Realistic
    time.sleep(0.5)

    if pid == None:
        result = dict()
        result['Result'] = 'Fail'
        result['Reason'] = 'This API need all params : Pid, F_list, Start_date, End_date'
        return jsonify(result)

    return jsonify(mock_patient_history(pid))


def mock_patient_history(pid):
    ## Make returning dictionary
    result = dict()


    if int(pid) % 2 == 0:

        result['Result'] = 'Fail'
        result['Reason'] = 'There is no patient with the patient id.'
        return result

    else:
        result['Result'] = 'Success'
        result['Notes'] = [
            {
            "contents": "Rectal hemorrhage; Pt. states that symptoms have resolve as of 9/9/13    ",
            'date' : "2015-02-21 00:00:00.0000000",
            'note_id' : '263991075',
            },
        {
            'contents': "Anxiety    ",
            'date': "2015-02-21 00:00:00.0000000",
            'note_id': '263991079',
        },
        {
            'contents': "Multiple thyroid nodules - R lobe    ",
            'date': "2015-02-21 00:00:00.0000000",
            'note_id': '263991089',
        },
        {
            'contents': "Neck pain    ",
            'date': "2015-02-21 00:00:00.0000000",
            'note_id': '263991092',
        },
        {
            'contents': "Exam Number:  17673957                        Report Status:  Final  Type:  Cervical Spine 2 or 3 Views  Date/Time:  10/24/2014 12:03  Exam Code:  XRCS1  Ordering Provider:  Hilfinger, Maureen    HISTORY:         spondyliolithesis, neck pain. -            REPORT     Cervical Spine  2 or 3 Views               COMPARISON: CT cervical spine 9/19/2014.               FINDINGS:       There is grade 1 anterolisthesis at C6-7 with linear defects in the        posterior elements representing abnormal segmentation of the C5-6        facet joints. The C5 articular pillars are elongated craniocaudally,        while the C6 articular pillars are short. Flexion and extension views        reveal no abnormal motion within the cervical spine.               Cervical spine is straightened. No acute fracture or compression        fracture or prevertebral soft tissue swelling. There is degenerative        disc disease at C6-7.                                 IMPRESSION:       Redemonstration of segmentation anomaly affecting the C5-6 facet        joints.               Grade 1 anterolisthesis at C6-7. No abnormal motion between flexion        and extension.                          PROVIDERS:                           SIGNATURES:       Huang, Ambrose J M.D.                   Huang, Ambrose J M.D.    ",
            'date': "2015-02-22 00:00:00.0000000",
            'note_id': '271016765',
        },
        ]
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5001)