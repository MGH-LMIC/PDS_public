#!/usr/bin/env python
# coding: utf-8

from print_functions import *


# There are a total of 5 treatment options as listed below:
option_1 = "Medical/Physical Therapy"
option_2 = "Anterior Cervical Fusion"
option_3 = "Anterior Cervical Fusion and Decompression(Disectomy or Corpectomy)"
option_4 = "Posterior Fusion"
option_5 = "Posterior Fusion and Decompression"


# Functions needed to implement the decision making process
def traumatic_injury_diagram():
    print_yesOrNo()
    #         Ask questions related to the condition
    other_sym = input('Does the patient have instability or anticipated instability from decompression? ')
    print_line()
    #         Decide treatment option based on user input
    if other_sym == "1":
        print("Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2, option_3, option_4, option_5))
        print_line()
        print("Rarely Appropriate: {}".format(option_1))
        print_line()
    else:
        print("Appropriate: {}".format(option_1))
        print_line()
        print("Rarely Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2, option_3, option_4, option_5))
        print_line()

def tumor_diagram():
    print_yesOrNo()
    #         Ask questions related to the condition
    other_sym = input(
        'Does the patient have instability or anticipated instability from resection and/or decompression? ')
    print_line()
    #         Decide treatment option based on user input
    if other_sym == "1":
        print("Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2, option_3, option_4, option_5))
        print_line()
        print("Rarely Appropriate: {}".format(option_1))
        print_line()
    else:
        print("Appropriate: {}".format(option_1))
        print_line()
        print("Rarely Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2, option_3, option_4, option_5))
        print_line()

def infection_diagram():
    print_yesOrNo()
    #         Ask questions related to the condition
    other_sym = input(
        'Are any of the following present:Instability,Failure of an appropriate course of antibiotics to control the infection,Debridement and/or decompression is anticipated to result in instability? ')
    print_line()
    #         Decide treatment option based on user input
    if other_sym == "1":
        print("Appropriate :\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2, option_3, option_4, option_5))
        print_line()
        print("Rarely Appropriate : {}".format(option_1))
        print_line()
    else:
        print("Appropriate:\n{}".format(option_1))
        print_line()
        print("Rarely Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2, option_3, option_4, option_5))
        print_line()

def deformity_diagram():
    print_yesOrNo()
    #         Ask questions related to the condition
    other_sym = input(
        'Are any of the following present:Inability of the patient to maintain a forward gaze,substantial functional limitation or documented progression of deformity')
    print_line()
    #         Decide treatment option based on user input
    if other_sym == "1":
        print("Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2, option_3, option_4, option_5))
        print_line()
        print("Maybe Appropriate:\n{}".format(option_1))
        print_line()
    else:
        print("Appropriate:{}".format(option_1))
        print_line()
        print("Rarely Appropriate :\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2, option_3, option_4, option_5))
        print_line()

def cervical_myelopathy_diagram():
    #         Decide treatment option based on user input
    print("Appropriate:\n1.{}\n2.{}".format(option_3, option_5))
    print_line()
    print("Maybe Appropriate:\n{}".format(option_1))
    print_line()
    print("Rarely Appropriate :\n1.{}\n2.{}".format(option_2, option_4))
    print_line()

def cervical_radiculopathy_diagram():
    print_yesOrNo()
    #         Ask questions related to the condition
    other_sym = input(
        'Does the patient have severe symptoms preventing work or have a functionally limiting motor weakness?')
    print_line()
    #         Decide treatment option based on user input
    if other_sym == "1":
        print("Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2, option_3, option_4, option_5))
        print_line()
        print("Maybe Appropriate:\n{}".format(option_1))
        print_line()
    else:
        print_yesOrNo()
        #         Ask questions related to the condition
        other_sym_list = input(
            'Does the patient have radiculopathy explained by imaging or has failed 6-12 week course of non-operative treatment')
        print_line()
        #         Decide treatment option based on user input
        if other_sym_list == "1":
            print("Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2, option_3, option_4, option_5))
            print_line()
            print("Maybe Appropriate:\n{}".format(option_1))
            print_line()
        else:
            print("Appropriate:{}".format(option_1))
            print_line()
            print("Rarely Appropriate :\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2, option_3, option_4, option_5))
            print_line()

def pseudarthrosis_diagram():
    print_yesOrNo()
    #         Ask questions related to the condition
    other_sym = input(
        'Is there a demonstrated presence of a gross failure of the instrumentation (e.g. screw breakage, screw loosening, curve/correction decompression)? ')
    #         Decide treatment option based on user input
    if other_sym == "1":
        print("Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2, option_3, option_4, option_5))
        print_line()
        print("Rarely Appropriate: {}".format(option_1))
        print_line()
    else:

        print_line()
        other_sym_list = [
            "Postoperative onset of mechanical neck pain that is approximately at the level of the pseudarthrosis",
            "A period of time following the index surgery during which the patient had symptomatic relief",
            "Nonoperative care of at least 3 months from the onset of symptoms",
            "CT or plain films that are highly suggestive of nonunion at a motion segment at which a fusion had been previously attempted. These criteria include:-Lack of bridging bone-Dynamic motion noted on flexion-extension radiographs"]
        i = 1
        for string in other_sym_list:
            print("{}.{}".format(i, string))
            i += 1
        #         Ask questions related to the condition
        other_check = input('Are all these conditions present?')
        #         Decide treatment option based on user input
        if other_check == "1":
            print("Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2, option_3, option_4, option_5))
            print_line()
            print("Rarely Appropriate: {}".format(option_1))
            print_line()
        else:
            print("Appropriate:{}".format(option_1))
            print_line()
            print("Rarely Appropriate :\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2, option_3, option_4, option_5))
            print_line()


def discogenic_neckpain_diagram():
    print("Rarely Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2, option_3, option_4, option_5))
    print_line()
    print("Appropriate: {}".format(option_1))
    print_line()


def nontraumatic_instability_diagram():
    print_yesOrNo()
    #         Ask questions related to the condition
    other_sym = input(
        'Are any of the following present:basilar invagination,C1-C2 widening greater than 3 mm or subaxial instability (C2-T1)with atleast 2 mm on flexion-extension views? ')
    print_line()
    #         Decide treatment option based on user input
    if other_sym == "1":
        print("Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2, option_3, option_4, option_5))
        print_line()
        print("Rarely Appropriate:{}".format(option_1))
        print_line()
    else:
        print("Appropriate:{}".format(option_1))
        print_line()
        print("Rarely Appropriate :\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2, option_3, option_4, option_5))
        print_line()