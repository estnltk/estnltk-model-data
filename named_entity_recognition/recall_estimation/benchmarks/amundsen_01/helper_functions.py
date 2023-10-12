import ast

import numpy as np
import pandas as pd
from pandas import read_csv

from tqdm import tqdm

from estnltk import Text, Layer
from estnltk.taggers import Tagger
from estnltk_core.taggers import MultiLayerTagger


def corpus_statistics(datafolder='data', description_file='data_description.csv'):
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


def load_evaluation_data(datafolder='data', description_file='data_description.csv'):
    gold_standard = pd.DataFrame(columns=('text','population'))
    desc = read_csv(description_file)
    for filename, population, positive in zip(desc.file, desc.population, desc.positive):
        data = read_csv(datafolder+'/'+filename)
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


def evaluate_benchmark(benchmark_data, tagger, auto_layer=None, 
                       gold_layer='_gold_ner', method='precise_recall', 
                       overwrite_existing=True):
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
        tagger.tag(eval_sentence)
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


def find_recall_estimate(eval_results, datafolder='data', description_file='data_description.csv'):
    '''
    Finds recall estimate based on the given sub-sample evaluation results. 
    
    TODO:
    
    Finds standard dev for each fraction estimate
    Combine stabndard deviation for the linear combination
    Find CI based on this estimate

    based on:
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
    for pop in eval_results.population:
        if pop not in populations:
            populations.append(pop)
    #print(populations)
    # Find corpus statistics
    corpus_stats = corpus_statistics(datafolder=datafolder, description_file=description_file)
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
    correct_vector = []
    for correct in eval_results.correct:
        correct_vector.append( 1 if correct=='yes' else 0 )
    correct_vector = np.array(correct_vector)
    # Calculate sample mean and conf interval
    sample_mean = np.matmul(weight_vector, correct_vector)
    standard_error = np.sqrt(sample_mean * (1-sample_mean) * np.sum(np.square(weight_vector)))
    confidence_interval = (sample_mean - standard_error * 1.96, sample_mean + standard_error * 1.96)
    return { 'Recall': sample_mean, 'Recall-95CI%': confidence_interval }

