# coding: utf-8

import re
import spacy
import pandas as pd
import numpy as np
import pickle
import nltk
import time
from tqdm import tqdm
from nlp_module.loader import load_feature_dict, load_rule_dict, nlp
from nlp_module.extractor import ReportExtractor
from nlp_module.extractor_Helper import *


def sort_list(lst):
    lengths = [len(item) for item in lst]
    lst_df = pd.Series(lengths, index=lst)  # , columns = ['len'])
    lst_df = lst_df.sort_values(ascending=False)
    return lst_df.index.tolist()


# ### Sentence Processing
def pre_process_sents(findings):
    if type(findings) == None or type(findings) == float:
        return []
    else:
        sentences = nltk.tokenize.sent_tokenize(findings)
        sentences = [sent.lower() for sent in sentences]
        sentences = [sent.split("   ") for sent in sentences]
        sentences = [sent for sents in sentences for sent in sents]
        sentences = [re.sub('\d+?/\d+?/\d{2,}', '', sent) for sent in sentences]
        sentences = [sent.replace("/", " ").replace("\n", " ") for sent in sentences]
        # sentences = [sent.replace("chronic obstructive pulmonary disease", "copd") for sent in sentences]
        # sentences = [sent.replace("coronary artery bypass graft", "cabg") for sent in sentences]
        # sentences = [sent.replace("coronary bypass surgery", "cabg") for sent in sentences]
        # sentences = [sent.replace("tb", "tuberculosis") for sent in sentences]
        # sentences = [sent.replace("cp", "costophrenic") for sent in sentences]
        sentences = [sent.replace(".", " ") for sent in sentences]
        return sentences


def get_sents(df):
    imps, finds = [], []
    for i in range(len(df)):
        pt = df.iloc[i]
        imps.append(pre_process_sents(pt.IMPRESSION))
        finds.append(pre_process_sents(pt.FINDINGS))
    imps = list(set([sent for sents in imps for sent in sents]))
    finds = list(set([sent for sents in finds for sent in sents]))
    return imps, finds


# ### ClauseSplitter
'''Split initial list of sentences into a list of sentences by clause'''
def split_by_clause(sentence, term_rules):
    # print("Sentence:", sentence)
    '''Subfunction to split up sentence if the word AND is present'''

    def split_ands(phrase):
        if phrase.count('and') == 1 and "," not in phrase:
            parts = phrase.split('and')
            pos1 = [token.pos_ for token in nlp(parts[0])]
            pos2 = [token.pos_ for token in nlp(parts[1])]
            if 'NOUN' in pos1 and 'VERB' in pos1 and 'NOUN' in pos2 and 'VERB' in pos2:  # maybe also 'ADV'
                return parts
            else:
                return [phrase]
        else:
            return [phrase]


    '''Subfunction to split up sentence into comma-separated phrases'''

    def split_sent_by_comma(sent):

        ## Find all commas
        comma_indices = [c.start() for c in re.finditer(',', sent)]

        ## If commas are more than 5, treat it as a single sentence.
        if len(comma_indices) > 5:
            return [sent]

        ## ------------------------
        ## Find commas not for sents
        ## ------------------------
        oxford_comma_indices = []
        no_oxford_comma_indices = []

        # if oxford comma
        reg_pattern = ', (((\w+\s?){1,3},)\s)+'
        if re.findall(reg_pattern, sent):
            found_indices = [(c.start(), c.end()) for c in re.finditer(reg_pattern, sent)]
            indices_and = [(start, end+3) for (start, end) in found_indices if 'and' == sent[end:end + 3]]
            indices_or = [(start, end+2) for (start, end) in found_indices if 'or' == sent[end:end + 2]]
            oxford_comma_indices += list(set(indices_and) | set(indices_or))

        # if no oxford comma
        reg_pattern = '((\w+\s?){1,3},\s?)+?(\s\w+){1,3}?'
        if not oxford_comma_indices and re.findall(reg_pattern, sent):
            found_indices = [(c.start(), c.end()) for c in re.finditer(reg_pattern, sent)]
            indices = [(start, end + re.search(r'\s(and|or)', sent[end:end+10]).end()) for (start, end) in found_indices if re.findall(r'\s(and|or)', sent[end:end+10])]
            no_oxford_comma_indices += list(indices)

        word_comma_indices = oxford_comma_indices + no_oxford_comma_indices
        for index_tuple in word_comma_indices:
            start_word_comma, end_oxford_comma = index_tuple
            comma_indices = [x for x in comma_indices if x not in range(start_word_comma, end_oxford_comma)]

        # if comma_indices:
        #     print("Sent commas: ", comma_indices)

        ## Split a sentence with sentences comma
        sxns = [sent[i:j] for i, j in zip([0] + comma_indices, comma_indices + [len(sent)])]

        return sxns

    term_pat, clauses = "\[TERM\]", []

    for rule in term_rules:  # check every rule for a clause termination word
        reformatRule = re.sub(r'\s+', '_', rule[0].strip())

        sentence = rule[3].sub(' ' + rule[2].strip()  # add in Negation tag to
                               + reformatRule + rule[2].strip() + ' ', sentence)

    if re.findall(term_pat, sentence, flags=re.IGNORECASE):
        # if termination words exist, split up the phrases by them
        phrases = re.split(term_pat, sentence, flags=re.IGNORECASE)
        phrases = [" ".join([word.strip() for word in phrase.split()]) for phrase in phrases if len(phrase.split()) > 1]
        phrases = [split_sent_by_comma(phrase) for phrase in phrases]  # Split phrases by comma, except in list case
        phrases = sum(phrases, []) # [phrase for sub_phrase in phrases for phrase in sub_phrase]
        phrases = [re.split(';|:', phrase) for phrase in phrases]
        phrases = sum(phrases, []) # [phrase for sub_phrase in phrases for phrase in sub_phrase]
        phrases = [phrase.split("  ") for phrase in phrases]
        phrases = sum(phrases, []) # [phrase for sub_phrase in phrases for phrase in sub_phrase]
    else:
        # if no termination words exist, return listicized sentence following other split rules
        phrases = split_sent_by_comma(sentence)
        phrases = [re.split(';|:', phrase) for phrase in phrases]
        phrases = sum(phrases, [])  # [phrase for sub_phrase in phrases for phrase in sub_phrase]
        phrases = [phrase.split("  ") for phrase in phrases]
        phrases = sum(phrases, [])  # [phrase for sub_phrase in phrases for phrase in sub_phrase]
        phrases = [split_ands(phrase) for phrase in phrases]
        phrases = sum(phrases, [])  # [phrase for sub_phrase in phrases for phrase in sub_phrase]

    phrases = [phrase.replace(" -,", " - ,") for phrase in phrases]
    for phrase in phrases:
        if len(phrase) != 0:
            clauses.append(phrase.lower())
    return clauses



def remove_double_errors(df):
    if 'effusion' in df.findings.values and 'pleural effusion' in df.findings.values:
        df = df[df.findings != 'effusion']
    if 'effusions' in df.findings.values and 'pleural effusions' in df.findings.values:
        df = df[df.findings != 'effusions']
    if 'process' in df.findings.values and re.findall('\S+\s+process', ", ".join(df.findings.values)):
        df = df[df.findings != 'process']
    if 'processes' in df.findings.values and re.findall('\S+\s+processes', ", ".join(df.findings.values)):
        df = df[df.findings != 'processes']
    if 'disease' in df.findings.values and (re.findall('\S+\s+disease', ", ".join(df.findings.values))):
        df = df[df.findings != 'disease']
    return df


def remove_submatches(matches_to_search):
    unique_matches = []

    while len(matches_to_search) > 0:
        match1 = max(matches_to_search, key=len)
        related_matches = [match1]
        matches_to_search.remove(match1)
        for match2 in matches_to_search:
            if match2 in match1:
                related_matches.append(match2)
        unique_matches.append(max(related_matches, key=len))
        for match in related_matches:
            if match in matches_to_search:
                matches_to_search.remove(match)
    return unique_matches


def get_abnormals(df):
    abnormals = []
    for finding in df[df.statuses == 'current'].findings:
        is_normal = False
        for word in normal_list + ["stable", "aerated", "aerated (well)"]:
            if word in finding.replace("(", "").replace(")", ""):
                is_normal = True
        if not is_normal:
            abnormals.append(finding)

    # include previous procedures
    procedure_df = df[df.finding_types == 'procedure']
    procedure_df = procedure_df[procedure_df.statuses == 'previous']
    for finding in procedure_df.findings:
        abnormals.append(finding)
    return list(set(remove_submatches(abnormals)))


def get_abnormals_and_locs(df):
    abnormal_locs = []
    abnormal_descrs = []

    currents = df[df.statuses == 'current']
    for idx in range(len(currents)):
        finding = currents.iloc[idx].findings
        is_normal = False
        for word in normal_list + ["stable", "aerated", "aerated (well)"]:
            if word in finding.replace("(", "").replace(")", ""):
                is_normal = True
        if not is_normal:
            abnormal_locs.append((finding, currents.iloc[idx].locations))
            abnormal_descrs.append((finding, currents.iloc[idx].descriptors))

    # include previous procedures
    procedure_df = df[df.finding_types == 'procedure']
    procedure_df = procedure_df[procedure_df.statuses == 'previous']
    for idx in range(len(procedure_df)):
        finding = procedure_df.iloc[idx].findings
        abnormal_locs.append((finding, procedure_df.iloc[idx].locations))
        abnormal_descrs.append((finding, procedure_df.iloc[idx].descriptors))
    return list(set(remove_submatches(abnormal_locs))), list(set(remove_submatches(abnormal_descrs)))


def get_findings(df):
    devices = []
    df = df[df.statuses != 'negated']
    df = df[df.statuses != 'negated, previous']
    df = df[df.statuses != 'previous']
    for finding in df.findings:
        devices.append(finding)
    return list(set(remove_submatches(devices)))


def get_changes(df):
    changes = []
    df = df[df.statuses != 'negated']
    df = df[df.statuses != 'negated, previous']
    for i in range(len(df)):
        change_description = df.iloc[i].findings + ", " + df.iloc[i].descriptors
        if len(change_description.split()) > 1:
            changes.append(change_description)
    return list(set(remove_submatches(changes)))


def get_changes_and_locs(df):
    change_locs = []
    change_descrs = []
    df = df[df.statuses != 'negated']
    df = df[df.statuses != 'negated, previous']
    for i in range(len(df)):
        change_description = df.iloc[i].findings + ", " + df.iloc[i].descriptors
        if len(change_description.split()) > 1:
            change_locs.append((change_description, df.iloc[i].locations))
            change_descrs.append((df.iloc[i].findings, df.iloc[i].descriptors))
    return list(set(remove_submatches(change_descrs))), list(set(remove_submatches(change_locs)))


def convert_list_to_string(list_items):
    #     print(list_items)
    if len(list_items) == 0 or list_items is None:
        final_str = ""
    else:
        #         for idx, item in enumerate(list_items):
        #             if "," in str(item):
        #                 words = item.split(',')
        #                 item = "__".join([word.strip() for word in words])
        #                 list_items[idx] = item
        final_str = "--".join([str(item) for item in list_items])
    print(list_items, final_str)
    return final_str


def merge_paragraphs(list_of_paragraph):
    ## return all merged paragraph
    report_interest = ""
    for paragraph in list_of_paragraph:
        if type(paragraph) != float:
            report_interest += paragraph

    return report_interest


# skipped 20737
def extract_from_rednet_report(radnet):
    all_abnorms, all_devices, all_vis_diseases, all_changes, all_procedures, all_anatomies = [], [], [], [], [], []
    for i in tqdm(range(len(radnet))):
        abnormalities, devices, vis_diseases, changes, procedures, anatomies = [], [], [], [], [], []

        findings = radnet.iloc[i].FINDINGS
        impression = radnet.iloc[i].IMPRESSION
        conclusion = radnet.iloc[i].Conclusion

        report_interest = merge_paragraphs([findings, impression, conclusion])

        patient_sents = pre_process_sents(report_interest)
        results = get_patient_results(patient_sents, feature_dict)

        if results is not None and len(results) > 0:
            abnormalities = get_abnormals(results[results.finding_types != 'change'])

            changes = get_changes(results[results.finding_types == 'change'])

            procedures = get_findings(results[results.finding_types == 'procedure'])

        all_abnorms.append(abnormalities)
        all_devices.append(devices)
        all_anatomies.append(anatomies)
        all_procedures.append(procedures)
        all_vis_diseases.append(vis_diseases)
        all_changes.append(changes)

    return pd.DataFrame([all_abnorms, all_devices, all_vis_diseases, all_anatomies, all_procedures, all_changes],
                        index=['abnorms', 'devices', 'vis_diseases', 'anatomies', 'procedures', 'changes']).T



def extract_from_calues(clauses, rules_dict, feature_dict):
    clause_outputs = []

    for clause in clauses:
        start = time.time()
        extractor = ReportExtractor(clause=clause, neg_rules=rules_dict["neg_rules"],
                                    prev_rules=rules_dict["prev_rules"],
                                    vis_dis_list=feature_dict["vis_dis_list"],
                                    anatomy_list=feature_dict["anatomy_list"],
                                    procedure_list=feature_dict["procedure_list"],
                                    device_list=feature_dict["device_list"],
                                    change_list=feature_dict["change_list"],

                                    locations_list=feature_dict["locations"],
                                    descriptor_list=sort_list(feature_dict["descriptors"]),
                                    normal_list=feature_dict["normal_list"],

                                    hedge_list=feature_dict["hedge_list"],
                                    post_hedge_list=feature_dict["post_hedge_list"],
                                    hedge_dict=feature_dict['hedge_dict'],
                                    hedge_scores=feature_dict['hedge_scores'],
                                    grab=True)

        clause_output = extractor.run_extractor()

        if clause_output.shape[0]:
            # clause_outputs.append(extractor.run_extractor())
            clause_outputs.append(clause_output)
        clause_output['clause'] = clause

    return clause_outputs


def get_patient_results(sents, feature_dict):
    rules_dict = feature_dict['rule_dict']
    patient_sent_dfs = []
    for sent in sents:
        pt_paths, pt_neg_paths, pt_changes, pt_devices, pt_procedures, pt_norm_anatomy = [], [], [], [], [], []
        print("Sent:", sent)

        clauses = split_by_clause(sent, rules_dict["term_rules"])
                # print("run_extractor: {:.2f}sec".format(time.time() - start), clause_outputs[-1].shape)
        # print(len(clause_outputs))

        clause_outputs = extract_from_calues(clauses)

        if len(clause_outputs) != 0:
            print(pd.concat(clause_outputs).shape)
            patient_sent_dfs.append(pd.concat(clause_outputs))

    return patient_sent_dfs


def extract_findings_from_reports(df, rules_dict, feature_dict):
    hedge_dict = feature_dict['hedge_dict']
    hedge_scores = feature_dict['hedge_scores']

    all_results = pd.DataFrame()
    for i in tqdm(range(len(df))):
        accnum = df.iloc[i].accnum
        findings = df.iloc[i].FINDINGS
        impression = df.iloc[i].IMPRESSION
        conclusion = df.iloc[i].Conclusion

        report_interest = ""
        if type(findings) != float:
            report_interest += findings
        if type(impression) != float:
            report_interest += impression
        if type(conclusion) != float:
            report_interest += conclusion

        patient_sents = pre_process_sents(report_interest)
        results = get_patient_results(patient_sents, feature_dict)
        all_results = all_results.append(results, ignore_index=True)
    return all_results


def extract_runner():
    feature_dict = load_feature_dict()

    # radnet = pd.read_excel("data/csvs/radnet_norm_parsed.xlsx")
    # df = pd.read_csv("{}/radnet_cxr_100K_reports_parsed.csv".format(cxr_rpt_dir), delimiter="|", dtype=str)
    df = pd.read_csv("{}/sample.csv".format(cxr_rpt_dir), delimiter="|", dtype=str)

    extracted_findings = extract_findings_from_reports(df, rule_dict, feature_dict)
    list_columns = ['accnum', 'findings', 'finding_types', 'certainties', 'statuses', 'descriptors', 'locations',
                    'changed']

    extracted_findings = extracted_findings[list_columns]
    work_df = df

    list_columns = ['accnum', 'abnorms', 'devices', 'vis_diseases', 'anatomies', 'procedures', 'changes']
    extracted_findings = extract_from_rednet_report(work_df)
    extracted_findings['accnum'] = pd.Series(list(work_df['accnum']))
    extracted_findings = extracted_findings[list_columns]

    extracted_findings['FINDINGS'] = pd.Series(list(work_df['FINDINGS']))
    extracted_findings['IMPRESSION'] = pd.Series(list(work_df['IMPRESSION']))
    extracted_findings['CONCLUSION'] = pd.Series(list(work_df['Conclusion']))
    extracted_findings['REPORT'] = pd.Series(list(work_df['report']))

    # Save Extracts
    extracted_findings.to_csv("outputs/extracts_all_1.csv", index=None)
    extracts = pd.read_csv("outputs/extracts_all_1.csv")  # .drop("Unnamed: 0", axis = 1)


def extract_from_paragraph(paragraph, feature_dict, rules_dict):
    outputs = []
    sents = pre_process_sents(paragraph)
    print("len sent", len(sents))
    for sent in sents:
        clauses = split_by_clause(sent, rules_dict["term_rules"])
        outputs += extract_from_calues(clauses, rules_dict, feature_dict)

    if outputs:
        result_df = pd.concat(outputs, axis=0).reset_index()
        result_df = result_df.sort_values('findings')
        result_df = result_df.drop(columns=['index'])
    else:
        result_df = pd.DataFrame()

    return result_df


def extract_from_paragraph_light(paragraph, target_list, rules_dict):
    outputs = []
    sents = pre_process_sents(paragraph)
    print("len sent", len(sents))

    filler = "_"
    term_rules = rules_dict['term_rules']
    neg_rules = rules_dict['neg_rules']

    output_df = pd.DataFrame()
    for sentence in sents:
        start_time = time.time()
        clauses_in_sent = split_by_clause(sentence, term_rules)
        execution_time = time.time() - start_time
        if execution_time > 1000:
            print("clauses", clauses_in_sent, file=open('../data/logs/long_clauses_{}.log'.format(time.time()), "a"))

        def show_neg_with_cla(cla, target):
            if target in cla.lower():
                # print(cla, target)
                for rule in neg_rules:
                    reformatRule = re.sub(r'\s+', filler, rule[0].strip()) # rule[0] == not_had
                    cla = rule[3].sub(' ' + rule[2].strip() + reformatRule + rule[2].strip() + ' ', cla)
                    # 'not had' -> ' [PREN]note_had[PREN] '
                if re.findall('\[[A-Za-z]{4}\]', cla):
                    tag = '-'
                else:
                    tag = '+'
                return tag

            return ""

        for cla in clauses_in_sent:
            # print('Len of clauses :', len(cla), cla)
            row = pd.Series()
            if len(cla) < 3:
                continue

            row['clause'] = cla
            row['sent'] = sentence

            result_tag = ""
            for target in target_list:
                tag = show_neg_with_cla(cla, target)
                row[target] = tag
                result_tag += tag

            ## Add only clasue having tag
            if result_tag.strip():
                output_df = output_df.append(row, ignore_index=True)

    return output_df



if __name__ == "__main__":
    # extract_runner()

    nlp_data_dir = "./rules"
    cxr_rpt_dir = "../../data"

    feature_dict = load_feature_dict(nlp_data_dir)
    rule_dict = load_rule_dict(nlp_data_dir)

    # text = "'EXAM: X-RAY CHEST PA AND LATERAL  HISTORY: Pneumonia, unspecified organism per script. Cough and congestion for 3 years. Chest pain since sternum injury from car accident on June 2, 2017. COPD. Hypertension controlled by medication. Former smoker for 55 years that quit 5 months ago.  TECHNIQUE: 2 views of the chest.  COMPARISON: 10/18/2017, 12/8/2014, and 1/16/2014  FINDINGS:  Cardiomediastinal silhouette is within normal limits. Atheromatous calcifications of the aorta. Mitral annulus calcifications.  Patchy infiltrate in the region of the superior segment of the right lower lobe is slightly decreased since 10/18/2017 and appears new since the 2014 x-rays. Relatively stable patchy density at the right lung base which may be from scarring or atelectasis. The lungs are hyperinflated consistent with chronic obstructive pulmonary disease. The left lung appears grossly clear.  Stable probable pleural thickening at the right lung base.  Degenerative changes of the spine. The bones appear demineralized.   IMPRESSION:  Patchy infiltrate in the region of the superior segment of the right lower lobe is slightly decreased since 10/18/2017. Other stable findings as described above.'"
    # result_df = extract_from_paragraph(text, feature_dict, rule_dict)
    # print(result_df)
    # result_df.to_csv('result_sample1.csv', index=False, encoding='utf8')
    #
    # text = "Exam Number:  17271262                        Report Status:  Final  Type:  CTChestWC  Date/Time:  08/01/2014 11:22  Exam Code:  CTCHW  Ordering Provider:  Hochberg, Ephraim P MD    HISTORY:         Lymphadenopathy - Neoplasm - Lymphoma           REPORT     CT scan of the chest  WITH intravenous contrast, using standard        protocol.               COMPARISON: 8/05/2013, 9/6/2011, 8/16/2010                   FINDINGS:       Lines/tubes:  There is a right chest port, the catheter tip is near        the cavoatrial junction.                Lungs and Airways:  The central airways are patent. There is left        lower lobe cylindrical bronchiectasis and thickening of subsegmental        bronchi. There is a right upper lobe central 1 cm groundglass opacity        on image 47, unchanged since 2010. A left upper lobe noncalcified 2        mm nodule on image 66 is also unchanged since 2010.               Pleura: There are partially calcified bilateral pleural plaques. No        pleural effusions.               Heart and mediastinum: The thyroid gland is unchanged.  Mediastinal        lymph nodes measure up to 8 mm short axis in the lower right        paratracheal station and 5 mm in the AP window, unchanged. No hilar        or axillary lymphadenopathy is seen. There is atherosclerotic        calcification of the coronary arteries, aortic valve and aorta. There        is cardiomegaly. No pericardial effusion. There is distal esophageal        wall thickening and a small hiatal hernia.               Soft tissues: Normal.               Abdomen: Please refer to separately dictated Abdominal CT.                Bones: There are new minimally displaced healing fractures of the        left lateral eighth and ninth ribs. Again seen are degenerative        changes. There are no suspicious lytic or blastic lesions.               IMPRESSION:        No evidence of lymphoma a the thorax.          "
    # result_df = extract_from_paragraph(text, feature_dict, rule_dict)
    # print(result_df)
    # result_df.to_csv('result_sample2.csv', index=False, encoding='utf8')
    #
    #
    # text = "  Thoracic Surgery Inpatient Post-Op Check     Attending: Dr. Christopher Morse   Hospital Day: 0 Post Op Day #0  Procedure: Procedure(s) (LRB):  THORACOSCOPY VIDEO ASSISTED LOBECTOMY WITH BRONCHOSCOPY FLEXIBLE (Right)    Recent Events:   No acute issues, pain relatively well controlled.     Vitals:  36.8 \xb0C (98.3 \xb0F) | P 90 | BP 102/60 | RR 18  | SpO2 100 %  |  3 | FiO2     |      Fluid Balance:  I/O       10/21 0000 - 10/21 2359 10/22 0000 - 10/22 2359    I.V.  800    IV Piggyback  100    Total Intake  900    Chest Tube  47    Total Output  47    Net  +853                Labs:  No results for input(s): WBC, HGB, HCT, PLT, NA, K, CL, CO2, BUN, EGFR, CRE, GLU, MG, PHOS, CA, CRP, ALBUMIN, TP, SGPT, SGOT, ALKPHOS, BILITOT, BILIDIR, AMY, LIPASE in the last 72 hours.  No results for input(s): PT, PTT, INR in the last 72 hours.  No results for input(s): TROPI in the last 72 hours.    Medications:  IVF:   \u2022 lactated Ringers 75 mL/hr (10/22/18 1458)   \u2022 morphine     \u2022 sodium chloride Stopped (10/22/18 1100)     Scheduled Meds:  \u2022 acetaminophen  650 mg Oral Q6H    Or   \u2022 acetaminophen  650 mg Rectal Q6H   \u2022 heparin  5,000 Units Subcutaneous Q8H SCH   \u2022 nicotine  1 patch Transdermal Daily      PRN Meds:  fentaNYL, haloperidol lactate, HYDROmorphone, ipratropium-albuterol, nalOXone, ondansetron **OR** ondansetron, polyethylene glycol, senna, sodium chloride    Current Diet: Diet Clear liquid; Thin  Advance diet as tolerated    Exam:  General: appears well, NAD  Neuro: alert and conversant, NAD  CV: RRR  Resp: symmetric chest wall expansion, unlabored breathing, CTAB  Abdomen: soft, non-tender, non-distended  Extremities: WWP  Incisions: CDI, appropriate peri-incisional tenderness  Tubes/Drains: CT, thin sanguinous, no AL     CXR  IMPRESSION:   Interval right upper lobectomy with right apical chest tube in place. There is  relative lucency at the right apex with equivocal small pneumothorax as detailed  above. Attention to this area at follow-up is advised    Assessment & Plan:  51 yo F former smoker with RUL nodule, FDG Avid and biopsy proven with atypical cells.    Morse  10/22: FB, VATS RULobectomy    Post Op Day #0 Procedure(s) (LRB):  THORACOSCOPY VIDEO ASSISTED LOBECTOMY WITH BRONCHOSCOPY FLEXIBLE (Right)    Plan:  N:morphine PCA, Tylenol. Can add toradol if chest tube output is low   Pulm: CT to H20 seal. Cxr in pacu and tomorrow   C: no home meds   FEN/GI: Clrs, ADAt, LR@75   GU: DTv   Heme/ID: no issues   Ppx: HepSC   Dispo: Inpatient floor  Code Status: Full Code (Presumed)"
    # result_df = extract_from_paragraph(text, feature_dict, rule_dict)
    # print(result_df)
    # result_df.to_csv('result_sample3.csv', index=False, encoding='utf8')


    sent = "  labs:  no results for input(s): wbc, hgb, hct, plt, na, k, cl, co2, bun, egfr, cre, glu, mg, phos, ca, crp, albumin, tp, sgpt, sgot, alkphos, bilitot, bilidir, amy, lipase in the last 72 hours "
    split_by_clause(sentence=sent, term_rules=rule_dict['term_rules'])

    sent = '''RegExr was created by gskinner.com, and is proudly hosted by Media Temple.
Edit the Expression & Text to see matches. Roll over matches or the expression for details. PCRE & Javascript flavors of RegEx are supported.
The side bar includes a Cheatsheet, full Reference, and Help. You can also Save & Share with the Community, and view patterns you create or favorite in My Patterns.
Explore results with the Tools below. Replace & List output custom results. Details lists capture groups. Explain describes your expression in plain English.
Sentence split sent by comma:   labs:  no results for input(s): wbc, hgb, hct, plt, na, k, cl, co2, bun, egfr, cre, glu, mg, phos, ca, crp, albumin, tp, sgpt, sgot, alkphos, bilitot, bilidir, amy, lipase, and in the last 72 hours 
'''
    print(split_by_clause(sentence=sent, term_rules=rule_dict['term_rules']))

    sent = '''result letter by dr ****  appears he was not concerned pt denies fever,chills,abd pain,dysphagia,odynophagia,brbpr,urinary symptoms,lh,dizziness,pnd,orthopnea,personal or fhx of blood clots,numbness,tingling,weakness in ext,bowel bladder issues,taking ocp ,wt loss etc'''
    print(split_by_clause(sentence=sent, term_rules=rule_dict['term_rules']))