# Shortened sentences from the EstUD Treebank

## Data description

Folders `Train` and `Dev` contain shortened sentences of EstUD treebank that
preserve the original split into training, development and test sets.
Each file name describes what phrase was omitted from the original sentence.
For instace `advmod_cut.conllu` contains sentences that are shortened by
elliminating adverbial modifiers from the original sentences. The file
`advmod_original.conllu` contains original unmodified sentences.
Comment blocks before each sentence specify the exact sentence and modification.
For instance the comment block
```
# sent_id = aja_ml200247_1591
# cut_word_ids = 3
# ud_version = 2.11
# text = Aga rehmab käega : mis seal ikka , müts on ikka kõige tähtsam .
```
specifies that the third word form the senetence was omitted and the sentece was 
taken from [the treebank version 2.11](https://github.com/EstSyntax/EstUD/tree/master/vers2_11).

## Methodology

For shortening, we fixed the list of phrase types which in theory are likely
free modifiers. For each phrase type, we chose 1000 random phrases form the
treebank and manually verified whether these phrases are indeed free modifiers
and whether the resulting shortening is grammatically correct sentence.
The exact workflow is in the [estnltk-model-training repo](https://github.com/estnltk/estnltk-model-training/tree/main/ud_treebank_data_augmentation/phrase_removal).

## Post-processing

Script `aggregate_datasets.py` aggregates all `train/*.conllu` and `dev/*.conllu` files into `cut_sentences_train.conllu` and `cut_sentences_dev.conllu` files that can be used as inputs in model training