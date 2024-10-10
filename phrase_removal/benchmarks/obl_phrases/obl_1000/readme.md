## Data description

The benchmark contains sentences taken form <puupank> with manually curated syntax tree.

The sentences contain obl phrases that were manually annotated to be 'free' (can be removed), 'bound' (can not be removed) and other.

Random 500 sentences with free phrases and 500 sentences with bound phrases are used to create the benchmark file.


## Validated models

* ChatGPT 3.5
* TartuNLP Grammatical Error Correction
* EstRoberta model
* different rule based approaches

## Model evaluation methods

The metrics are calculated based on model predictions vs manual annotation.  
The manual annotations categorize phrases as free or bound. For evaluation, free phrase is categorized as removetype "yes" and bound as removetype "no".
In case the model categorizes the sentence as grammatically correct or doesn't suggest any corrections, the answer is considered to be removetype "yes", otherwise "no".

[leaderboard_obl_1000_phrases.csv](results/obl_1000_leaderboard.csv) 

corresponding code for calculating precision and recall: 

[chatgpt 3.5 eval](evaluation/chatgpt35_eval.ipynb)

[Grammatical Error Correction eval](evaluation/grammatical_error_correction_eval.ipynb)

[BERT model eval](evaluation/model_eval_template.ipynb) 

[Creating the benchmark graph](evaluation/benchmark_graph.ipynb) 


## Additional annotations

The benchmark also contains additional annotations about location phrases.



## Annotation quides

[link to obl hand annotation guide](../labeling_guides/labelling_instruction.md)
 
[link to time/location annotation guide](../../time_loc_labeling_rules.md)





