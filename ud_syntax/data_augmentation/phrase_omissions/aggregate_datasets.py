#
#  Aggregates train/*.conllu and dev/*.conllu files into 
#  cut_sentences_train.conllu and cut_sentences_dev.conllu 
#  files 
#

from collections import defaultdict
import os, os.path

# Validate that the result is a valid conllu file 
# that stanza can load (requires stanza package)
validate_conllu = False

cut_file_suffix = '_cut.conllu'
dirs = ['Train', 'Dev']

for d in dirs:
    assert os.path.exists(d) and \
           os.path.isdir(d), f'(!) Invalid or missing directory {d!r}'
    dir_name = os.path.basename( d )
    dir_conllu_content = []
    token_count = 0
    sentence_count = 0
    sent_ids = defaultdict(int)
    for fname in os.listdir( d ):
        if fname.endswith( cut_file_suffix ):
            with open(os.path.join(d, fname), 'r', encoding='utf-8') as in_f:
                empty_lines_in_row = 0
                for line in in_f:
                    line_clean = line.strip()
                    if len(line_clean) > 0:
                        if line_clean[0].isnumeric():
                            if line_clean.startswith('1\t'):
                                sentence_count += 1
                            token_count += 1
                        elif line_clean.startswith('# sent_id = '):
                            sent_ids[line_clean] += 1
                        empty_lines_in_row = 0
                    else:
                        empty_lines_in_row += 1
                    if empty_lines_in_row != 2:
                        dir_conllu_content.append(line)
    if dir_conllu_content:
        print('Total token    count:', token_count)
        print('Total sentence count:', sentence_count)
        print('Unique sentence  ids:', len(sent_ids))
        out_fname = f'cut_sentences_{dir_name.lower()}.conllu'
        with open(out_fname, 'w', encoding='utf-8') as out_f:
            for line in dir_conllu_content:
                out_f.write( line )
        print(f' ->  {out_fname}')
        if validate_conllu:
            # Import stanza data loading functions
            from stanza.utils.conll import CoNLL
            from stanza.models.common.doc import Document
            from stanza.utils.conll18_ud_eval import load_conllu_file
            # 1) Test data loading for training
            train_data, _ = CoNLL.conll2dict(input_file=out_fname)
            train_doc = Document(train_data)
            print( f'{out_fname!r} conllu loading test #1: OK' )
            # 2) Test data loading for evaluation
            treebank_type = {}
            treebank_type['no_gapping'] = 0
            treebank_type['no_shared_parents_in_coordination'] = 0
            treebank_type['no_shared_dependents_in_coordination'] = 0
            treebank_type['no_control'] = 0
            treebank_type['no_external_arguments_of_relative_clauses'] = 0
            treebank_type['no_case_info'] = 0
            treebank_type['no_empty_nodes'] = False
            treebank_type['multiple_roots_okay'] = False
            eval_doc = load_conllu_file(out_fname, treebank_type)
            print( f'{out_fname!r} conllu loading test #2: OK' )
    else:
        print('No suitable conllu files found.')