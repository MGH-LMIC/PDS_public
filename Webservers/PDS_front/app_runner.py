import os

from flask import Flask, flash, redirect, render_template, request, session, abort, jsonify
import urllib.request
import requests
import json

from constants import ConfigConstants as CC
from constants import HtmlConstants as HC 

 

app = Flask(__name__)

@app.route('/')
def home():
    try:
        return render_template(HC.HTML_MAIN_PATH_AND_FILE_NAME, api_host_ip="http://" + request.host)
    except Exception as e:
        return str(e)
    #if not session.get('logged_in'):  # getting session 
    #    return render_template('login.html')
    #else:
    #    return "Hello Boss!  <a href='/logout'>Logout</a>"

#@
# param : list of all indications 
# TODO : should show ONLY chosen / pre-selected ones

@app.route('/patient_history')
def patient_history():

    pid = request.args.get("Pid")
    target_url = CC.API_SERVER_IP_ADDRESS + "/patient_history" + "?Pid=" + pid
    print(target_url)

    with urllib.request.urlopen(target_url) as response:
        the_page = response.read()
        print(the_page)
        return the_page


def display_all_indications(selected_list):
    temp_list = ["Infection", "Tumor" ,"Traumatic Injury", "Deformity", "Myelopathy", "Radiculopathy from DDD of DJD","Pseudoarthrosis", "Non-traumatic instability","Discogenic axial neck pain"]


@app.route('/feature_extract', methods=['POST'])
def addr_feature_extract():
    note = request.form["note"]
    pid = request.form['mrn']
    f_list = request.form["F_list"].split("__")
    # print(pid, note, f_list)

    target_url = CC.API_SERVER_IP_ADDRESS + "/feature_extract"

    res = requests.post(target_url, data=request.form)
    print(res.text)

    return res.text

 
if __name__ == "__main__":
    ## Set app secret_key
    #app.secret_key = os.urandom(12)

    ## Set api address
    CC.set_api_server_ip_address(input("Enter API adress(default=127.0.0.1:5001) :"))

    app.run(debug=True,host=CC.WEB_SERVER_IP_ADDRESS, port=4000)

