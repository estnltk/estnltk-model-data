#
#    Functions for converting UD_Estonian-EDT corpus that has semantic role annotations
#    into EstNLTK JSON format, and, optionally, splitting document Text objects into 
#    sentence Text objects. 
#

import re
import os, os.path

from tqdm import tqdm

from estnltk.converters import text_to_json
from estnltk.converters import json_to_text
from estnltk_core.layer_operations import split_by_sentences
from estnltk.converters.conll.conll_importer import conll_to_texts_list
from estnltk.taggers.standard.syntax.syntax_dependency_retagger import SyntaxDependencyRetagger


def convert_conllu_into_estnltk_json(conllu_file, output_dir, output_jl_file, split_into_sentences=True, 
                                                  syntax_layer='conll_syntax', sentences_layer='sentences'):
    # Separate documents in the file and load as Text objects
    print(f'Loading documents in {conllu_file!r} as Text objects ...')
    texts = conll_to_texts_list( conllu_file, syntax_layer=syntax_layer )
    dep_retagger = SyntaxDependencyRetagger(syntax_layer=syntax_layer)
    new_texts = []
    for text in tqdm( texts, ascii=True ):
        if split_into_sentences:
            sent_id = 0
            for sent_text in split_by_sentences(text, 
                                                layers_to_keep=text.layers, 
                                                trim_overlapping=False, 
                                                input_sentences_layer=sentences_layer): 
                # set metadata
                sent_text.meta = text.meta.copy()
                sent_text.meta['sentence_id'] = sent_id
                # dependency relations need to be corrected within sentences
                dep_retagger.retag( sent_text )
                sent_id += 1
                new_texts.append( sent_text )
        else:
            new_texts.append(text)
    print(f'Saving Text objects into {output_dir!r} ...')
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, output_jl_file), mode='w', encoding='utf-8') as out_f:
        for new_text in tqdm( new_texts, ascii=True ):
            out_f.write( text_to_json(new_text) )
            out_f.write( '\n' )


def load_estnltk_texts_from_jsonlines( jsonlines_file ):
    print(f'Loading Text objects from {jsonlines_file!r} ...')
    texts = []
    with open(jsonlines_file, mode='r', encoding='utf-8') as in_f:
        for line in tqdm( in_f, ascii=True ):
            texts.append( json_to_text(line) )
    return texts

