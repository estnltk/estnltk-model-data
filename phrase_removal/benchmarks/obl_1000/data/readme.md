
# Dataset for obl_1000 benchmark 

The test corpus contains 1000 sentences, 500 with free and 500 with bound phrases.
The code for creating the benchmark dataset is located at phrase_removal/data_generation/obl/01_create dataset.ipynb

Data file *obl_gpt_large1_verb_lem_adv.csv* contains additional information about the phrases: whether they represent time, location or an event. Category *other* is used for phrases that do not fit into any of the previously mentioned categories.
