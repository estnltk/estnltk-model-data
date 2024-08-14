
#  Precision and recall estimation on benchmarks

## Algorithms/models

* Bert models
* different rule based approaches

## Evaluation/estimation

The metrics are calculated based on model predictions vs manual annotation.  
The manual annotations categorize phrases as free or bound. For evaluation, free phrase is categorized as removetype "yes" and bound as removetype "no".
In case the model categorizes the sentence as grammatically correct or doesn't suggest any corrections, the answer is considered to be removetype "yes", otherwise "no".

The test corpus contains 2444 sentences, 1199 with free and 1245 with bound phrases.

## Results
