# Potentially conflicting NER phrases and noun phrases

There four potential placement patterns of noun and ner phrases:

* noun phrase coincides with a NER phrase;
* noun phrase is inside NER phrase;
* NER phrase is inside noun phrase;
* noun and NER phrases intersect.

Naively, only the first placement pattern is correct and all others indicate to an error.
In practice, this is not the case as a noun phrase can contain another noun phrase.
The following dataset contains manually corrected NER annotations for the last three configuration types. 
Further details about sampling look at [the original sampling code](https://github.com/estnltk/estnltk-model-training/blob/516f33431950d60c974168f724584514de170a42/statistical_ner_labelling/ner_obl_sampling.ipynb).

