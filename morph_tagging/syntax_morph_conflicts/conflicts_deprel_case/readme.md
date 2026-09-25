## Syntax and morphology conflict dataset

Syntax models based on neural networks do not take into account agreement rules between syntax and morphology.
The following dataset has been obtained by analyzing a subset of sentences from [Estonian Reference Corpus](https://metashare.ut.ee/repository/browse/estonian-reference-corpus/4c8f460c463411e2a6e4005056b40024a0f8c14982ef44b8962802ca8099554b/) (*Koondkorpus*), specifically from a [database of verb transactions](https://github.com/estnltk/syntax_experiments/tree/verb_templates/workflows/001_verb_transactions/v33).
In the future, there are plans to extend this with analysis of the entire Estonian Reference Corpus.

Below is a set of conflicts identified from the [syntax–morphology conflict table](https://github.com/estnltk/syntax_experiments/tree/verb_templates/workflows/004_analysis_of_known_verb_rection_patterns/004_extracting_syntax_morphology_conflicts).

 - *Error rate (transactions)* represents the proportion of this type of error among all occurrences of the given dependency relation (deprel) in the transactions database.
 - *Impact (transactions)* represents the proportion of this type of error among all transaction heads in the transactions database.
 - *Error rate (syntax-morph conflicts)* represents the proportion of this type of error among all occurrences of the given deprel in the syntax–morphology conflict table.
 - *Impact (syntax-morph conflicts)* represents the proportion of this type of error among all conflicts in the syntax–morphology conflict table.

Error rate and impact values are scaled by 1:100000. 


| description | deprel | case | error rate (transactions) | impact (transactions) | error rate (syntax-morph conflicts) | impact (syntax-morph conflicts)
|---|---|---|---|---|---|---
| when *nsubj* is not in nominative/partitive case | nsubj | ^(nom\|part) | 68.2 | 32.03 | 7864.6 | 1471
| when 
*nsubj:cop* is not in nominative/partitive case | nsubj:cop | ^(nom\|part) | 10.89 | 0.01 | 3288.4 | 0.46
| when *obj* is not in nominative/genitive/partitive case| obj | ^(nom\|gen\|part) | 892.95 | 193.47 | 22764.9 | 8884.32
| when *advcl* has case marking | advcl | ^0 | 131.72 | 8.69 | 35505.8 | 399.2
| when *advmod* has case marking | advmod | ^0 | 4.37 | 0.81 | 181.67 | 37.1
| when *xcomp* has case marking | xcomp | ^0 | 120.98 | 10.42 | 34653.25 | 478.3
| when *obl* is in nominative case | obl | nom | 137.79 | 42.64 | 12241.96 | 1958.3

**Note:** According to UD annotation guidelines, *xcomp* and *advcl* may in fact appear with case marking, and *obl* may also occur in nominative case. Therefore, these cannot be treated as definitive morpho-syntactic conflicts. More detailed analysis is required.

**Dataset contents:**

 - `conflicts` -- sentences with marked conflict locations
 - `conflict_annotations` -- where it is specified whether the morphology is correct or not

**Workflow for generating the dataset:** [https://github.com/estnltk/syntax_experiments/tree/verb_templates/workflows/004_analysis_of_known_verb_rection_patterns/005_categorizing_syntax_morphology_conflicts](https://github.com/estnltk/syntax_experiments/tree/verb_templates/workflows/004_analysis_of_known_verb_rection_patterns/005_categorizing_syntax_morphology_conflicts)