import configparser
import os, os.path
import ast

from estnltk.storage.postgres import PostgresStorage


def load_configuration(config_file):
    config = configparser.ConfigParser()

    file_name = os.path.abspath(os.path.expanduser(os.path.expandvars(str(config_file))))

    if not os.path.exists(file_name):
        raise ValueError("File {file} does not exist".format(file=str(config_file)))

    if len(config.read(file_name)) != 1:
        raise ValueError("File {file} is not accessible or is not in valid INI format".format(file=config_file))

    for option in ["host", "port", "database", "username", "password", "role", "schema", "collection"]:
        if not config.has_option('source_database', option):
            prelude = "Error in file {}\n".format(file_name) if len(file_name) > 0 else ""
            raise ValueError(
                "{prelude}Missing option {option} in the section [{section}]".format(
                    prelude=prelude, option=option, section='source_database'
                )
            )

    config.read(file_name)
    
    return config


def connect_to_database(config):

    dbname = config['source_database']['database']
    user = config['source_database']['username']
    password = config['source_database']['password']
    host = config['source_database']['host']
    port = config['source_database']['port']
    role = config['source_database']['role']
    schema = config['source_database']['schema']
    collection = config['source_database']['collection']


    storage = PostgresStorage(host=host,
                              port=int(port),
                              dbname=dbname,
                              user=user,
                              password=password,
                              schema=schema,
                              role=role,
                              temporary=False)
    return storage

def load_local_configuration(config_file):
    
    config = configparser.ConfigParser()

    file_name = os.path.abspath(os.path.expanduser(os.path.expandvars(str(config_file))))

    if not os.path.exists(file_name):
        raise ValueError("File {file} does not exist".format(file=str(config_file)))

    if len(config.read(file_name)) != 1:
        raise ValueError("File {file} is not accessible or is not in valid INI format".format(file=config_file))

    for option in ["sqlite_file"]:
        if not config.has_option('local_database', option):
            prelude = "Error in file {}\n".format(file_name) if len(file_name) > 0 else ""
            raise ValueError(
                "{prelude}Missing option {option} in the section [{section}]".format(
                    prelude=prelude, option=option, section='local_database'
                )
            )

    config.read(file_name)
    
    return config


def load_term_subpopulations(subpop_dir='config/subpopulations', remove_substr='_suffix_words.txt'):
    subpop_terms = {}
    for fname in os.listdir(subpop_dir):
        with open(os.path.join(subpop_dir, fname), 'r', encoding='UTF-8') as in_f:
            if remove_substr is not None and len(remove_substr)>0:
                fname = fname.replace(remove_substr, '')
            subpop_terms[fname] = set()
            for line in in_f:
                if len(line.strip()) > 0:
                    subpop_terms[fname].add(line.strip())
    return subpop_terms


def count_terms_by_subpopulations(sampler, subpopulations_dir='config/subpopulations'):
    raw_term_counts = sampler.get_attribute_counts()
    term_subpopulations = load_term_subpopulations(subpopulations_dir)
    subpopulation_counts = { k: 0 for k in term_subpopulations.keys() }
    for (term, term_count) in raw_term_counts:
        for subpop in term_subpopulations.keys():
            if term in term_subpopulations[subpop]:
                subpopulation_counts[subpop] += term_count
                break
    return subpopulation_counts


class DuplicatesChecker:
    '''Validates that recall_set items are in correct format and do not contain duplicates.'''

    def __init__(self, validate=True):
        self.seen_text_annotations=dict()
        self.validate=validate

    def validate_entry(self, text, span):
        assert isinstance(text, str), f'(!) text is not string, but {type(text)}.'
        assert isinstance(span, str), f'(!) span is not string, but {type(span)}.'
        span = ast.literal_eval( span )
        assert 'start' in span,  f'(!) {span}: span is missing "start" attribute'
        assert 'end' in span,    f'(!) {span}: span is missing "end" attribute'
        assert 'labels' in span, f'(!) {span}: span is missing "labels" attribute'
        assert 'text' in span,   f'(!) {span}: span is missing "text" attribute'
        assert isinstance(span['labels'], list), f'(!) {span}: span "labels" is not a list'
        ner_phrase = text[span['start']:span['end']]
        if len(span['text']) > 0 and ner_phrase != span['text']:
            raise Exception(f'(!) Annotation mismatch: span.text ({span["text"]}!r) != text@span_location ({ner_phrase}!r).')
        elif len(span['text']) == 0:
            raise Exception(f'(!) Annotation error: span.text cannot be empty string.')

    def check_for_duplicates(self, text, span):
        if self.validate:
            self.validate_entry(text, span)
        span = ast.literal_eval( span )
        if text not in self.seen_text_annotations:
            self.seen_text_annotations[text] = []
        assert span not in self.seen_text_annotations[text], \
             f'(!) duplicate entry: {span} already annotated for {text!r}'
        # Check for matching location but different labels
        for prev_span in self.seen_text_annotations[text]:
            if prev_span['start'] == span['start'] and \
               prev_span['end'] == span['end'] and \
               prev_span['labels'] != span['labels']:
                raise ValueError(f'(!) span {span["text"]!r} annotated with different labels: '+\
                                 f'{span["labels"]!r} vs {prev_span["labels"]!r}.')
        self.seen_text_annotations[text].append(span)