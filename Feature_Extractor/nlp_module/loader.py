import re
import spacy
import pandas as pd
import numpy as np
import pickle
import nltk
import time

nlp = spacy.load('en_core_web_lg')
nltk.download('punkt')

def load_rule_dict(nlp_data_dir):
    rule_dict = dict()
    with open("{}/term_rules.p".format(nlp_data_dir), 'rb') as f:
        term_rules = pickle.load(f)
    with open("{}/neg_rules_181105.p".format(nlp_data_dir), "rb") as f:
        neg_rules = pickle.load(f)
    with open("{}/prev_rules.p".format(nlp_data_dir), "rb") as f:
        prev_rules = pickle.load(f)

    rule_dict['term_rules'] = term_rules
    rule_dict['neg_rules'] = neg_rules
    rule_dict['prev_rules'] = term_rules

    return rule_dict


def get_hedge_dict(high_hedges, med_hedges, low_hedges):
    # Set Up Hedge Scoring System & Check That No Hedges Are Placed in Multiple Categories
    for h in high_hedges:
        for m in med_hedges:
            for l in low_hedges:
                if h == m or h == l or l == m:
                    print("ERROR: redundancy found", h, m, l)

    hedge_dict = {}

    for word in low_hedges:
        hedge_dict[word] = 'low'
    for word in med_hedges:
        hedge_dict[word] = 'medium'
    for word in high_hedges:
        hedge_dict[word] = 'high'

    return hedge_dict

def load_feature_dict(nlp_data_dir):
    vis_dis_list = pd.read_csv("{}/pds_vis_dis.csv".format(nlp_data_dir)).name.tolist()
    anatomy_list = pd.read_csv("{}/radlex_anatomy.csv".format(nlp_data_dir)).name.tolist()
    device_list = pd.read_csv("{}/radlex_devices.csv".format(nlp_data_dir)).name.tolist()
    procedure_list = pd.read_csv('{}/radlex_procedures.csv'.format(nlp_data_dir)).name.tolist()

    change_list = pd.read_csv('{}/change_list.csv'.format(nlp_data_dir)).name.tolist()
    normal_list = pd.read_csv('{}/normal_list.csv'.format(nlp_data_dir)).name.tolist()
    degree_list = pd.read_csv('{}/degree_list.csv'.format(nlp_data_dir)).name.tolist()

    locations = pd.read_csv("{}/radlex_location_list.csv".format(nlp_data_dir)).name.tolist()
    descriptors = pd.read_csv("{}/radlex_descriptor_list.csv".format(nlp_data_dir)).name.tolist()
    post_hedge_list = pd.read_csv("{}/post_hedge_list.csv".format(nlp_data_dir)).name.tolist()
    high_hedges = pd.read_csv("{}/high_hedges.csv".format(nlp_data_dir)).name.tolist()
    med_hedges = pd.read_csv("{}/med_hedges.csv".format(nlp_data_dir)).name.tolist()
    low_hedges = pd.read_csv("{}/low_hedges.csv".format(nlp_data_dir)).name.tolist()

    hedge_list = list(set(high_hedges + low_hedges + med_hedges))
    hedge_dict = get_hedge_dict(high_hedges, med_hedges, low_hedges)

    feature_dict = {}
    feature_dict["vis_dis_list"] = vis_dis_list
    feature_dict["anatomy_list"] = anatomy_list
    feature_dict["device_list"] = device_list
    feature_dict["procedure_list"] = procedure_list
    feature_dict["change_list"] = change_list
    feature_dict["normal_list"] = normal_list
    feature_dict["degree_list"] = degree_list
    feature_dict["locations"] = locations
    feature_dict["descriptors"] = descriptors
    feature_dict["post_hedge_list"] = post_hedge_list
    feature_dict["high_hedges"] = high_hedges
    feature_dict["med_hedges"] = med_hedges
    feature_dict["low_hedges"] = low_hedges
    feature_dict["hedge_list"] = hedge_list
    feature_dict["hedge_dict"] = hedge_dict
    feature_dict["hedge_scores"] = {'low': 3, 'medium': 2, 'high': 1}

    return feature_dict


if __name__ == "__main__":
    rule_dir = './rules'
    load_rule_dict(rule_dir)