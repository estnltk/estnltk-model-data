
# NER recall estimation on benchmarks

## Algorithms/models

| Model | Description | Paper  | Code |
|-------|-------------|--------|------|
| EstNLTK-default-NER | CRF-based system (traditional ML) | [Tkachenko et al. (2013)](https://aclanthology.org/W13-2412/) | [estnltk-ner](https://github.com/estnltk/estnltk/tree/main/estnltk/estnltk/taggers/standard/ner) |
| EstBertNER-v1-estnltk_words | EstBERT finetuned for NER (v1), using EstNLTK's words tokenization | [Kairit Sirts (2023)](https://openreview.net/pdf?id=4CTnlIc1rhw) | [https://huggingface.co/tartuNLP/EstBERT_NER](https://huggingface.co/tartuNLP/EstBERT_NER) |
| EstBertNER-v1-bert_tokens   | EstBERT finetuned for NER (v1), using Bert's original tokenization | [Kairit Sirts (2023)](https://openreview.net/pdf?id=4CTnlIc1rhw) | [https://huggingface.co/tartuNLP/EstBERT_NER](https://huggingface.co/tartuNLP/EstBERT_NER) |
| EstBertNER-v2-estnltk_words | EstBERT finetuned for NER (v2), using EstNLTK's words tokenization | [Kairit Sirts (2023)](https://openreview.net/pdf?id=4CTnlIc1rhw) | [https://huggingface.co/tartuNLP/EstBERT_NER_v2](https://huggingface.co/tartuNLP/EstBERT_NER_v2)  |
| EstBertNER-v2-bert_tokens | EstBERT finetuned for NER (v2), using Bert's original tokenization | [Kairit Sirts (2023)](https://openreview.net/pdf?id=4CTnlIc1rhw) | [https://huggingface.co/tartuNLP/EstBERT_NER_v2](https://huggingface.co/tartuNLP/EstBERT_NER_v2)  |

## Calculations

Recall estimations are based on: https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval#Standard_error_of_a_proportion_estimation_when_using_weighted_data

This shows how to calculate the standard error of a binomial distribution when using weighted data. The 95% confidence interval is (sample_mean - 1.96 * standard_error, sample_mean + 1.96 * standard_error)

This standard error calculation assumes that the probability of each sample is equal to the sample mean. We could improve on that by using subsample means instead, not implemented here.

## Results

* [leaderboard_amundsen_01.csv](leaderboard_amundsen_01.csv) ( corresponding code: [evaluate_benchmark_amundsen_01.ipynb](evaluate_benchmark_amundsen_01.ipynb) )