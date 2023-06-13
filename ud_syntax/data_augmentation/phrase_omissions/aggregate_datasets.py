#
#  Aggregates train/*.conllu and dev/*.conllu files into 
#  cut_sentences_train.conllu and cut_sentences_dev.conllu 
#  files 
#

from collections import defaultdict
import os, os.path


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
            #print(dir_root, fname)
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
                    if empty_lines_in_row != 3:
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
    else:
        print('No suitable conllu files found.')