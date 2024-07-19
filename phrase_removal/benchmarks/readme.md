
# ChatGPT precision and recall estimation on benchmarks

## Algorithms/models

* ChatGPT 3.5
* TartuNLP Grammatical Error Correction

## Evaluation/estimation

The metrics are calculated based on model predictions vs manual annotation.  
The manual annotations categorize phrases as free or bound. For evaluation, free phrase is categorized as removetype "yes" and bound as removetype "no".
In case the model categorizes the sentence as grammatically correct or doesn't suggest any corrections, the answer is considered to be removetype "yes", otherwise "no".


## Results

[leaderboard_obl_phrases.csv](leaderboard_obl_phrases.csv) ( corresponding code: [obl_chatgpt35_eval.ipynb](obl_chatgpt35_eval.ipynb),  [obl_Grammatical_Error_Correction_eval.ipynb](obl_Grammatical_Error_Correction_eval.ipynb) )
