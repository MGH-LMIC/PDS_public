#!/usr/bin/env python
# coding: utf-8

# # ProE- Cervical Spine

# All possible reasons that can indicate cervical spine fusion
# 
# 1.Infection
# 2.Tumor
# 3.Traumatic Injury
# 4.Deformity
# 5.Cervical Myelopathy
# 6.Cervical Radiculopathy from Degenerative Disorders
# 7.Pseudarthrosis in the cervical spine
# 8.Non traumatic instability
# 9.Discogenic axial neck pain
# 

# There are a total of 5 treatment options as listed below:

# In[1]:


option_1 = "Medical/Physical Therapy"
option_2 = "Anterior Cervical Fusion"
option_3 = "Anterior Cervical Fusion and Decompression(Disectomy or Corpectomy)"
option_4 = "Posterior Fusion"
option_5 = "Posterior Fusion and Decompression"


# Based on the user input(Main reason & co-existing conditions), any combination of the above options will be recommended for treatment as Appropriate, Rarely Appropriate & Maybe Appropriate

# In[5]:


# Functions needed to implement the decision making process

# Function to decide userinput based on the question asked
def yes_or_no():
    dic = {'1': 'Yes', '2':'No'}
    print ("Based on the question below, enter '1' for yes or '2' for no and then press enter")
#     for option_num,option in sorted(dic.iteritems(),key=lambda x: x[0]):   
#         print "{}.{}".format(option_num,option)
    

    
# Function to print dashed lines to improve readability       
def print_line():
    print("-" * 80)
    
# Function to decide treatment options based on the reason for cervical spine    
def category(condition):
#     condition 1 = Infection
    if condition == "1":
        yes_or_no()
#         Ask questions related to the condition
        other_sym = raw_input('Are any of the following present:Instability,Failure of an appropriate course of antibiotics to control the infection,Debridement and/or decompression is anticipated to result in instability? ')
        print_line()
        #         Decide treatment option based on user input
        if other_sym == "1":
            print "Appropriate :\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2,option_3,option_4,option_5)
            print_line()
            print "Rarely Appropriate : {}".format(option_1)
            print_line()
        else:
            print "Appropriate:\n{}".format(option_1)
            print_line()
            print "Rarely Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2,option_3,option_4,option_5)
            print_line()
#     condition 2 = Tumor
    elif condition == "2":
        yes_or_no()
#         Ask questions related to the condition
        other_sym = raw_input('Does the patient have instability or anticipated instability from resection and/or decompression? ')
        print_line()
        #         Decide treatment option based on user input
        if other_sym == "1":
            print "Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2,option_3,option_4,option_5)
            print_line()
            print "Rarely Appropriate: {}".format(option_1)
            print_line()
        else:
            print "Appropriate: {}".format(option_1)
            print_line()
            print "Rarely Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2,option_3,option_4,option_5)
            print_line()
#     condition 3 = Traumatic Injury
    elif condition == "3":
        yes_or_no()
        #         Ask questions related to the condition
        other_sym = raw_input('Does the patient have instability or anticipated instability from decompression? ')
        print_line()
#         Decide treatment option based on user input
        if other_sym == "1":
            print "Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2,option_3,option_4,option_5)
            print_line()
            print "Rarely Appropriate: {}".format(option_1)
            print_line()
        else:
            print "Appropriate: {}".format(option_1)
            print_line()
            print "Rarely Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2,option_3,option_4,option_5)
            print_line()
#     condition 4 = Deformity
    elif condition == "4":
        yes_or_no()
    #         Ask questions related to the condition
        other_sym = raw_input('Are any of the following present:Inability of the patient to maintain a forward gaze,substantial functional limitation or documented progression of deformity')
        print_line()
    #         Decide treatment option based on user input
        if other_sym == "1":
            print "Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2,option_3,option_4,option_5)
            print_line()
            print "Maybe Appropriate:\n{}".format(option_1)
            print_line()
        else:
            print "Appropriate:{}".format(option_1)
            print_line()
            print "Rarely Appropriate :\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2,option_3,option_4,option_5)
            print_line()
#     condition 5 = Cervical Myelopathy   
#         Decide treatment option based on user input
    elif condition == "5":         
        print "Appropriate:\n1.{}\n2.{}".format(option_3,option_5)
        print_line()
        print "Maybe Appropriate:\n{}".format(option_1)
        print_line()
        print "Rarely Appropriate :\n1.{}\n2.{}".format(option_2,option_4)
        print_line()
#       condition 6 = Cervical Radiculopathy from Degenerative Disorders        
    elif condition == "6":
        yes_or_no()
    #         Ask questions related to the condition
        other_sym = raw_input('Does the patient have severe symptoms preventing work or have a functionally limiting motor weakness?')
        print_line()
    #         Decide treatment option based on user input
        if other_sym == "1":
            print "Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2,option_3,option_4,option_5)
            print_line()
            print "Maybe Appropriate:\n{}".format(option_1)
            print_line()
        else:
            yes_or_no()
            #         Ask questions related to the condition
            other_sym_list= raw_input('Does the patient have radiculopathy explained by imaging or has failed 6-12 week course of non-operative treatment')
            print_line()
        #         Decide treatment option based on user input
            if other_sym_list == "1":
                print "Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2,option_3,option_4,option_5)
                print_line()
                print "Maybe Appropriate:\n{}".format(option_1)
                print_line()
            else:
                print "Appropriate:{}".format(option_1)
                print_line()
                print "Rarely Appropriate :\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2,option_3,option_4,option_5)
                print_line()
#       condition 7 = Pseudarthrosis in the cervical spine 
    elif condition == "7":
        yes_or_no()
        #         Ask questions related to the condition
        other_sym = raw_input('Is there a demonstrated presence of a gross failure of the instrumentation (e.g. screw breakage, screw loosening, curve/correction decompression)? ')
        #         Decide treatment option based on user input
        if other_sym == "1":
            print "Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2,option_3,option_4,option_5)
            print_line()
            print "Rarely Appropriate: {}".format(option_1)
            print_line()
        else:
            
            print_line()
            other_sym_list = ["Postoperative onset of mechanical neck pain that is approximately at the level of the pseudarthrosis","A period of time following the index surgery during which the patient had symptomatic relief","Nonoperative care of at least 3 months from the onset of symptoms","CT or plain films that are highly suggestive of nonunion at a motion segment at which a fusion had been previously attempted. These criteria include:-Lack of bridging bone-Dynamic motion noted on flexion-extension radiographs"]
            i=1
            for string in other_sym_list:
                print "{}.{}".format(i,string)
                i+=1
            #         Ask questions related to the condition
            other_check = raw_input('Are all these conditions present?')
            #         Decide treatment option based on user input
            if other_check == "1":
                print "Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2,option_3,option_4,option_5)
                print_line()
                print "Rarely Appropriate: {}".format(option_1)
                print_line()
            else:
                print "Appropriate:{}".format(option_1)
                print_line()
                print "Rarely Appropriate :\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2,option_3,option_4,option_5) 
                print_line()
#       condition 8 = Non traumatic instability            
    elif condition == "8":
        yes_or_no()
        #         Ask questions related to the condition
        other_sym = raw_input('Are any of the following present:basilar invagination,C1-C2 widening greater than 3 mm or subaxial instability (C2-T1)with atleast 2 mm on flexion-extension views? ')
        print_line()
        #         Decide treatment option based on user input
        if other_sym == "1":
            print "Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2,option_3,option_4,option_5)
            print_line()
            print "Rarely Appropriate:{}".format(option_1)
            print_line()
        else:
            print "Appropriate:{}".format(option_1)
            print_line()
            print "Rarely Appropriate :\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2,option_3,option_4,option_5)
            print_line()
#       If none of the above 1-8 condition,its  Discogenic axial neck pain            
    else:
        print "Rarely Appropriate:\n1.{}\n2.{}\n3.{}\n4.{}".format(option_2,option_3,option_4,option_5)
        print_line()
        print "Appropriate: {}".format(option_1)
        print_line()


# In[6]:


print "All possible conditions that can indicate cervical spine fusion:"
print_line()
   
dic2 = {'1':'Infection(eg:Tuberculosis,discitis,osteomyelitis,epidural abscess)',
      '2':'Tumor',
      '3':'Traumatic Injury(eg:fracture,fracture-dislocation,dislocation,traumatic ligamentous disruption)',
      '4':'Deformity(eg:kyphosis,head-drop syndrome,post-laminectomy deformity)',
      '5':'Cervical Myelopathy(eg:disc herniation,bony stenosis,OPLL as an adjunct to decompression,synovial facet cyst)',
      '6':'Cervical Radiculopathy from Degenerative Disorders(eg:(either from disc herniation,synovial facet cyst,bony stenosis), as an adjunct to disc excision)',
      '7':'Pseudarthrosis in the cervical spine',
      '8':'Non traumatic instability((of a motion segment(defined as two adjacent vertebrae and associated ligaments, disc, and facet capsules), such as that which occurs in patients with inflammatory arthritis)',
      '9':'Discogenic axial neck pain(no radiographic evidence of nerve root or spinal compression, instability, or spinal deformity)'}
 
for symptom_num,symptom in sorted(dic2.iteritems(),key=lambda x: x[0]):   
    print "{}.{}".format(symptom_num,symptom)
    


# In[8]:


# Ask user the reason for cervical spine
cause = raw_input('What is the reason for cervical spine fusion?(Enter a number from the list above and press enter?')
print_line()
    
for disease_category,symptoms in dic2.iteritems():  
   
    if disease_category == cause:            
        category(disease_category)
