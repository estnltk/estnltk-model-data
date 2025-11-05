
# NER recall estimation on benchmarks

## Algorithms/models

| Model | Description | Paper  | Code |
|-------|-------------|--------|------|
| EstNLTK-default-NER | CRF-based system (traditional ML). Recognizes three types of entities: PER, LOC, ORG. | [Tkachenko et al. (2013)](https://aclanthology.org/W13-2412/) | [estnltk-ner](https://github.com/estnltk/estnltk/tree/main/estnltk/estnltk/taggers/standard/ner) |
| EstBertNER-v1-estnltk_words | EstBERT finetuned for NER (v1), using EstNLTK's words tokenization. Recognizes three types of entities: PER, LOC, ORG. | [Hasan Tanvir et al. (2020)](https://arxiv.org/pdf/2011.04784) | [https://huggingface.co/tartuNLP/EstBERT_NER](https://huggingface.co/tartuNLP/EstBERT_NER) |
| EstBertNER-v1-bert_tokens   | EstBERT finetuned for NER (v1), using Bert's original tokenization. Recognizes three types of entities: PER, LOC, ORG. | [Hasan Tanvir et al. (2020)](https://arxiv.org/pdf/2011.04784) | [https://huggingface.co/tartuNLP/EstBERT_NER](https://huggingface.co/tartuNLP/EstBERT_NER) |
| EstBertNER-v2-estnltk_words | EstBERT finetuned for NER (v2), using EstNLTK's words tokenization. Recognizes 11 types of entities: PER, LOC, ORG, GPE, MONEY, PERCENT, PROD, TITLE, DATE, TIME and EVENT. | [Kairit Sirts (2023)](https://openreview.net/pdf?id=4CTnlIc1rhw) | [https://huggingface.co/tartuNLP/EstBERT_NER_v2](https://huggingface.co/tartuNLP/EstBERT_NER_v2)  |
| EstBertNER-v2-bert_tokens | EstBERT finetuned for NER (v2), using Bert's original tokenization. Recognizes 11 types of entities: PER, LOC, ORG, GPE, MONEY, PERCENT, PROD, TITLE, DATE, TIME and EVENT. | [Kairit Sirts (2023)](https://openreview.net/pdf?id=4CTnlIc1rhw) | [https://huggingface.co/tartuNLP/EstBERT_NER_v2](https://huggingface.co/tartuNLP/EstBERT_NER_v2)  |
| est-roberta-UD-ner_estnltk_words | Est-RoBERTa finetuned for NER on Estonian treebanks ([EDT](https://github.com/UniversalDependencies/UD_Estonian-EDT) and [EWT](https://github.com/UniversalDependencies/UD_Estonian-EWT)), using EstNLTK's words tokenization. Recognizes 8 types of entities: PER, LOC, ORG, GEP, PROD, EVE (event), MUU (misc) and UNK (unknown). | [Martin Kivisikk (2025)](https://thesis.cs.ut.ee/41345518-f5a0-471a-b3de-eddfa5d7073a) | [https://huggingface.co/vbius01/est-roberta-ud-ner](https://huggingface.co/vbius01/est-roberta-ud-ner)  |

## Evaluation/estimation

The recall is estimated on a sample of named entity phrases, which was (randomly) drawn from a large corpus and manually corrected.  
The sample has been divided into subsamples (sub populations) based on different criteria (e.g. in the `amundsen_01` benchmark, based on the frequency/ambiguity of geographical terms appearing in subsamples).   
A tagger/model is evaluated on each of these subsamples and a weighted average of the results is the estimate of the recall. 

Recall estimations are based on: https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval#Standard_error_of_a_proportion_estimation_when_using_weighted_data

This shows how to calculate the standard error of a binomial distribution when using weighted data. The 95% confidence interval is (sample_mean - 1.96 * standard_error, sample_mean + 1.96 * standard_error).
This standard error calculation assumes that the probability of each sample is equal to the sample mean. We could improve on that by using subsample means instead, not implemented here.

## Results

* [leaderboard_amundsen_01.csv](leaderboard_amundsen_01.csv) ( corresponding code: [evaluate_benchmark_amundsen_01.ipynb](evaluate_benchmark_amundsen_01.ipynb) )
* [leaderboard_amundsen_02.csv](leaderboard_amundsen_02.csv) ( corresponding code: [evaluate_benchmark_amundsen_02.ipynb](evaluate_benchmark_amundsen_02.ipynb) )