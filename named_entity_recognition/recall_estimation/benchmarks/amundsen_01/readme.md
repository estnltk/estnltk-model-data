# Recall benchmark for geographic locations (amundsen_01)

This benchmark contains geographic location phrases that end with specific suffix words ([geo_terms.txt](https://github.com/estnltk/estnltk-model-data/blob/main/named_entity_recognition/recall_estimation/data_generation/amundsen_01/geo_terms.txt)).
Sub populations are created by dividing samples into frequency/ambiguity classes, in which tagger results can differ. 

|Subpopulation | Description | Examples |
|:--- |:---|:---|
|Levinumad | Geographic locations with most frequent suffixes | Niiluse jõgi, Aasovi meri, Peipsi järv |
|Mitmetäheduslikud | Geographic locations with ambigous suffixes | Panama kanal, Panga pank, Kura kurk |
|Ülejäänud | Other/remaining geographic locations | Vaikne ookean, Liivi laht, Tehvandi mägi |

Code for benchmark creation/updating: https://github.com/estnltk/estnltk-model-data/blob/main/named_entity_recognition/recall_estimation/data_generation/amundsen_01
