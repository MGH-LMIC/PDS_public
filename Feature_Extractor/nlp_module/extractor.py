
import re
import spacy
import pandas as pd
import numpy as np
import pickle
import nltk
import time
import datetime

from tqdm import tqdm
from nlp_module.loader import load_feature_dict, load_rule_dict, nlp
from nlp_module.extractor_Helper import *

class ReportExtractor(object):
    def __init__(self,
                 clause=None, neg_rules=None, prev_rules=None,

                 vis_dis_list=[], anatomy_list=[],
                 procedure_list=[], device_list=[], change_list=[],

                 locations_list=[], descriptor_list=[], normal_list=[],

                 hedge_list=[], post_hedge_list=[],
                 hedge_dict={}, hedge_scores={}, grab=False):

        self.__filler = '_'
        self.__clause = clause
        self.__clause_doc = nlp(clause)
        self.__keys = ['visual_disease', 'anatomy', 'procedure', 'device', 'change']
        self.__neg_rules = neg_rules
        self.__prev_rules = prev_rules
        self.__vis_dis_list = vis_dis_list
        self.__anatomy_list = anatomy_list
        self.__procedure_list = procedure_list
        self.__device_list = device_list

        self.__joined_rules = []

        for rule_set in [neg_rules, prev_rules]:
            if rule_set is not None:
                self.__joined_rules = self.__joined_rules + rule_set

        self.__dicts = self.bind_dicts([vis_dis_list, anatomy_list, procedure_list, device_list, change_list])

        self.__neg_list = [rule[0] for rule in neg_rules if rule[3] is not '[PSEU]']
        self.__location_list = locations_list
        self.__descriptor_list = descriptor_list
        self.__normal_list = normal_list
        self.__change_list = change_list

        self.__hedge_list = hedge_list
        self.__post_hedges = post_hedge_list
        self.__hedge_dict = hedge_dict
        self.__hedge_scores = hedge_scores

        self.__grab = grab
        return None

    '''MAIN CALL'''

    def run_extractor(self):
        start_time = time.time()
        # cur_time = time.time()
        self.__chunks, self.__tagged_chunks, self.__raw_mapping_dicts, self.__full_chunks_dicts = self.run_chunker()
        # cur_time = time.time()
        # print("Time-run_chunker(sec) : ", cur_time - start_time)
        # start_time = cur_time
        self.__tagged_clause = self.tag(self.__clause)
        # cur_time = time.time()
        # print("Time-tag(sec) : ", cur_time - start_time)
        # start_time = cur_time
        self.__chunk_idx_dicts = self.get_indices()
        # cur_time = time.time()
        # print("Time-get_indices(sec) : ", cur_time - start_time)
        # start_time = cur_time
        self.__all_entities = self.parse_indices()  # should be a list of ExtractedEntity objects
        # cur_time = time.time()
        # print("Time-parse_indices(sec) : ", cur_time - start_time)
        # start_time = cur_time
        self.apply_hedges()
        # cur_time = time.time()
        # print("Time-apply_hedges(sec) : ", cur_time - start_time)
        # start_time = cur_time
        result = self.clean_output()
        # cur_time = time.time()
        # print("Time-clean_output(sec) : ", cur_time - start_time)
        return result

    '''INITIALIZING FUNCTIONS'''

    def bind_dicts(self, lists):
        new_dict, key_idx = {}, 0
        for lst in lists:
            new_dict[self.__keys[key_idx]] = lst
            key_idx += 1
        return new_dict

    def tag(self, phrase):
        for rule in self.__joined_rules:
            reformatRule = re.sub(r'\s+', self.__filler, rule[0].strip())
            phrase = rule[3].sub(' ' + rule[2].strip() + reformatRule + rule[2].strip() + ' ', phrase)
        return phrase

    '''MAPPING TO RADLEX FUNCTIONS'''

    def map_text_to_radlex(self, text, dictionary):
        text = text.strip()
        if text in dictionary:
            return text, text

        # SUFFIX SUBSTITUTIONS
        # plurals
        elif text.replace("'s", "") in dictionary:
            return text, text.replace("'s", "")
        elif text.replace("ies", "y") in dictionary:
            return text, text.replace("ies", "ty")
        elif text.replace("es", "is") in dictionary:
            return text, text.replace("es", "is")
        elif text[:-1] in dictionary:
            return text, text[:-1]
        # -ing/-ed/-ion words all map to -ed (ie, "hyperinflation of the lungs")
        elif text.replace("ing", "ed") in dictionary:
            return text, text.replace("ing", "ion")
        elif text.replace("ing", "") in dictionary:  # should catch also spurring/spur
            return text, text.replace("ing", "")
        elif text.replace("ring", "") in dictionary:
            return text, text.replace("ring", "")
        elif text.replace("ion", "ed") in dictionary:
            return text, text.replace("ion", "ed")
        elif text.replace("ative", "ed") in dictionary:
            return text, text.replace("ative", "ed")
            # -atous/-a matches (ie emphysema/emphysematous, atheroma/atheromatous)
        elif text.replace("tous", "") in dictionary:
            return text, text.replace("tous", "")
        # WHY THIS?
        elif text.replace("ed", "ement") in dictionary:
            return text, text.replace("ed", "ement")
        # haziness/hazy
        elif text.replace("iness", "y") in dictionary:
            return text, text.replace("iness", "y")
        # mildly/mild
        elif text.replace("ly", "") in dictionary:
            return text, text.replace("ly", "")
            # tortuousity/tortuous
        elif text.replace("ity", "") in dictionary:
            return text, text.replace("ity", "")
        # infiltrate/infiltration
        elif text.replace("e", "ion") in dictionary:
            return text, text.replace("e", "ion")

        # AFFIX SUBSTITUTIONS
        elif text.replace("para", "") in dictionary:
            return text, text.replace("para", "")
        elif text.replace("peri", "") in dictionary:
            return text, text.replace("peri", "")
        elif text.replace("bi", "") in dictionary:
            return text, text.replace("bi", "")

        else:
            return None, None

    def map_to_radlex(self, chunk, dictionary):
        if type(chunk) != str:
            text = chunk.text
        else:
            text = chunk
        text_words, word_idx = text.split(), 0

        found_mapping = False

        while not found_mapping and word_idx < len(text_words):
            raw_text, mapped = self.map_text_to_radlex(text, dictionary)
            if raw_text is not None:
                found_mapping = True
            else:
                word_idx += 1
                text = " ".join(text_words[word_idx:])

        if word_idx == len(text_words) and not found_mapping:
            for word in text_words[:-1]:
                if not found_mapping:
                    raw_text, mapped = self.map_text_to_radlex(word, dictionary)
                    if raw_text is not None:
                        found_mapping = True

        return [raw_text, mapped]

    def remove_submatches(self, matches_to_search):
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

    def map_modifiers(self, possible_modifiers):
        mod_descriptors = []
        is_normal = False

        for modifier in possible_modifiers:
            # print("IN MAP MODIFIERS, mapping", modifier)
            descripts = self.map_to_radlex(modifier, self.__descriptor_list)
            normals = self.map_to_radlex(modifier, self.__normal_list)

            if descripts[0] is not None:
                # print("found a descriptor, ", descripts[0])
                descr_name, adverbs = descripts[0], []
                descr_token = [token for token in self.__clause_doc if token.text == descripts[0]][0]
                if descr_token.pos_ == 'VERB' or descr_token.pos_ == 'ADJ':
                    adverbs = [child.text for child in descr_token.children if child.pos_ == 'ADV']
                mod_descriptors.append(Descriptor(name=descr_name, qualifiers=adverbs))
            if normals[0] is not None:
                is_normal = True
        return is_normal, mod_descriptors

    def map_locations(self, possible_locations):
        # print("in MAP LOCATIONS, considering ", possible_locations)
        locations = []
        for location in possible_locations:
            locs = self.map_to_radlex(location, self.__location_list)

            if locs[0] is not None:
                locations.append(locs[0])
        return locations

    def run_chunker(self):
        # KEYS ORDER: 'visual-disease', 'anatomy', 'procedure', 'device', 'change'
        num_keys = len(self.__keys)
        chunk_lists, tagged_chunk_lists = [[] for i in range(num_keys)], [[] for i in range(num_keys)]
        mapping_dicts, full_chunk_dicts = [{} for i in range(num_keys)], [{} for i in range(num_keys)]

        chunks = list(set([chunk for chunk in self.__clause_doc.noun_chunks] + [token for token in self.__clause_doc if
                                                                                token.pos_ == 'VERB' or token.pos_ == 'NOUN' or token.pos_ == 'ADJ']))
        narrowed_chunk_texts = self.remove_submatches([chunk.text for chunk in chunks])
        chunks = [chunk for chunk in chunks if chunk.text in narrowed_chunk_texts]
        self.__spacy_chunks = chunks

        # Sort chunks and store mappings
        for chunk_list_idx in range(num_keys):
            for chunk in chunks:
                raw, mapped = self.map_to_radlex(chunk, self.__dicts[self.__keys[chunk_list_idx]])

                if raw is not None and raw not in chunk_lists[chunk_list_idx]:
                    full_chunk_dicts[chunk_list_idx][raw] = chunk
                    chunk_lists[chunk_list_idx].append(raw)
                    mapping_dicts[chunk_list_idx][raw] = mapped

            chunk_lists[chunk_list_idx] = self.remove_submatches(chunk_lists[chunk_list_idx])

        ## Ignore exception for lymph node
        # # caveat
        # if "lymph node" in " ".join(chunk_lists[1]):
        #     replace_vis_dis_list = []
        #     for chunk in chunk_lists[0]:  # vis_dis
        #         if "node" not in chunk:
        #             replace_vis_dis_list.append(chunk)
        #     chunk_lists[0] = replace_vis_dis_list

        # Tag the raw_text of the chunks with rules (allow for proper indexing later)
        tagged_chunk_list_idx = 0
        for chunk_list in chunk_lists:
            for raw in chunk_list:
                tagged_chunk_lists[tagged_chunk_list_idx].append(self.tag(raw))
            tagged_chunk_list_idx += 1

        return chunk_lists, tagged_chunk_lists, mapping_dicts, full_chunk_dicts

    def get_indices(self):
        chunk_idx_dicts = []
        for lst in self.__tagged_chunks:
            chunk_idx_dict = {}
            for tagged_chunk in lst:
                chunk_idx_dict[tagged_chunk] = self.__tagged_clause.index(tagged_chunk)
            chunk_idx_dicts.append(chunk_idx_dict)
        return chunk_idx_dicts

    '''CHECK NEGATIONS AND PREVIOUS STATUS'''

    def check_change_negation(self, raw_chunk):
        is_negated = False

        for token in self.__clause_doc:

            if token.text in raw_chunk:
                if token.pos_ == 'NOUN':
                    to_check = [child.text for child in token.children]
                else:
                    to_check = [child.text for anc in [anc for anc in token.ancestors] for child in anc.children]

                for word in self.__neg_list:
                    if word in to_check:
                        is_negated = True
        return is_negated

    def check_negation(self, chunk_idx):
        # Find the indices of the pre-negation, post-negation flags
        clause_words, preneg_idxs, postneg_idxs = self.__tagged_clause.split(), [], []

        for word in clause_words:
            if re.findall('\[PREN\]|\[PREP\]', word):
                preneg_idxs.append(self.__tagged_clause.index(word))
            if re.findall('\[POST\]|\[POSP\]', word):
                postneg_idxs.append(self.__tagged_clause.index(word))

        # return false if no negation tags present
        if len(preneg_idxs) == 0 and len(postneg_idxs) == 0:
            return False

        # extract only those tags that are before or after the chunk idx
        preneg_idxs = [neg_idx for neg_idx in preneg_idxs if neg_idx < chunk_idx]
        postneg_idxs = [neg_idx for neg_idx in postneg_idxs if neg_idx > chunk_idx]

        # Set pre-neg/post-neg/previous indices, handling multiple negations
        if len(preneg_idxs) % 2 == 0:
            is_pre_negated = False
        else:
            is_pre_negated = True

        if len(postneg_idxs) % 2 == 0:
            is_post_negated = False
        else:
            is_post_negated = True

        neg_sum = is_pre_negated + is_post_negated

        if neg_sum % 2 == 0:  # if not pre or post negated, or if both pre and post negated
            return False
        if neg_sum == 1:
            return True

    def check_previous(self, chunk_idx):
        clause_words, prev_idxs = self.__tagged_clause.split(), []

        for word in clause_words:
            if re.findall('\[PREV\]', word):
                prev_idxs.append(self.__tagged_clause.index(word))
        if len(prev_idxs) == 0:
            return False
        else:
            prev_idx = prev_idxs[0]
            if prev_idx < chunk_idx:
                return True
        return False

    ###DEBUG LOCATIONS
    '''PARSING ENTITIES FUNCTIONS'''

    def get_modifiers(self, token, location=False):

        children = [child.text for child in token.children if child.pos_ in ['ADJ', 'ADV', 'NOUN', 'VERB']]
        ancestors = [anc.text for anc in token.ancestors if anc.pos_ in ['VERB', 'ADJ', 'ADV', 'NOUN']]
        additionals = [tok.text for tok in self.__clause_doc if (tok.dep_ in ['conj', 'acomp', 'xcomp']) and (
        token in [child for child in tok.children] or token in [anc for anc in tok.ancestors])]

        dets = [tok.text for tok in self.__clause_doc if
                tok.dep_ is 'det' and (token in [anc for anc in tok.ancestors])]

        if location:
            lost_adjs = [tok.text for tok in self.__clause_doc if
                         tok.pos_ == 'ADJ' and token in [anc for anc in tok.ancestors]]
        else:
            lost_adjs = []
        possible_modifiers = list(set(children + ancestors + additionals + dets + lost_adjs))

        # print("IN GET MODIIFERS, possible mods are ", possible_modifiers)

        if not location:
            narrowed_modifiers = []
            for modifier in possible_modifiers:
                mod_token = [tok for tok in self.__clause_doc if tok.text == modifier][0]
                mod_dependents = [child for child in mod_token.children] + [anc for anc in mod_token.ancestors]
                if token in mod_dependents:
                    narrowed_modifiers.append(modifier)
            # print("not location, returning a narrowed version")  #DEBUG
            return narrowed_modifiers
        else:
            return possible_modifiers

    def get_location(self, ent):

        possible_modifiers = []
        for token in self.__clause_doc:
            if token.text in ent:
                possible_modifiers = possible_modifiers + self.get_modifiers(token, location=True)
        location = self.map_locations(possible_modifiers)

        # Check anatomy chunks for mapping
        anatomy_chunks = self.__chunks[1]
        # print("IN GET LOCATION,   FULL LIST OF ANATOMY CHUNKS ARE: ", anatomy_chunks)
        for anatomy in anatomy_chunks:
            anatomy_chunk = self.__full_chunks_dicts[1][anatomy]
            # print("IN GET LOCATION, considering chunk", anatomy, "with full chunk", anatomy_chunk, "\n")

            if type(anatomy_chunk) == spacy.tokens.span.Span:
                ancestors = [anc.text for anc in anatomy_chunk.root.ancestors]
                children = [child.text for child in anatomy_chunk.root.children]

            else:
                ancestors = [anc.text for anc in anatomy_chunk.ancestors]
                children = [child.text for child in anatomy_chunk.children]

            # print("considering ancestors and children", ancestors, children)
            retain_anatomy = []
            for word in ent.split(" "):
                # print("looking at word", word)
                # print("it should match ", ancestors + children)
                if word in ancestors + children:
                    words = anatomy_chunk.text.split()
                    refined_words = []
                    for word in words:
                        # print("LOOKING AT WORD", word)
                        if word not in ["the", "a"]:
                            if self.map_to_radlex(word, self.__location_list)[0] is not None:
                                refined_words.append(word)
                            elif self.map_to_radlex(word, self.__anatomy_list)[0] is not None:
                                refined_words.append(word)
                    location.append(" ".join(refined_words))
        location = list(set(location))
        location = self.remove_submatches(location)
        return location

    def parse_entity(self, idx, ent_type):
        entity_chunks, raw_chunks = self.__tagged_chunks[idx], self.__chunks[idx]
        chunk_idx_dict = self.__chunk_idx_dicts[idx]
        entity_ents, chunk_list_idx = [], 0

        if ent_type == 'anatomy':
            location = True
        else:
            location = False

        while chunk_list_idx < len(entity_chunks):
            tagged_chunk, raw_chunk = entity_chunks[chunk_list_idx], raw_chunks[chunk_list_idx]
            chunk_idx = chunk_idx_dict[tagged_chunk]

            is_previous = self.check_previous(chunk_idx)
            is_negated = self.check_negation(chunk_idx)

            possible_modifiers = []
            for token in self.__clause_doc:
                if token.text in raw_chunk:
                    possible_modifiers = possible_modifiers + self.get_modifiers(token, location)

            is_normal, mod_descriptors = self.map_modifiers(list(set(possible_modifiers)))
            # print("IN PARSE_ENTITY: Possible modifiers are", possible_modifiers,
            # "selected descriptors are", [descr.name for descr in mod_descriptors])

            if not (ent_type == 'anatomy' and len(mod_descriptors) == 0):
                if ent_type == 'anatomy':

                    potential_location = self.__full_chunks_dicts[1][raw_chunk].text
                    refined_words = []
                    for word in potential_location.split():
                        if word not in ["the", "a"]:
                            if self.map_to_radlex(word, self.__location_list)[0] is not None:
                                refined_words.append(word)
                            elif self.map_to_radlex(word, self.__anatomy_list)[0] is not None:
                                refined_words.append(word)
                    anat_loc = " ".join(refined_words)

                    ent_name = raw_chunk + " (" + ", ".join(
                        [descriptor.describe() for descriptor in mod_descriptors]) + ")"
                    location = [anat_loc]  # self.get_location(raw_chunk)
                else:
                    ent_name = raw_chunk
                    location = self.get_location(raw_chunk)
                if ent_type == 'change':
                    is_negated = self.check_change_negation(raw_chunk)

                entity_ents.append(ExtractedEntity(name=ent_name, ent_type=ent_type,
                                                   location=", ".join(location),
                                                   description=mod_descriptors,
                                                   is_previous=is_previous,
                                                   is_negated=is_negated, is_normal=is_normal))
            chunk_list_idx += 1

        return entity_ents

    def parse_indices(self):
        entity_lsts = [self.parse_entity(i, self.__keys[i]) for i in range(len(self.__keys))]
        return [ent for lst in entity_lsts for ent in lst]

    '''HEDGING CODE'''

    def apply_hedges(self):
        hedges = [phrase for phrase in self.__hedge_list if phrase in self.__clause]

        doc = nlp(self.__clause)
        if len(hedges) > 0:

            for entity in self.__all_entities:
                ent_hedges = []

                # Assume the last word in the entity name is the fundamental one
                ent_tokens = [token for token in doc if token.text == entity.name.split()[-1]]

                # If you format naming correctly (NO parentheses, should always be a match to the text), you shouldn't need this caveat
                if len(ent_tokens) > 0:
                    ent_token = ent_tokens[0]

                    for hedge in hedges:
                        anc_hedges = list(set(
                            [hedge for anc in ent_token.ancestors if anc.text in hedge] + [hedge for child in
                                                                                           ent_token.children if
                                                                                           child.text in hedge]))
                        for anc_hedge in anc_hedges:
                            if anc_hedge not in self.__post_hedges:
                                if self.__clause.index(anc_hedge) < self.__clause.index(ent_token.text):
                                    ent_hedges.append(anc_hedge)
                            else:
                                ent_hedges.append(anc_hedge)  # because post hedges often can also be prior

                    # 2nd Layer Search for hedge among children
                    if len(ent_hedges) == 0:
                        # print("2nd layer search")
                        for hedge in hedges:
                            child_hedges = [hedge for child in ent_token.children if child.text in hedge]
                            # print("Child hedges:", child_hedges)
                            for child_hedge in child_hedges:
                                if self.__clause.index(child_hedge) < self.__clause.index(ent_token.text):
                                    ent_hedges.append(child_hedge)

                    ent_hedges = list(set(ent_hedges))
                    if len(ent_hedges) > 0:
                        entity.set_hedging(self.remove_submatches(ent_hedges))

                    for descriptor in entity.description:
                        descr_token = [token for token in doc if token.text == descriptor.name][0]
                        descr_hedges = [anc.text for anc in descr_token.ancestors if anc.text in hedges] + [child.text
                                                                                                            for child in
                                                                                                            descr_token.children
                                                                                                            if
                                                                                                            child.text in hedges]
                        if len(descr_hedges) > 0:
                            descriptor.set_hedging(self.remove_submatches(descr_hedges))
        return None

    def remove_redundant_anatomy(self, df):
        findings_to_remove, idxs_to_check, findings_to_check = [], [], []

        for i in range(len(df)):
            if df.finding_types.loc[i] == 'anatomy':  # or df.finding_types.loc[i] == 'visual_disease':
                idxs_to_check.append(i)
                findings_to_check.append(df.findings[i])

        for k in range(len(findings_to_check)):
            finding = findings_to_check[k]
            for j in range(len(df)):
                if j not in idxs_to_check:
                    ent = df.iloc[j]
                    slim_finding = finding.split("(")[0].strip()  # this counts on the parentheses being at the end
                    if ent.locations in slim_finding or slim_finding in ent.locations:
                        findings_to_remove.append(finding)

        for finding in findings_to_remove:
            df = df[df.findings != finding]

        return df

    def check_lost(self):
        num_chunks = np.sum([len(chunk_list) for chunk_list in self.__chunks])
        if num_chunks > len(self.__all_entities):
            ent_adjs = [adj for entity in self.__all_entities for adj in entity.describe().split(",")]
            ent_adjs = ent_adjs + [adj for entity in self.__all_entities for adj in entity.location.split(",")]
            ent_adjs = list(set([word.strip("\'") for ent in ent_adjs for word in ent.split(" ")]))

            adjs = [token for token in nlp(self.__clause) if token.pos_ == 'ADJ']
            missing_adjs = []
            for adj in adjs:
                if adj.text not in ent_adjs:
                    missing_adjs.append(adj)

            # print(ent_adjs, missing_adjs, adjs)
            if len(missing_adjs) > 0:
                return True, True
            else:
                return True, False
        else:
            return False, False

    def grab_bag(self):
        # print("IN GRAB BAG")
        doc = nlp(self.__clause)
        root_verb = [token for token in doc if token.dep_ == 'ROOT']
        if len(root_verb) == 0:
            return None
        else:
            root_verb = root_verb[0]
            root_adjs = [child.text for child in root_verb.children if child.pos_ == 'ADJ']
            relations = [token.text for token in doc if
                         root_verb.text in [anc.text for anc in token.ancestors] and token.pos_ == 'NOUN']

            adj_string = ", ".join(root_adjs)
            new_outputs = []

            for relation in relations:
                new_clause = "the " + adj_string + " " + relation
                sub_extractor = ReportExtractor(clause=new_clause, neg_rules=self.__neg_rules,
                                                prev_rules=self.__prev_rules,

                                                vis_dis_list=self.__vis_dis_list, anatomy_list=self.__anatomy_list,
                                                procedure_list=self.__procedure_list, device_list=self.__device_list,

                                                locations_list=self.__location_list,
                                                descriptor_list=self.__descriptor_list,
                                                normal_list=self.__normal_list,

                                                hedge_list=self.__hedge_list, post_hedge_list=self.__post_hedges,
                                                hedge_dict=self.__hedge_dict, hedge_scores=self.__hedge_scores,
                                                grab=False)
                new_outputs.append(sub_extractor.run_extractor())

            if len(new_outputs) is not 0:
                return pd.concat(new_outputs)
            else:
                return None

    def remove_nonsense_locations(self, locations):
        new_locs = []
        for location in locations:
            doc = nlp(location)
            pos = [token.pos_ for token in doc]
            if 'NOUN' in pos:
                new_locs.append(location)
            elif 'ADJ' in pos:
                new_locs.append(location)
            else:
                new_locs.append('')
        return new_locs

    def clean_output(self):
        chunks_lost, adjs_lost = self.check_lost()
        addl_df = None
        if chunks_lost and adjs_lost and self.__grab:
            addl_df = self.grab_bag()

        findings, finding_types, certainties, statuses, descriptors, locations, changes = [], [], [], [], [], [], []

        for entity in self.__all_entities:
            # finding, finding_type, ceratinty, status, descriptors, locations, is_changed
            findings.append(entity.name)
            finding_types.append(entity.ent_type)
            certainties.append(entity.set_hedge_level(self.__hedge_dict, self.__hedge_scores))
            descriptors.append(entity.describe())
            locations.append(entity.location)
            changes.append(entity.is_changed(self.__change_list))

            if entity.negated and entity.previous:
                statuses.append("negated, previous")
            elif entity.negated:
                statuses.append("negated")
            elif entity.previous:
                statuses.append("previous")
            else:
                statuses.append("current")

        locations = self.remove_nonsense_locations(locations)

        # print(len(findings), len(finding_types), len(certainties), len(statuses), len(descriptors), len(locations), len(changes))
        output_df = pd.DataFrame([findings, finding_types, certainties, statuses, descriptors, locations, changes],
                                 index=['findings', 'finding_types', 'certainties', 'statuses', 'descriptors',
                                        'locations', 'changed']).T
        if addl_df is not None:
            addl_df.index = range(len(addl_df))
            addl_copy = addl_df.copy()
            for i in range(len(addl_df)):
                finding = addl_df.findings[i]
                if finding in output_df.findings.tolist():
                    addl_copy = addl_copy.drop(i)
            addl_df = addl_copy
            if addl_copy is not None:
                output_df = pd.concat([output_df, addl_copy])

        output_df.index = range(len(output_df))

        # print("CONCAT DF: ", output_df)
        if self.__grab:
            output_df = self.remove_redundant_anatomy(output_df)

        return output_df

