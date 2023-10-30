# Workflow to create recall benchmark for geographic locations (amundsen_01)

This benchmark considers two word geographic location phrases that end with specific suffix words (listed in [geo_terms.txt](geo_terms.txt)).
Sub populations are created by dividing samples into frequency/ambiguity classes, in which tagger results can (expectedly) differ. 

|Subpopulation | Description | Examples |
|:--- |:---|:---|
|Levinumad | Geographic locations with most frequent suffixes | Niiluse jõgi, Aasovi meri, Peipsi järv |
|Mitmetäheduslikud | Geographic locations with ambigous suffixes | Panama kanal, Panga pank, Kura kurk |
|Ülejäänud | Other/remaining geographic locations | Vaikne ookean, Liivi laht, Tehvandi mägi |

Exact division into sub populations can be found from [this folder](https://github.com/estnltk/estnltk-model-data/tree/main/named_entity_recognition/recall_estimation/data_generation/amundsen_01/config/subpopulations).


## I. Setup

* For the input, you first need a corpus in EstNLTK's PostgreSQL database. The corpus/text collection needs to be stored at the sentence level, that is, each Text object in the collection must be a sentence. We used the Koondkorpus database, which creation scripts are [here](https://github.com/estnltk/estnltk-workflows/tree/master/estnltk_workflows/koondkorpus_and_ettenten_to_postgres) and sentence-splitting scripts are [here](https://github.com/estnltk/syntax_experiments/tree/syntax_consistency/collection_splitting);
* You need a layer marking all the sentences containing given geographical terms. Use the script [extract_geo_sentences.p](https://github.com/estnltk/estnltk-model-training/blob/main/statistical_ner_labelling/scripts/extract_geo_sentences.py) for creating that layer;
* Once previous points have been completed, create a configuration INI file in [config/](config) folder;
* Use [00_validate_setup.ipynb](00_validate_setup.ipynb) to check the setup/configuration; 

## II. Benchmark creation steps

* Use [01_create_sampling_tasks.ipynb](01_create_sampling_tasks.ipynb) to create a local sampling database and to randomly pick a fixed amount of samples from each sub population. The same notebook also exports picked samples as [labelstudio format json files](unlabelled_data/sampled_sentences_ls_format). We picked 1000 samples from each sub population.
* Use [02_process_labelled_samples.ipynb](02_process_labelled_samples.ipynb) to do the basic validation of the manual labelling;
* Use [03_resolve_labellling_conflicts.ipynb](03_resolve_labellling_conflicts.ipynb) to check consistency of manual labellings with the benchmark setup and to create a labelling task for consolidating conflicting labellings;
* Convert manual labellings from json format to recall_sets CSV files;
* Use [04_update_benchmark.ipynb](04_update_benchmark.ipynb) to validate recall_sets files (check for duplicates), and to create a dataset description CSV file (example [description file](data_description.csv)).
* Finally, copy [recall_sets](labelled_data/recall_sets) and the [description file](data_description.csv) into [the benchmarks folder](https://github.com/estnltk/estnltk-model-data/tree/main/named_entity_recognition/recall_estimation/benchmarks), following the structure of existing benchmarks (amundsen_01, amundsen_02) in the directory.
