import pandas as pd
import numpy as np
import time

from nlp_module import load_feature_dict, load_rule_dict
from nlp_module import extract_from_paragraph, extract_from_paragraph_light

def extract_feature(paragraph, feature_list):
    nlp_data_dir = "./nlp_module/rules"
    feature_dict = load_feature_dict(nlp_data_dir)
    rule_dict = load_rule_dict(nlp_data_dir)

    feature_dict["vis_dis_list"] = feature_list
    para_df = extract_from_paragraph(paragraph, feature_dict=feature_dict, rules_dict=rule_dict)

    result_list = []
    for index, row in para_df.iterrows():

        ele = {
            "finding" : row['findings'],
            "finding_types": row['finding_types'],
            "statuses" : row['statuses'],
            "clause" : row['clause']
        }

        result_list.append(ele)
    return result_list


def extract_feature_light(paragraph, feature_list):
    nlp_data_dir = "./nlp_module/rules"
    rule_dict = load_rule_dict(nlp_data_dir)

    para_df = extract_from_paragraph_light(paragraph, feature_list, rules_dict=rule_dict)

    # print("Feature df shape : ", para_df.shape)
    result_list = []
    for index, row in para_df.iterrows():
        ele = {}
        ele['clause'] = row['clause']
        ele['sent'] = row['sent']
        for key in feature_list:
            ele[key] = row[key]
        result_list.append(ele)
    return result_list
