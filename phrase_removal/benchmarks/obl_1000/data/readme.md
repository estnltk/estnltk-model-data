
# Dataset for obl_1000 benchmark 

The test corpus contains 1000 sentences, 500 with free and 500 with bound phrases.
The code for creating the benchmark dataset is located at phrase_removal/data_generation/obl/01_create dataset.ipynb

The obl_benchmark_1000_original.conllu contains the syntax for the benchmark sentences.
In the conllu file benchmark_id refers to the column id in the obl_benchmark_1000.csv file.


Data file *obl_benchmark_1000_verb_lem_adv.csv* contains additional information about the phrases: whether they represent time, location or an event. Additional category *time-loc* is used for phrases that represent both time and location (an exception). Category *other* is used for phrases that do not fit into any of the previously mentioned categories. 

File *labelling_instruction.md* contains the rules which were used to annotate obl phrases.

Legacy: File *M2rgendusreeglid.docx* contains annotation guidelines in Estonian. 


