import ast
import warnings
import os, os.path
from collections import defaultdict

import numpy as np
import pandas as pd
from pandas import read_csv

from tqdm import tqdm

from estnltk import Text, Layer
from estnltk.taggers import Tagger
from estnltk_core.taggers import MultiLayerTagger


class RecallEstimator:
    '''Recall estimator for named entity recognizers.
    '''

    def __init__(self, description_file, method='precise_recall', add_correct_count=True):
        '''
        Loads evaluation benchmark data based on given data description_file. 
        Validates data (via the function validate_evaluation_data(...) below) 
        and throws an exception in case of any issues.
        
        Parameters
        ----------
        description_file: str
            Name of the file describing evaluation sub samples and corresponding statistics. 
            Must be a CSV format file.
        method: str
            Evaluation method. Currently, only one method has been implemented: 'precise_recall';
        add_correct_count: bool
            If True (default), then counts of correct/incorrect spans will be added to the 
            evaluation results. Otherwise, evaluation results contains only 'Recall' and 
            'Recall-95CI%'. 
            Default: True.
        '''
        if not os.path.isfile(description_file):
            raise Exception(f'(!) Non-existent or bad description file name {description_file!r}.')
        self.description_file = description_file
        self.gold_standard = \
            load_evaluation_data(description_file=self.description_file, validate=True)
        print(f'Loaded evaluation benchmark of size {len(self.gold_standard)}.')
        self.all_eval_results = {}
        self.eval_counter = 0
        self.add_correct_count = add_correct_count
        supported_methods = ['precise_recall']
        if method not in supported_methods:
            raise ValueError(f'(!) Unexpected method={method!r}. Supported methods: {supported_methods!r}')
        self.method = method
        self.gold_layer = '_gold_ner'

    def evaluate_tagger(self, tagger, eval_name=None, auto_layer=None, overwrite_existing=True, 
                              ignore_errors=False):
        '''
        Evaluates tagger on different sub samples / populations, calculates recall on 
        each sub sample, and a weighted average of recalls as the estimate of the recall 
        of the tagger. 
        Records evaluation results under eval_name and returns a dictionary with the 
        results. 
        
        Parameters
        ----------
        tagger: Union[Tagger, MultiLayerTagger]
            Tagger to be evaluated on the benchmark data.
        eval_name: str
            Name/description of tagger's evaluation. If not provided (default), then 
            defaults to f'{tagger.output_layer}_#{evaluation_count}', where 
            {evaluation_count} is the number of evaluations performed so far. 
        auto_layer: str
            (Optional) Name of the tagger's output layer. If not provided (default), 
            then attempts to detect the layer name automagically. 
        overwrite_existing: bool
            Whether existing layers will be removed in case the benchmark data has 
            already been tagged by this tagger. If set to False and the benchmark 
            data has already been annotated, an Exception will be thrown because an 
            attempt to add duplicate layers.
            Default: True.
        ignore_errors: bool
            If True, then ignores tagger errors/exceptions. A text causing a tagger error 
            will be taken as a text where no entities were detected by the tagger. 
            If False (default), then a tagger error will break the evaluation process.

        Returns
        -------
        Dict
            A dictionary with evaluation results (minimum keys: 'Recall', 'Recall-95CI%'). 
        '''
        # Evaluate tagger on sub-samples
        eval_result = evaluate_benchmark(self.gold_standard, tagger, auto_layer=auto_layer, 
                                         gold_layer=self.gold_layer, method=self.method, 
                                         overwrite_existing=overwrite_existing, 
                                         ignore_errors=ignore_errors)
        self.eval_counter += 1
        eval_name = self._construct_eval_name(tagger, eval_name)
        # Find & record recall estimate
        self.all_eval_results[eval_name] = \
            find_recall_estimate(eval_result, description_file=self.description_file)
        if self.add_correct_count:
            # Add correct/incorrect counts
            self.all_eval_results[eval_name]['correct'] = \
                eval_result['correct'].value_counts()['yes']
            self.all_eval_results[eval_name]['incorrect'] = \
                eval_result['correct'].value_counts()['no']
        return self.all_eval_results[eval_name].copy()

    def _construct_eval_name(self, tagger, eval_name):
        ''' [Internal] Constructs the name of tagger's evaluation if eval_name is None. '''
        if isinstance(eval_name, str):
            return eval_name
        else:
            # Construct eval_name based on tagger's output layer name and counter
            if isinstance(tagger, Tagger):
                eval_name = tagger.output_layer
            elif isinstance(tagger, MultiLayerTagger):
                eval_name = tagger.output_layers[0]
            else:
                raise TypeError(f'(!) Unexpected tagger type {type(tagger)!r}, '+\
                                 'unable to detect name of the output layer.')
            return f'{eval_name}_#{self.eval_counter}'

    def leaderboard(self, order_by_recall=True):
        '''Returns leaderboard of the evaluation (pandas.DataFrame). 
           If order_by_recall is True (default), then the table is 
           sorted by column 'Recall'.
        '''
        leaderboard = pd.DataFrame.from_dict(self.all_eval_results, orient='index')
        if order_by_recall and not leaderboard.empty:
            leaderboard = \
                leaderboard.sort_values( by='Recall', ascending=False )
        return leaderboard


# =================================================================
#  Validate and summarize evaluation data
# =================================================================

def validate_evaluation_data(description_file='data_description.csv'):
    '''
    Validates recall benchmark evaluation data:
    * Data description is in right format;
    * Data description is consistent with the benchmark files;
    * No duplicates in the files;
    * Input files are in the same format;
    Throws an exception in case of detected inconsistencies.
    '''
    # Validate data description's format
    try:
        desc = read_csv(description_file)
    except Exception as csv_parsing_err:
        raise ValueError(f'(!) Bad description file format: unable to open {description_file!r} as a CSV file: ') from csv_parsing_err
    required_columns = ['file', 'population', 'occurences', 'labelled', 'positive']
    missing_columns = []
    for req_col in required_columns:
        if req_col not in desc.columns:
            missing_columns.append(req_col)
    if missing_columns:
        raise ValueError(f'(!) CSV file {description_file!r} is missing columns {missing_columns!r}.')
    # Validate data description's content
    seen_files = set()
    last_population = None
    populations_count = defaultdict(int)
    for filename, population, positive in zip(desc.file, desc.population, desc.positive):
        # Validate population files ordering
        populations_count[population] += 1
        if populations_count[population] > 1 and last_population != population:
            # Validate that all examples of a population are consecutive. 
            # (If not, then our weight calculations do not work as expected)
            raise ValueError(f'(!) Non-consecutive files of the population {population!r}: '+
                             f'unexpectedly previous file is from another population {last_population!r} '+
                             f'in {description_file!r}.')
        # Validate input files
        if filename in seen_files:
            raise ValueError(f'(!) Duplicate file {filename!r} in evaluation benchmark {description_file!r}.')
        if not os.path.isfile(filename):
            raise Exception(f'(!) Non-existent or bad file name {filename!r} in evaluation benchmark {description_file!r}.')
        try:
            data = read_csv(filename)
        except Exception as csv_parsing_err:
            raise ValueError(f'(!) Bad input file format: unable to open {filename!r} as a CSV file: ') from csv_parsing_err
        if len(data.text) != positive:
            raise ValueError(f'(!) Number of samples in file {filename!r} ({len(data.text)}) does '+\
                             f'not match with the number of samples in {description_file!r} ({positive}).')
        index = 0
        # Validate NE annotations
        for text_str, span in zip(data.text, data.span):
            span = ast.literal_eval( span )
            # Example span: "{'start': 0, 'end': 13, 'text': 'Inglise kanal', 'labels': ['LOC']}"
            assert 'start' in span,  f'(!) {filename!r}:{index}: span is missing "start" attribute'
            assert 'end' in span,    f'(!) {filename!r}:{index}: span is missing "end" attribute'
            assert 'labels' in span, f'(!) {filename!r}:{index}: span is missing "labels" attribute'
            assert 'text' in span,   f'(!) {filename!r}:{index}: span is missing "text" attribute'
            assert isinstance(span['labels'], list), f'(!) {filename!r}:{index}: span "labels" is not a list'
            ner_phrase = text_str[span['start']:span['end']]
            if len(span['text']) > 0 and ner_phrase != span['text']:
                raise Exception(f'(!) {filename!r}:{index}: span.text ({span["text"]}!r) != text@span_location ({ner_phrase}!r).')
            elif len(span['text']) == 0:
                raise Exception(f'(!) {filename!r}:{index}: span.text cannot be "".')
            index += 1
        seen_files.add( filename )
        last_population = population


def corpus_statistics(description_file='data_description.csv'):
    '''Calculates the estimated number of positive cases in the corpus (along with 
       95% CI) based on numbers of all detected occurrences, manually labelled 
       occurrences and positive instances. 
       Returns Dataframe of description_file with added columns: 'estimated_positives',
       'estimated_positives_lower', 'estimated_positives_upper'.
    '''
    desc = read_csv(description_file, index_col=0)
    desc = desc.rename_axis('index')
    # Calculate the estimated number of positives for each population along with 95% CI
    estimated_pos = []
    estimated_lowers = []
    estimated_uppers = []
    for filename, population, positives, labelled, total in zip( desc.file, desc.population, \
                                                                 desc.positive, desc.labelled, \
                                                                 desc.occurences ):
        estimated_pos.append( positives * total / labelled )
        ones = positives * [1]
        zeros = (labelled-positives) * [0]
        ones.extend(zeros)
        std_dev = np.std( np.array(ones) )
        lower = (positives/labelled - 0.95 * std_dev / np.sqrt(labelled))*labelled
        upper = (positives/labelled + 0.95 * std_dev / np.sqrt(labelled))*labelled
        estimated_lowers.append( int(lower*total/labelled) )
        estimated_uppers.append( int(upper*total/labelled) )
    desc['estimated_positives'] = estimated_pos
    desc['estimated_positives_lower'] = estimated_lowers
    desc['estimated_positives_upper'] = estimated_uppers
    # Calculate total estimated number of positives over all populations
    total_estimated_positives = desc['estimated_positives'].sum()
    #print(total_estimated_positives)
    return desc

# =================================================================
#  Detect overlaps between evaluation datasets
# =================================================================

def detect_evaluation_sets_overlaps(root_dir='.', description_file='data_description.csv', output_duplicates=True):
    eval_sets = {}
    for root, dirs, files in os.walk(root_dir):
        if description_file in files:
            fpath = os.path.join(root, description_file)
            eval_sets[root] = load_evaluation_data(description_file=fpath)
            print(f'Loaded evaluation set {root!r} of size {len(eval_sets[root])}.')
    all_texts = 0
    all_text_annotations = 0
    duplicate_texts = 0
    duplicate_text_annotations = 0
    seen_texts = set()
    seen_text_annotations = dict()
    confirmed_duplicates = dict()
    for set_name in sorted( eval_sets.keys() ):
        for sent_text_obj, population in zip(eval_sets[set_name].text, eval_sets[set_name].population):
            all_texts += 1
            sent_str = sent_text_obj.text
            if sent_str not in seen_texts:
                seen_texts.add(sent_str)
                seen_text_annotations[sent_str] = []
                for span in sent_text_obj['_gold_ner']:
                    all_text_annotations += 1
                    annotation = (span.start, span.end, span.text, span.annotations[0]['labels'], population, set_name)
                    seen_text_annotations[sent_str].append( annotation )
            else:
                duplicate_texts += 1
                for span in sent_text_obj['_gold_ner']:
                    all_text_annotations += 1
                    annotation = (span.start, span.end, span.text, span.annotations[0]['labels'], population, set_name)
                    # Check for the annotation duplicate
                    for prev_annotation in seen_text_annotations[sent_str]:
                        if annotation[:-2] == prev_annotation[:-2]:
                            if sent_str not in confirmed_duplicates:
                                confirmed_duplicates[sent_str] = {}
                            ann_key = str(annotation[:-2])
                            if ann_key not in confirmed_duplicates[sent_str]:
                                confirmed_duplicates[sent_str][ann_key] = [prev_annotation]
                            confirmed_duplicates[sent_str][ann_key].append(annotation)
                            duplicate_text_annotations += 1
                    seen_text_annotations[sent_str].append( annotation )
    if output_duplicates:
        print()
        for sent_str in confirmed_duplicates.keys():
            print(f'* {sent_str!r} has been annotated in multiple evaluation sets:')
            for ann_key in confirmed_duplicates[sent_str].keys():
                for annotation in confirmed_duplicates[sent_str][ann_key]:
                    print(f'   {ann_key} in {annotation[-1]!r} subpopulation {annotation[-2]!r}')
            print()
    print()
    per_dup_texts = (duplicate_texts/all_texts)*100.0
    print(f' Total duplicate sentences:             {duplicate_texts!r} / {all_texts!r} ({per_dup_texts:.2f}%)')
    per_dup_text_annotations = (duplicate_text_annotations/all_text_annotations)*100.0
    print(f' Total duplicate sentence annotations:  {duplicate_text_annotations!r} / {all_text_annotations!r} ({per_dup_text_annotations:.2f}%)')



# =================================================================
#  Load evaluation data, perform evaluation and estimate recall    
# =================================================================

def load_evaluation_data(description_file='data_description.csv', validate=True):
    if validate:
        validate_evaluation_data(description_file=description_file)
    gold_standard = pd.DataFrame(columns=('text','population'))
    desc = read_csv(description_file)
    for filename, population, positive in zip(desc.file, desc.population, desc.positive):
        data = read_csv(filename)
        assert len(data.text) == positive
        for text_str, span in zip(data.text, data.span):
            text_obj = Text(text_str)
            span = ast.literal_eval( span )
            assert isinstance(span['labels'], list)
            gold_layer = Layer('_gold_ner', attributes=['labels'], text_object=text_obj)
            gold_layer.add_annotation( (span['start'], span['end']), labels=span['labels'] )
            text_obj.add_layer( gold_layer )
            gold_standard.loc[len(gold_standard)] = {'text':text_obj, 'population':population}
    return gold_standard

def _create_empty_layers(tagger):
    if isinstance(tagger, Tagger):
        return [tagger.get_layer_template()]
    elif isinstance(tagger, MultiLayerTagger):
        empty_layers = []
        for output_layer in tagger.output_layers:
            attribs = tagger.output_layers_to_attributes.get(output_layer, ())
            empty_layers.append(Layer(output_layer, attributes=attribs))
        return empty_layers

def evaluate_benchmark(benchmark_data, tagger, auto_layer=None, 
                       gold_layer='_gold_ner', method='precise_recall', 
                       overwrite_existing=True, ignore_errors=False):
    if auto_layer is None:
        # Try to detect name of the ner layer automatically
        if isinstance(tagger, Tagger):
            auto_layer = tagger.output_layer
        elif isinstance(tagger, MultiLayerTagger):
            auto_layer = tagger.output_layers[0]
        else:
            raise TypeError(f'(!) Unexpected tagger type {type(tagger)!r}, '+\
                             'unable to detect name of the output layer.')
    columns=['correct']
    for population in set(benchmark_data.population.values):
        columns.append(f'{population}_correct')
    results = pd.DataFrame(columns = ['correct', 'population'])
    for eval_sentence, cur_population in tqdm( zip(benchmark_data.text, benchmark_data.population), \
                                               total=len(benchmark_data.text) ):
        # Add prerequisite layers
        eval_sentence.tag_layer()
        
        # Remove existing layer(s) (if required)
        if overwrite_existing:
            if isinstance(tagger, Tagger):
                if tagger.output_layer in eval_sentence.layers:
                    eval_sentence.pop_layer(tagger.output_layer)
            elif isinstance(tagger, MultiLayerTagger):
                for output_layer in tagger.output_layers:
                    if output_layer in eval_sentence.layers:
                        eval_sentence.pop_layer(output_layer)
        # Add new layer
        try:
            tagger.tag(eval_sentence)
        except Exception as ex:
            if ignore_errors:
                warnings.warn(f'(!) Failed processing {eval_sentence.text!r} due to an error:\n {ex}')
                # Create empty output layers
                # (like tagger detected nothing)
                empty_layers = _create_empty_layers(tagger)
                for empty_layer in empty_layers:
                    eval_sentence.add_layer(empty_layer)
            else:
                # Halt the evaluation, raise the exception
                raise ex
        
        if auto_layer not in eval_sentence.layers:
            raise ValueError(f' (!) Tagger {tagger} did not create layer '+\
                             f'{auto_layer!r}. Unable to evaluate output.')
        correct = 'no'
        nerspans = getattr(eval_sentence, auto_layer)
        gold_span = eval_sentence[gold_layer][0]
        for nerspan in nerspans:
            if nerspan.start==gold_span.start and \
               nerspan.end==gold_span.end and \
               nerspan.nertag==gold_span.labels[0]:
                correct = 'yes'
        results.loc[len(results)] = {'population': cur_population, \
                                     'correct':correct}
    return results


def find_recall_estimate(eval_results, description_file='data_description.csv'):
    '''
    Finds recall estimate based on the given sub-sample evaluation results. 
    
    First, calculates weight for each item in a population, following the formula:
    estimated_positives_in_population/(observed_positives_in_population*
    total_estimated_positives_over_all_populations).
    Second, finds a sample mean by calculating a dot product of the weight vector and 
    the correct vector (binomial encoding of the eval_results: 1==match, 0==mismatch). 
    This is the recall estimate. 
    Finally, estimates the standard error of the sample mean, and finds confidence 
    intervals (assuming 95% confidence level) for the estimated recall.
    Returns a dictionary with estimated variable values ('Recall' and 'Recall-95CI%').
    
    Based on:
    https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval#Standard_error_of_a_proportion_estimation_when_using_weighted_data

    TODO: Correct and hard version
    # https://stats.stackexchange.com/questions/485266/better-confidence-intervals-for-weighted-average
    # find a convolution of distributions 
    # https://medium.com/analytics-vidhya/sum-of-two-random-variables-or-the-rocky-path-to-understanding-convolutions-of-probability-b0fc29aca3b5
    # https://stackoverflow.com/questions/66218036/question-on-discrete-convolution-with-python
    # https://numpy.org/doc/stable/reference/generated/numpy.convolve.html
    # https://stackoverflow.com/questions/28901221/faster-convolution-of-probability-density-functions-in-python
    '''
    # Collect populations used in the evaluation
    populations = []
    populations_count = defaultdict(int)
    last_pop = None
    for pop in eval_results.population:
        if pop not in populations:
            populations.append(pop)
        populations_count[pop] += 1
        if populations_count[pop] > 1 and last_pop != pop:
            # Validate that all examples of a population are consecutive. 
            # (If not, then our weight calculations do not work)
            raise ValueError(f'(!) Non-consecutive examples of the population {pop!r}: '+
                             f'unexpectedly previous example is from another population {last_pop!r}.')
        last_pop = pop
    #print(populations)
    # Find corpus statistics
    corpus_stats = corpus_statistics(description_file=description_file)
    # Observed positives -> estimated positives -> total estimated positives
    total_positives = corpus_stats['estimated_positives'].sum()
    # Construct weight vector
    weight_vector = []
    for pop in populations:
        positives = corpus_stats.loc[corpus_stats['population']==pop, 'positive'].iloc[0]
        estimated_positives = corpus_stats.loc[corpus_stats['population']==pop, 'estimated_positives'].iloc[0]
        pop_weight = estimated_positives/(positives*total_positives)
        #print(pop, pop_weight, int(positives))
        weight_vector += ([pop_weight] * positives)
    # Construct correct assignments vector
    # Assume binomial distribution (1==match, 0==mismatch)
    correct_vector = []
    for correct in eval_results.correct:
        correct_vector.append( 1 if correct=='yes' else 0 )
    correct_vector = np.array(correct_vector)
    # Calculate sample mean and conf interval (for a 95% confidence level)
    sample_mean = np.matmul(weight_vector, correct_vector)
    standard_error = np.sqrt(sample_mean * (1-sample_mean) * np.sum(np.square(weight_vector)))
    confidence_interval = (sample_mean - standard_error * 1.96, sample_mean + standard_error * 1.96)
    return { 'Recall': sample_mean, 'Recall-95CI%': confidence_interval }

