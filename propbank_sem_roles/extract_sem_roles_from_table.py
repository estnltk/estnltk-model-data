#
#  Extracts semantic roles lexicon from manually crafted semantic roles table (created in the 
#  project EKTB75). The table describes verbs' senses, corresponding semantic roles and 
#  morphosyntactic properties of semantic roles, allowing to map semantic roles to syntactic 
#  and morphological features. 
#  This resulting lexicon is used by PropBankPreannotator on tagging semantic roles. 
#  
#  The input table must given as a .tsv file that has columns: "verb", "tüüpverb", "sagedus korpuses", 
#  "Arg0", "Arg0 süntaks", "Arg1", "Arg1 süntaks", "Arg2", "Arg2 süntaks", "Arg3", "Arg3 süntaks", 
#  "Arg4", "Arg4 süntaks", "Arg5", "ArgM", "ArgM-aeg", "ArgM-viis", "ArgM-koht", "Arg_xarg"
#
#  As a result, the script creates two files:
#  * 'propbank_frames.jl' -- a lexicon file where each line contains a JSON object describing 
#     a specific verb sense along with all of its semantic roles and roles' morphosyntactic 
#     properties; 
#  * 'propbank_frames_pretty.json' -- a pretty-printed version of 'propbank_frames.jl'
#    (technically not valid json, only for human inspection)
#
#  Requirement:
#  * estnltk version 1.7.3+
#

import re
import os, os.path
import sys
import csv
import json

from estnltk.taggers.system.rule_taggers.regex_library.string_list import StringList

if __name__ == '__main__':
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        print('Extracting sem role information from: ', input_file)
        extracted_entries = []
        # Try to extract creation date from the lexicon name
        lexicon_date = None
        lexicon_date_match = re.search(r'(\d\d\d\d-\d\d-\d\d)', input_file)
        if lexicon_date_match:
            lexicon_date = lexicon_date_match.group(1)
        with open(input_file, 'r', encoding='utf-8', newline='') as tsvfile:
            fmtparams = {'delimiter': '\t'}
            fle_reader = csv.reader(tsvfile, dialect='excel-tab', **fmtparams)
            header = next(fle_reader)
            print(header)
            verb_class = ''
            last_verb = ''
            for row in fle_reader:
                analysis_dict = {}
                assert len(row) == len(header), \
                    '(!) Unexpected number of elements in a row: {!r}'.format(row)
                all_fields_empty = True
                adds_to_previous_entry = False
                has_arg_syntax_info = False
                has_argm_info = False
                has_argx_info = False
                for kid, key in enumerate(header):
                    value = row[kid]
                    analysis_dict[key] = value
                    if key == 'verb' and len(value) > 0:
                        if value[:3].isupper():
                            # Fetch general verb type, if available
                            if value not in ['ANDRIELA', 'KAILI'] and not value.startswith(('KUULIS ÖELDAVAT', 'NB! on näha')):
                                if value.startswith('KERTU ÜLEKANDED'):
                                    value = '----'
                                if value.startswith('TAJUVERBID.'):
                                    value = 'TAJUVERBID'
                                verb_class = value
                        else:
                            # Fetch verb name, sense and any extra information
                            verb_name_pat = re.match(r'^(?P<verb>\S+ma)((_|\s+)(?P<sense>\d+))?(?P<extra>$| .+$)', value)
                            if verb_name_pat:
                                if verb_name_pat.group('verb') is not None:
                                    analysis_dict['_verb'] = verb_name_pat.group('verb')
                                if verb_name_pat.group('sense') is not None:
                                    analysis_dict['_verb_sense_id'] = int(verb_name_pat.group('sense'))
                                if verb_name_pat.group('extra') is not None:
                                    if len( verb_name_pat.group('extra').strip() ) > 0:
                                        analysis_dict['_verb_extra'] = verb_name_pat.group('extra').strip()
                                        if (verb_name_pat.group('sense') is None) and (analysis_dict['_verb_extra']).isnumeric():
                                            # (!) Correct verb sense number with verb_extra
                                            analysis_dict['_verb_sense_id'] = int(analysis_dict['_verb_extra'])
                                            analysis_dict['_verb_extra'] = ''
                                if len(last_verb) > 0 and last_verb == analysis_dict.get('_verb', ''):
                                    adds_to_previous_entry = True
                                last_verb = analysis_dict.get('_verb', '')
                    if key.endswith('süntaks') and len(value) > 0:
                        has_arg_syntax_info = True
                    elif key.endswith('süntaks') and len(value) == 0:
                        # If 'ArgX süntaks' does not have any value, 
                        # try to get the value from 'ArgX'
                        arg_number = key[:4]
                        assert arg_number.startswith('Arg')
                        for kid2, key2 in enumerate(header):
                            if key2 == arg_number and kid2 != kid and len(row[kid2]) > 0:
                                # Take value from the ArgX field:
                                # 'Arg0 süntaks' -> 'Arg0'
                                # 'Arg1 süntaks' -> 'Arg1'
                                # 'Arg2 süntaks' -> 'Arg2'
                                #  ...
                                analysis_dict[key] = f'{row[kid2]} (from {key2})'
                                break
                    if key.startswith('ArgM') and len(value) > 0:
                        has_argm_info = True
                    if key.startswith('Arg_xarg') and len(value) > 0:
                        has_argx_info = True
                    if len(value) > 0:
                        all_fields_empty = False
                # Collect entry
                if len(analysis_dict.get('_verb', '')) > 0 and \
                   (has_arg_syntax_info or has_argm_info or has_argx_info):
                    extracted_entries.append( analysis_dict )
                
                '''
                if (has_arg_syntax_info or has_argm_info or has_argx_info):
                    print(analysis_dict.get('_verb', ''), '|', 
                          analysis_dict.get('_verb_sense_id', ''), '|',
                          analysis_dict.get('_verb_extra', ''), '|', 
                          adds_to_previous_entry, '|', 
                          verb_class, '|', 
                          'Arg0:', analysis_dict.get('Arg0 süntaks', ''), '|', 
                          'Arg1:', analysis_dict.get('Arg1 süntaks', ''), '|', 
                          'Arg2:', analysis_dict.get('Arg2 süntaks', ''), '|', 
                          'Arg3:', analysis_dict.get('Arg3 süntaks', ''), '|', 
                          'Arg4:', analysis_dict.get('Arg4 süntaks', ''), '|' ,
                          'ArgM:', analysis_dict.get('ArgM', ''), '|' ,
                          'ArgM-aeg:', analysis_dict.get('ArgM-aeg', ''), '|' ,
                          'ArgM-koht:', analysis_dict.get('ArgM-koht', ''), '|' ,
                          'ArgM-viis:', analysis_dict.get('ArgM-viis', ''), '|' ,
                          'Arg_xarg:', analysis_dict.get('Arg_xarg', ''))
                '''
                
                if len(verb_class) > 0 and not all_fields_empty:
                    # 'PROTSESS'  #191
                    # 'KÕNEAKTID'  #39
                    # 'TAJUMISE KAUSATIIVID'  #18
                    # 'LIIKUMINE'  #12
                    # 'TAJUVERBID'  #11
                    if verb_class.endswith('ID'):
                        verb_class = verb_class[:-2]
                    analysis_dict['_verb_class'] = verb_class
                
                #
                # (!) ühendverbid: "compound:prt" jäävad välja;
                #
        
        # 
        #   Display statistics about collected entries
        #
        print()
        print('(!) Collected entries (stats): ')
        for field in ['_verb_class', 'Arg0 süntaks', 'Arg1 süntaks', 'Arg2 süntaks', 'Arg3 süntaks', 'Arg4 süntaks', 'Arg5', 'ArgM', 'ArgM-aeg', 'ArgM-koht', 'ArgM-viis', 'Arg_xarg']:
            print('='*35)
            print(f'  {field}')
            print('='*35)
            counts = {}
            for entry in extracted_entries:
                value = entry.get(field, 'N/A')
                if value not in counts:
                    counts[value] = 1
                else:
                    counts[value] += 1
            print(f' Values total: {len(counts.keys())}')
            for val in sorted(counts.keys(), key=counts.get, reverse=True):
                print(f'    {val!r}  #{counts.get(val)}')
            print()
        
        #
        # https://github.com/UniversalDependencies/UD_Estonian-EDT/blob/master/stats.xml
        #
        all_deprels_pat = StringList(["acl", "acl:relcl", "advcl", "advmod", "amod", "appos", 
            "aux", "case", "cc", "cc:preconj", "ccomp", "compound", "compound:prt", "conj", "cop", 
            "csubj", "csubj:cop", "dep", "det", "discourse", "fixed", "flat", "flat:foreign", 
            "goeswith", "list", "mark", "nmod", "nsubj", "nsubj:cop", "nummod", "obj", "obl", 
            "orphan", "parataxis", "punct", "root", "vocative", "xcomp"], 
            description='All deprel values from UD_Estonian-EDT (v2.13).',
            ignore_case=True)
        all_cases_pat = StringList(["Abe", "Abl", "Ade", "All", "Com", "Ela", "Ess", "Gen", 
            "Ill", "Ine", "Nom", "Par", "Ter", "Tra"],
            description='All case values from UD_Estonian-EDT (v2.13).',
            ignore_case=True)
        
        def collect_case_markers(_extracted_entries):
            #
            #  Collect information about case-marking elements
            #     (prepositions, postpositions etc)
            # 'obl_Ine//obl_Ade/obl_Case:ümber/vahel', 'obl_Add/ob_Ill/obl_Case:poole/suunas',
            # 'obl_All/obl_Ill/obl_Ine/obl_Case:poole', 'obl_Ade/obl_Ine/obl_Case:ees/juures'
            #     or 
            # 'obl_Add/obl_Gen->case kätte/obl_Gen->case keskele/obl_Gen->case juurde', 
            # 'obl_Ill/obl_Gen->case poole', 'obl_Gen->case sekka/obl_com->case kokku'
            # 
            all_case_markers = set()
            deprels_pat = all_deprels_pat.compile()
            cases_pat   = all_cases_pat.compile()
            for entry in _extracted_entries:
                for field in ['Arg0 süntaks', 'Arg1 süntaks', 'Arg2 süntaks', 'Arg3 süntaks', 'Arg4 süntaks', 'Arg5', 'ArgM', 'ArgM-aeg', 'ArgM-koht', 'ArgM-viis', 'Arg_xarg']:
                    value = entry.get(field, 'N/A')
                    value = value.lower()
                    # example:  _Case:poole/juurde,  _Case:asemele/alla
                    case_info_match_1 = re.search(r'_case:(\S+)', value)
                    if case_info_match_1:
                        lemmas_str = case_info_match_1.group(1)
                        lemmas = re.split(r'/|_', lemmas_str)
                        for lemma in lemmas:
                            # break when stumbling upon deprels and morph cases
                            if deprels_pat.fullmatch(lemma):
                                break
                            if cases_pat.fullmatch(lemma):
                                break
                            all_case_markers.add(lemma)
                    # example:  ->case kallale, juurde, kätte, alla, taha
                    case_info_match_2 = re.search(r'->\s*case\s*:?\s*([a-zöäüõšž,]+\s*)+', value)
                    if case_info_match_2:
                        lemmas_str = case_info_match_2.group(1)
                        lemmas = re.split(r',|_', lemmas_str)
                        for lemma in lemmas:
                            lemma = lemma.strip()
                            # break when stumbling upon deprels and morph cases
                            if deprels_pat.fullmatch(lemma):
                                break
                            if cases_pat.fullmatch(lemma):
                                break
                            all_case_markers.add(lemma)
            return all_case_markers

        case_markers = collect_case_markers(extracted_entries)
        print()
        print(f'Case-marking words ({len(case_markers)}): ', sorted(list(case_markers)))
        print()
        all_case_markers_pat = StringList(list(case_markers),
            description='Case marker words extracted from the input TSV file.',
            ignore_case=True)

        # 
        #   Parse values from collected entries
        #
        def parse_arg_values(arg_name: str, arg_value: str):
            arg_value = re.sub(r'//+', '/', arg_value)
            arg_value = re.sub(r'\s+\(from Arg[0-9]\)', '', arg_value)
            if arg_name.startswith('Arg0'):
                #
                # Arg 0
                #
                if re.fullmatch(f'({all_deprels_pat})(/{all_deprels_pat})*', arg_value):
                    return {'name': 'Arg0', 
                            'variants': [ \
                                {'feats': [f'deprel={deprel}']} for deprel in arg_value.split('/') ] \
                            }
                else:
                    # Arg 0 not available !!!
                    return {}
            else:
                #
                # Arg 1, 2, 3, ...
                #
                arg_name_clean = arg_name.replace(' süntaks', '')
                collected_variants = []
                i = 0
                while i < len(arg_value):
                    snippet = arg_value[i:]
                    # Try all patterns from the location
                    #
                    # 1) deprel-s without case information, e.g.
                    # 'obj', 'nsubj', 'obj/ccomp', 'ccomp/obj', 'nsubj/csubj', 'xcomp'
                    #
                    only_deprel_match = re.match(f'({all_deprels_pat})', snippet)
                    #
                    # 2) deprel-s with case information, e.g.
                    # 'obj/obl_Ade', 'obl_Abl', 'obl_Com', 'obl_Ela/obl_Abl'
                    #
                    deprel_case_match = re.match(f'({all_deprels_pat})_({all_cases_pat})', snippet)
                    #
                    # 3) deprel-s with case-marking-element information, e.g.
                    # 'obl_Ine//obl_Ade/obl_Case:ümber/vahel', 'obl_Add/ob_Ill/obl_Case:poole/suunas',
                    # 'obl_All/obl_Ill/obl_Ine/obl_Case:poole', 'obl_Ade/obl_Ine/obl_Case:ees/juures'
                    #
                    deprel_case_with_markers = re.match(f'({all_deprels_pat})_[Cc]ase:({all_case_markers_pat}(/{all_case_markers_pat})*)', snippet)
                    #
                    # 4) deprel-s with case information and case-marking-element information, e.g.
                    # 'obl_Add/obl_Gen->case kätte/obl_Gen->case keskele/obl_Gen->case juurde', 
                    # 'obl_Ill/obl_Gen->case poole', 'obl_Gen->case sekka/obl_com->case kokku'
                    #
                    deprel_case_and_casemarker = re.match(fr'({all_deprels_pat})_({all_cases_pat})\s*->\s*[Cc]ase\s*([a-zöäüõšž,]+\s*)+', snippet)
                    match_collected = False
                    if deprel_case_and_casemarker:
                        deprel, case, casemarkers_str = deprel_case_and_casemarker.group(1), \
                                                        deprel_case_and_casemarker.group(2), \
                                                        deprel_case_and_casemarker.group(3)
                        casemarkers = re.split(',|;', casemarkers_str)
                        for casemarker in casemarkers:
                            casemarker = casemarker.strip()
                            if len(casemarker) > 0:
                                feats = {'feats': [f'deprel={deprel.lower()}', 
                                                   f'case={case.title()}', 
                                                   f'casemarker={casemarker}']}
                                collected_variants.append(feats)
                        i += len(deprel_case_and_casemarker.group(0))
                        match_collected = True
                    elif deprel_case_with_markers:
                        deprel, casemarkers_str = deprel_case_with_markers.group(1), deprel_case_with_markers.group(2)
                        casemarkers = casemarkers_str.split('/')
                        for casemarker in casemarkers:
                            feats = {'feats': [f'deprel={deprel.lower()}', f'casemarker={casemarker}']}
                            collected_variants.append(feats)
                        i += len(deprel_case_with_markers.group(0))
                        match_collected = True
                    elif deprel_case_match:
                        deprel, case = deprel_case_match.group(1), deprel_case_match.group(2)
                        feats = {'feats': [f'deprel={deprel.lower()}', f'case={case.title()}']}
                        collected_variants.append(feats)
                        i += len(deprel_case_match.group(0))
                        match_collected = True
                    elif only_deprel_match:
                        feats = {'feats': [f'deprel={(only_deprel_match.group(1)).lower()}']}
                        collected_variants.append(feats)
                        i += len(only_deprel_match.group(0))
                        match_collected = True
                    if not match_collected:
                        break
                    else:
                        # Skip separating '/'
                        while i < len(arg_value) and arg_value[i] == '/':
                            i += 1
                # Check if the whole string was matched
                if i >= len(arg_value) and collected_variants:
                    assert collected_variants
                    return {'name': arg_name_clean, 'variants': collected_variants}
            return {}

        total_values = 0
        parsed_values = 0
        formalized_entries = []
        seen_senses = set()
        duplicates_discarded = 0
        last_seen_sense = ''
        for entry in extracted_entries:
            parsed_arguments = []
            parsing_successes = []
            for field in ['Arg0 süntaks', 'Arg1 süntaks', 'Arg2 süntaks', 'Arg3 süntaks', 'Arg4 süntaks', 'Arg5', 'ArgM', 'ArgM-aeg', 'ArgM-koht', 'ArgM-viis', 'Arg_xarg']:
                value = entry.get(field, 'N/A')
                if value != 'N/A' and len(value) > 0:
                    total_values += 1
                parsed_successfully = False
                parsed_val = parse_arg_values(field, value)
                if parsed_val != {}:
                    parsed_values += 1
                if parsed_val != {}:
                    field_name_clean = field.replace(' süntaks', '')
                    if field != field_name_clean:
                        field_desc = entry.get(field_name_clean, '')
                        if len(field_desc) > 0:
                            # Apply ad-hoc descriptions to parsed_val:
                            if field_desc.startswith('millisena: nad on esitatud väga abitus seisus;'):
                                field_desc = 'millisena'
                            elif field_desc.startswith('koht. Kui on kaks kohatähendusega eraldi Arg'):
                                field_desc = 'koht'
                            parsed_val['description'] = field_desc
                            # Reorder fields
                            assert len(parsed_val.keys()) == 3
                            parsed_val = \
                                { field: parsed_val[field] for field in ['name', 'description', 'variants'] }
                    parsed_arguments.append( parsed_val )
                    parsed_successfully = True
                if value != 'N/A' and len(value) > 0:
                    parsing_successes.append( parsed_successfully )
                if parsed_val != {} and parsed_val['name'] != 'Arg0':
                    print(entry.get('_verb', ''), '|', 
                          entry.get('_verb_sense_id', ''), '|',
                          entry.get('_verb_extra', ''), '|', 
                          parsed_val)
            if parsed_arguments and len( entry.get('_verb', '') )>0:
                full_sense_id = f"{entry.get('_verb', '')}_{entry.get('_verb_sense_id', '1')}"
                if full_sense_id not in seen_senses:
                    # formalize full entry
                    full_entry = { 'sense_id': full_sense_id, 
                                   'lemma': entry.get('_verb', ''), 
                                   'class': entry.get('_verb_class', ''),
                                   'description': entry.get('_verb_extra', ''), 
                                   'complete': all(parsing_successes), 
                                   'arguments': parsed_arguments }
                    formalized_entries.append(full_entry)
                    last_seen_sense = entry.get('_verb_sense_id', '1')
                else:
                    print()
                    print('(!) Duplicate sense_id: ', full_sense_id)
                    print()
                    duplicates_discarded += 1
                seen_senses.add(full_sense_id)
        
        print()
        print(f' Parsing success:  {parsed_values} / {total_values}  ({((100.0*parsed_values)/total_values):.2f}%)')
        if duplicates_discarded > 0:
            print(f'   Duplicate senses discarded:  {duplicates_discarded}')
            print()
        # Write formalized entries into json
        if formalized_entries:
            print('  --> "propbank_frames_pretty.json"')
            with open('propbank_frames_pretty.json', 'w', encoding='utf-8') as out_f:
                if lexicon_date is not None:
                    out_f.write(f'##  PropBank preliminary lexicon, version {lexicon_date}. Based on resources of the project EKTB75')
                    out_f.write('\n')
                for entry in formalized_entries:
                    json_string = json.dumps( entry, indent = 3, ensure_ascii=False )
                    out_f.write(json_string)
                    out_f.write('\n')
            print('  --> "propbank_frames.jl"')
            with open('propbank_frames.jl', 'w', encoding='utf-8') as out_f2:
                if lexicon_date is not None:
                    out_f2.write(f'##  PropBank preliminary lexicon, version {lexicon_date}. Based on resources of the project EKTB75')
                    out_f2.write('\n')
                for entry in formalized_entries:
                    json_string = json.dumps( entry, ensure_ascii=False )
                    out_f2.write(json_string)
                    out_f2.write('\n')
    else:
        raise ValueError('(!) Missing input argument: name of a .tsv file containing manually crafted semantic role descriptions, e.g. "verbid_semrollidega_2024-10-28.tsv"')
