# Recall benchmark for geographic locations (amundsen_02)

This benchmark contains geographic location phrases that end with specific suffix words ([geo_terms.txt](https://github.com/estnltk/estnltk-model-data/blob/main/named_entity_recognition/recall_estimation/data_generation/amundsen_02/geo_terms.txt)).
Sub populations are created by dividing phrases into classes by (automatically assigned) part of speech tags of first words of phrases.

|Subpopulation | Description | Examples |
|:--- |:---|:---|
|A    | Geographic locations starting with an adjective (A) | Vaikse ookeani, Mustast merest, Kollase mere |
|H    | Geographic locations starting with a proper noun (H) | Pärnu lahelt, Fidzhi saartega, Viljandi järve     |
|S    | Geographic locations starting with a common noun (S) | Rohuneeme poolsaare, Pühajärve randa, Kolka neeme |
|...  | ... | ... |

Code for benchmark creation/updating: https://github.com/estnltk/estnltk-model-data/blob/main/named_entity_recognition/recall_estimation/data_generation/amundsen_02
