
# Dataset description

The test corpus contains 1000 sentences, 500 with free and 500 with bound phrases.
The code for creating the benchmark dataset is located at phrase_removal/data_generation/obl/01_create dataset.ipynb


## Files

* `obl_1000_benchmark.csv`: contains 1000 sentences with manual labeling

* `obl_1000_syntax.conllu`: contains the original syntax for the 1000 sentences; In the conllu file benchmark_id refers to the column id in the obl_benchmark_1000.csv file

* `obl_1000_verb_lem.csv`: contains sentences with additional information about the main word in phrase, phrase related verb and the verb lemma

* `obl_1000_verb_lem_adv.csv`: contains sentences with additional information if the phrase is time, location, event or other; category time-loc is used for phrases that represent both time and location (an exception), category other is used for phrases that do not fit into any other category

