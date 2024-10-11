## Verb patterns
- Directory `data/verb_pattern_data`:
  - `12_eesti_ilmik_rektsiooniga_linkideta.xlsx` is the source file, from which verbs and patterns are extracted.
  - `rektsioon_kaanetega.csv` is similar to the source file, but longer verb constructions have been splitted and grammatical case information added.
  - `verb_patterns_len1.csv` is the first version of extracted verbs and patterns that consist of a singular phrase (now irrelevant).
  - `verb_patterns_len2.csv` is the first version of extracted verbs and patterns that consist of two phrases (now irrelevant).
  - `verb_patterns_len1_new.csv` is the new version of extracted verbs and patterns that consist of a singular phrase. This table is saved in database *verb_patterns_new.db*.
  - `verb_patterns_len2_new.csv` is the new version of extracted verbs and patterns that consist of two phrases. This table is saved in database *verb_patterns_new.db*.
- Notebook `verb_patterns.ipynb` consists of step-by-step code for extracting verbs, their compound parts and patterns from the source file and finally saving the resulting pattern tables in database *verb_patterns_new.db*.
