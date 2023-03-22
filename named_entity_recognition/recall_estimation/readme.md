# Benchmark datasets for estimating recall


Estimating the recall of a tagger on non-labelled data is important because this allows calculation of the F1 score and the evaluation of taggers on new data that was not used in the training phase. Having different datasets also allows for more analysis and customization in the test sets.

    
Whereas estimating the precision of a tagger on non-labelled data is easy because only the spans that have been tagged have to be manually checked, estimating the recall is much harder because it is necessary to go through all the texts to get the correct recall score.

    
Since the test corpus is big and the amount of total texts is much larger than the ones tagged as the positive class, we use sampling to find texts that could potentially contain the positive span and sample from subsets of these.


This example is created to calculate the recall for named entity phrases consisting of two words, the second of which is a geographic term such as 'lake', 'river', 'ocean' etc.
To find potential candidates of these entities for the recall estimation, only texts where these terms appear are considered. Since the recall can be very different for different terms, the sample is divided into three subsamples: the most popular terms ('järv','jõgi','saar',...), the ones that have more common homonyms ('pank', 'kurk', 'kanal') and all the others. The recall is calculated for samples from each of these groups and a weighted average of these recalls is the estimate of the recall of the tagger.