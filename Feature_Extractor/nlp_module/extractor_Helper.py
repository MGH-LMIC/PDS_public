

import re
import spacy
import pandas as pd
import numpy as np
import pickle
import nltk
import time
from tqdm import tqdm
from nlp_module.loader import load_feature_dict, load_rule_dict, nlp


# ### Supporting Classes (Descriptor, ChangeEntity, ExtractedEntity)
class Descriptor(object):
    def __init__(self, name, qualifiers=[], hedges=[]):
        self.name = name
        self.hedge = self.set_hedging(hedges)
        self.qualifiers = qualifiers

    def set_hedging(self, hedges):
        self.hedge = ", ".join(hedges)

    def describe(self):
        if len(self.qualifiers) > 0:
            return self.name + " (" + ", ".join(self.qualifiers) + ")"
        else:
            return self.name


class ChangeEntity(object):
    def __init__(self, name, prior_exam_exists=False, location='', description=[]):
        self.name = name
        self.prior_exam_exists = prior_exam_exists
        self.location = location
        self.description = description


class ExtractedEntity(object):
    def __init__(self, name, ent_type='', location='', hedges=[],
                 description=[],
                 is_previous=False, is_normal=False, is_negated=False):

        self.name = name

        self.ent_type = ent_type  # Vis-Disease, Anatomy, Procedure, Device, Change
        self.location = location
        self.hedges = hedges
        self.description = description  # this should hold Descriptor objects

        self.previous = is_previous  # should be 'current' or 'previous'
        self.normality = is_normal  # should be 'abnormal' or 'normal'
        self.negated = is_negated

        self.hedging = self.set_hedging(self.hedges)

    def describe(self):
        return_string = ""
        for descriptor in self.description:
            doc = nlp(descriptor.describe())
            tok_pos = [token.pos_ for token in doc]
            if 'NOUN' not in tok_pos:

                if descriptor.hedge is None:
                    return_string = descriptor.describe() + ", " + return_string
                else:
                    # modify this later to match test set format
                    return_string = descriptor.describe() + " (" + descriptor.hedge + "), " + return_string
        return return_string.strip(", ")

    def is_changed(self, change_rules):
        change_present = False

        if self.name in change_rules:
            change_present = True
        for descriptor in self.description:
            if descriptor.name in change_rules:
                change_present = True

        if not change_present:
            return False
        elif self.negated:
            return False
        else:
            return True

    def set_hedging(self, hedges):
        self.hedging = ", ".join(hedges)
        self.hedges = hedges

    def set_hedge_level(self, hedge_dict, hedge_scores):
        for word in self.hedges:
            h_score = hedge_dict[word]

        score = np.sum([hedge_scores[hedge_dict[word]] for word in self.hedges])
        if score <= 1:
            self.hedge_level = 'high'
        elif score >= 3:
            self.hedge_level = 'low'
        else:
            self.hedge_level = 'medium'
        return self.hedge_level

    def get_description(self, certainties=True):
        if certainties:
            return str([str(mod.certainty) + " " + str(mod.name) for mod in self.description]).replace("[", "").replace(
                "]", "")
        else:
            return str([mod.name for mod in self.description]).replace("[", "").replace("]", "")

    def output(self):
        output = str(self.name)
        values = [self.category, self.location,
                  self.get_description(), self.certainty]
        value_names = ['category', 'location', 'description', 'certainty']

        for i in range(len(values)):
            value = values[i]
            if value is not '':
                output = output + "     " + value_names[i].upper() + ": " + value
        return output
