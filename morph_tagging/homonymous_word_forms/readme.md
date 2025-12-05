# Manually labelled morphological tags for homonymous word forms in Vabamorf format

There are many homonymous word forms in Estonian. 
This creates a problem in morphological disambiguation that Vabamorf cannot resolve correctly. 
The following dataset consists of targeted samples, which capture these ambiguities. 
Samples come from 4 different inflectional types:

* inflectional type 1: 
    * words that are ambiguous between nominative and genitive case: `sg n`, `sg g`
    * example: _akadeemia_ (nominative), _akadeemia_ (genitive)

* inflectional type 16:
    * words that are ambiguous between nominative and genitive case: `sg n`, `sg g`
    * example: _kõne_ (nominative), _kõne_ (genitive)

* inflectional type 17:
    * words that are ambiguous between nominative, genitive and partitive case: `sg n`, `sg g`, `sg p` 
    * example: _muna_ (nominative), _muna_ (genitive), _muna_ (partitive)

* inflectional type 19:
    * words that are ambiguous between genitive, partitive and short illative case: `sg g`, `sg p`, `adt`
    * example: _admirali_ (genitive), _admirali_ (partitive), _admirali_ (short illative)

Note that only homonymous word form has manually curated tags. 
The surrounding words are without annotations.
For further details, see [the code for generating the targeted sample](https://github.com/estnltk/estnltk-model-training/tree/main/morph_tagging/1000_sentences_with_homonymous_words).

