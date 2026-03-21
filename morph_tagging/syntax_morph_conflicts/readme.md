## Süntaksi ja morfoloogia konfliktide andmestik

Problem statement

Neuromudelitel põhinevad süntaksimudelid ei arvesta süntaksi ja morfoloogia kooskõlareeglitega. 
Järgenev andmestik on saadud koondkorpuse lausete alamosa verbitransaktsioonide andmebaasi analüüsimisel.
Hiljem on plaanis siia lisada ka kogu koondkorpuse analüüs.

Simple consistency rules

[https://github.com/estnltk/estnltk-model-data/blob/main/morph_tagging/syntax_morph_conflicts/syntax_morph_conflicts.md](https://github.com/estnltk/estnltk-model-data/blob/main/morph_tagging/syntax_morph_conflicts/syntax_morph_conflicts.md)

Dataset description

 - conflicts -- laused koos konflikti asukohaga 
 - conflict_annotations -- need kus on määratud kas morf on õige või mitte 

Töövoog andmestiku saamiseks: [https://github.com/estnltk/syntax_experiments/tree/verb_templates/workflows/004_analysis_of_known_verb_rection_patterns/005_categorizing_syntax_morphology_conflicts](https://github.com/estnltk/syntax_experiments/tree/verb_templates/workflows/004_analysis_of_known_verb_rection_patterns/005_categorizing_syntax_morphology_conflicts)