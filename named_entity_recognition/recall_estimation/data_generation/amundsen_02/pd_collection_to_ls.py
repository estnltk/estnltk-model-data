from estnltk import Text
import random
import json
from typing import List


def conf_gen(classes: List[str]):
    single_label = '\t<Label value="{label_value}" background="{background_value}"/> \n'
    conf_string = """
<View>
    <Labels name="label" toName="text">\n
    """
    end_block = """
"""

    for entry in classes:
        conf_string += single_label.format(
            label_value=entry,
            background_value=("#" + "%06x" % random.randint(0, 0xFFFFFF)).upper()
        )
    conf_string += end_block

    return conf_string



def from_pd_dataframe(row, layer):
    predictions = []
    results = {}

    predictions.append({

            'to_name': "text",
            'from_name': "label",
            'type': 'labels',
            'value': {
                "start": int(row["start"]),  # span.start,
                "end": int(row["end"]) , # span.end,
                "text":  str(row["phrase"])   ,   #span.text,
                "labels": [
                    str(layer)
                ]
            }
        
            })
    data = {'text': str(row["text"])} 
    results = {
        'data': data,
        'predictions': [{
            'result': predictions}
            ]
    }
        
    return results



def collection_to_labelstudio(collection, 
                              deprel, 
                              filename: str,
                              regular_layers: List[str]=None, 
                              classification_layer: str = None,
                              ner_layer: str = None
                              ):


    data1 = [from_pd_dataframe(collection.iloc[i], deprel) for i in range(len(collection))]
    data = []
    
    for elem in data1:
        if type(elem) == list:
            for e in elem:
                data.append(e)
        else:
            data.append(elem)

    with open(filename, 'w') as f:
        json.dump(data, f)

