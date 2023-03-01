TODO: 
* Describe the NER algorithms in the leaderboard.md
* Give a source code links and description of all algorithms





Calculations based on https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval#Standard_error_of_a_proportion_estimation_when_using_weighted_data

This shows how to calculate the standard error of a binomial distribution when using weighted data. The 95% confidence interval is (sample_mean - 1.96 * standard_error, sample_mean + 1.96 * standard_error)

This standard error calculation assumes that the probability of each sample is equal to the sample mean. We could improve on that by using subsample means instead, not implemented here.