# Potentially conflicting NER phrases and noun phrases

There four potential placement patterns for NER and noun phrases:

* a noun phrase coincides with a NER phrase;
* a noun phrase is inside a NER phrase;
* a NER phrase is inside a noun phrase;
* a noun and a NER phrases intersect.

Naively, only the first placement pattern is correct and all others are indications of an error.
In practice, this is not the case as a noun phrase can contain another noun phrase.
The following dataset contains manually corrected NER annotations for the last three configuration types. 
Further details about sampling look at [the original sampling code](https://github.com/estnltk/estnltk-model-training/blob/516f33431950d60c974168f724584514de170a42/statistical_ner_labelling/ner_obl_sampling.ipynb).

