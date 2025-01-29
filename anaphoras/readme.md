# Sentences with anaphores

Dataset generation for anaphore resolution can be divided into three stages.

1. Detect whether a sentence contains an anaphore.
2. Detect whether the anaphore references phrase in a sentence or the antecedent is outside the sentence.
3. Extract the antecedent from a list of potential sentence elements in the sentence.

The current dataset is based on a subset random sentences from Koondkorpus with following manual annotations
1. Whether a sentence contains an anaphore?
2. Whather a antecedent is inside the sentence?
3. What would be a question that reveals antecedent?
3. What is a the correct antecedent?

### Labelling in `anaphora_presence.csv`

The set of sentences was prefiltered based on Vabamorph morphological analysis.
All words that have part-of-speetch tag as P (pronomen) are marked as anaphoras.
All sentences without pronomens are filtered out.
No other anaphora types are considered.

|Label  |Meaning |
|:------|:-------|
|     -1| anaphore candidate is not pronoun                   |
|      0| invalid anaphore candidate                          |
|      1| antecedent is inside of the sentence                |
|      2| antecedent is outside of the sentence               |
|      3| antecedent can be inside or outside of the sentence |


### Labelling in `revealing_questions.csv`

The set of sentences that were prefiltered based on the annotations in `anaphora_presence.csv`.
All sentences where the antecendent was inside the sentence were kept.
The column `question` contains an automatically synthesised questions whose answer should be the antecedent.
The column ``question_fix` is manually corrected question if automatically syntesised question was incorrect.
The special value `0` was used as `question_fix` for sentences that do not have antecendent in them (postcorrections).


### Labelling in `anaphora_resolution.csv`

The set of sentences from `revealing_questions.csv` from which sentences wihtout antecendent in them were removed.
The column `possible_antecendents` contain all nouns that were detected based on automatic syntax analysis.
The column `correct_antecendent` is the correct worform in the text.
The column `antecendent_in_list` shows if the correct answer was in the list or not.
