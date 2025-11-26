
# Dataset description

The test corpus contains 1000 sentences, 500 with free and 500 with bound phrases.
The code for creating the benchmark dataset is located at [data generation](https://github.com/estnltk/estnltk-model-data/blob/main/phrase_removal/data_generation/obl/01_create%20dataset.ipynb).



## Files

* `appos_benchmark_1000.csv`: contains 1000 sentences with manual labeling.

* `appos_benchmark_1000_original.conllu`: contains the original syntax for the 1000 sentences. In the conllu file benchmark_id refers to the column id in the benchmark_1000.csv file.

* `appos_benchmark_1000_peasona_verb.csv`: contains sentences with additional information about the main word in phrase, phrase related verb and the verb lemma.
