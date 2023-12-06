# Structurally augmented EstUD Treebank


[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

This folder contains various augmentations of [EstUD Treebank](https://github.com/EstSyntax/EstUD).
Most of them are manually curated but some of them can be fully automatic.
Exact methodology is described for each folder separately.

## Motivation

Correctness of syntactic labels is only one goal in automatic syntax analysis.
Consistency against word reorderings and sentence shortenings is another important property.
The same sentence can have many forms in Estonian as the word order is quite relaxed.
In such cases, the changes in the syntax tree are fully predictable.
The same is true when one removes free modifers from the sentence.
More formally, a syntactical invariant is a sentence modification rule together with 
a syntax modification rule such that when applicable the modified sentence has indeed
the predicted syntax tree.
We apply these transformations on manually annotated sentences to get additional 
training data for enforcing consistency against syntactical invariants.

## Methods

Omitted phrases are subtrees of a syntax tree. Its type is defined by the dependency 
relation of the root node. See the documentation of [UD dependency relations](https://universaldependencies.org/u/dep/).



