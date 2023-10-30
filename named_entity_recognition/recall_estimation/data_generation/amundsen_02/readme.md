# Workflow to create recall benchmark for geographic locations (amundsen_02)

This benchmark considers only geographic locations that end with specific suffix words (listed in [geo_terms.txt](geo_terms.txt)), and make up two word phrases with a preceding word. 
Sub populations are created by dividing phrases into classes by (automatically assigned) part of speech tags of preceding words.

Some examples:

|Subpopulation | Description | Examples |
|:--- |:---|:---|
|A    | geographic location phrases where the first word is adjective (A) | Vaikse ookeani, Mustast merest, Kollase mere |
|H    | geographic location phrases where the first word is proper noun (H) | Pärnu lahelt, Fidzhi saartega, Viljandi järve     |
|S    | geographic location phrases where the first word is common noun (S) | Rohuneeme poolsaare, Pühajärve randa, Kolka neeme |
|...  | ... | ... |


## I. Setup

* For the input, you first need a corpus in EstNLTK's PostgreSQL database. The corpus/text collection needs to be stored at the sentence level, that is, each Text object in the collection must be a sentence. We used the Koondkorpus database, which creation scripts are [here](https://github.com/estnltk/estnltk-workflows/tree/master/estnltk_workflows/koondkorpus_and_ettenten_to_postgres) and scripts for splitting the corpus into sentences are [here](https://github.com/estnltk/syntax_experiments/tree/syntax_consistency/collection_splitting);
* You need a layer marking all the sentences containing given geographical terms. Use the script [extract_geo_sentences.p](https://github.com/estnltk/estnltk-model-training/blob/main/statistical_ner_labelling/scripts/extract_geo_sentences.py) for creating that layer;
* Once previous points have been completed, create a configuration INI file in [config/](config) folder;
* Use [00_validate_setup.ipynb](00_validate_setup.ipynb) to check the setup/configuration; 

## II. Benchmark creation steps

* Use [01_create_sampling_tasks.ipynb](01_create_sampling_tasks.ipynb) to create a local sampling database and to randomly pick a fixed amount of samples from each sub population. The same notebook also exports picked samples as labelstudio json files. We picked 1000 samples from each part of speech.
* Use [02_prepare_for_labelling.ipynb](02_prepare_for_labelling.ipynb) to extend randomly chosen annotations into 2 word phrases and to extract a small subset of sentences for the first phase of annotation. We picked 100 samples from each sub population sample for the first phase of manual annotation.
* Import data into [labelstudio](https://labelstud.io/) and use it for the first phase of manual annotation. The goal of manual labelling is to determine whether sampled phrases represent a named entity (NE). More specifically, annotators are  given choices for evaluating the match with NE: 'partial match', 'full match' ja 'no'. In our case, 1 annotator completed the work, following [the Estonian NE annotation guidelines](https://docs.google.com/document/d/1gZcNHmSEK3ua6EwsGJJgRUbfOTzSSa6LuQaDvgNThM4/) by Laura Katrin Leman and Kairit Sirts.
* Use [03_prepare_for_labelling_(phase_2).ipynb](03_prepare_for_labelling_(phase_2).ipynb) to prepare data for the second annotation phase. Exclude populations that did not contain any matches in the first annotation, also exclude sentences that have already been annotated in the first phase;
* Use [04_update_benchmark.ipynb](04_update_benchmark.ipynb) to post-process manual annotations (remove duplicates, take out positive cases, merge annotations of the first & second phase and save into [recall_sets](labelled/recall_sets) CSV files), and to create a dataset description CSV file (example [description file](data_description.csv)).
* Finally, copy [recall_sets](labelled/recall_sets) and the [description file](data_description.csv) into [the benchmarks folder](https://github.com/estnltk/estnltk-model-data/tree/main/named_entity_recognition/recall_estimation/benchmarks), following the structure of existing benchmarks (amundsen_01, amundsen_02) in the directory.
