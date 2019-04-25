#!/usr/bin/env python
# coding: utf-8

# ------------------------------------------------------------
# # PDS- Cervical Spine : made by Poornima Ramamraj, Myeongchan Kim
# ------------------------------------------------------------

from print_functions import *
from diagram_functions import *

'''
All possible reasons that can indicate cervical spine fusion
1.Infection
2.Tumor
3.Traumatic Injury
4.Deformity
5.Cervical Myelopathy
6.Cervical Radiculopathy from Degenerative Disorders
7.Pseudarthrosis in the cervical spine
8.Non traumatic instability
9.Discogenic axial neck pain
'''
category_desc_dict = {
    '1': 'Infection(eg:Tuberculosis,discitis,osteomyelitis,epidural abscess)',
    '2': 'Tumor',
    '3': 'Traumatic Injury(eg:fracture,fracture-dislocation,dislocation,traumatic ligamentous disruption)',
    '4': 'Deformity(eg:kyphosis,head-drop syndrome,post-laminectomy deformity)',
    '5': 'Cervical Myelopathy(eg:disc herniation,bony stenosis,OPLL as an adjunct to decompression,synovial facet cyst)',
    '6': 'Cervical Radiculopathy from Degenerative Disorders(eg:(either from disc herniation,synovial facet cyst,bony stenosis), as an adjunct to disc excision)',
    '7': 'Pseudarthrosis in the cervical spine',
    '8': 'Non traumatic instability((of a motion segment(defined as two adjacent vertebrae and associated ligaments, disc, and facet capsules), such as that which occurs in patients with inflammatory arthritis)',
    '9': 'Discogenic axial neck pain(no radiographic evidence of nerve root or spinal compression, instability, or spinal deformity)'
}

# Based on the user input(Main reason & co-existing conditions), any combination of the above options will be recommended for
# treatment as Appropriate, Rarely Appropriate & Maybe Appropriate
def show_diagram(condition):
    if condition == "1": # condition 1 = Infection
        infection_diagram()

    elif condition == "2": # condition 2 = Tumor
        tumor_diagram()

    elif condition == "3": # condition 3 = Traumatic Injury
        traumatic_injury_diagram()

    elif condition == "4": # condition 4 = Deformity
        deformity_diagram()

    elif condition == "5": # condition 5 = Cervical Myelopathy
        cervical_myelopathy_diagram()

    elif condition == "6": # condition 6 = Cervical Radiculopathy from Degenerative Disorders
        cervical_radiculopathy_diagram()

    elif condition == "7": # condition 7 = Pseudarthrosis in the cervical spine
        pseudarthrosis_diagram()

    elif condition == "8": # condition 8 = Non traumatic instability
        nontraumatic_instability_diagram()

    elif condition == "9": #       condition 9 = Discogenic axial neck pain
        discogenic_neckpain_diagram()

    else:
        print("Wrong value is inputed : ", condition, "value should be 1-9")
        raise AssertionError


# Function to decide treatment options based on the reason for cervical spine
def run_with_category_selections():
    ## Show category list
    for symptom_num, symptom in sorted(category_desc_dict.items(), key=lambda x: x[0]):
        print("{}.{}".format(symptom_num,symptom))

    # Ask user the reason for cervical spine
    cause = input('What is the reason for cervical spine fusion?(Enter a number from the list above and press enter?')
    print_line()

    for disease_category, symptoms in category_desc_dict.items():
        if disease_category == cause:
            show_diagram(disease_category)


if __name__ == "__main__":
    # Ask users to choose options
    print("All possible conditions that can indicate cervical spine fusion:")
    print_line()

    ## Run
    run_with_category_selections()
