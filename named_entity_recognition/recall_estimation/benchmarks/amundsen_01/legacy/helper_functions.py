from estnltk.taggers import NerTagger
from estnltk import Text
from tqdm import tqdm
import pandas as pd


def evaluate_benchmark(benchmark_data, model, layer, method='precise_recall'):
    
    estnltk_correct = pd.DataFrame(columns=['correct'])

    for snt in tqdm(benchmark_data.text):
        snt.tag_layer()
        model.tag(snt)
        correct = 'no'
        nerspans = getattr(snt,layer)
        span = snt.spans[0]
        for nerspan in nerspans:
            if nerspan.start==span.start and nerspan.end==span.end and nerspan.nertag==span['labels'][0]:
                correct = 'yes'
        estnltk_correct.loc[len(estnltk_correct)] = {'correct':correct}
    
    return estnltk_correct
