# PropBank semantic roles

This repository contains resources for building a lexicon for [PropBankPreannotator](https://github.com/estnltk/estnltk/blob/75cf224889554f49fdc4576f206eacd3270ef8d3/tutorials/nlp_pipeline/X_miscellaneous/04_propbank_semantic_roles_preannotation.ipynb).

* `01_extract_sem_roles_from_table.py` -- Extracts semantic roles lexicon from a manually crafted semantic roles table (created in the project EKTB75). The input table describes verbs' senses, corresponding semantic roles and morphosyntactic properties of semantic roles, allowing to map semantic roles to their syntactic and morphological features. The resulting lexicon file `'propbank_frames.jl'` is used by PropBankPreannotator on tagging semantic roles. 

* [`02_convert_conllu_to_estnltk_json.ipynb`](02_convert_conllu_to_estnltk_json.ipynb) -- Converts conllu files with semantic role annotations to EstNLTK Text objects, splits into sentences and saves as JSON objects. This is a preprocessing step required for evaluation of PropBankPreannotator's performance.

* [`03_eval_propbank_preannotator_edt_gold.ipynb`](03_eval_propbank_preannotator_edt_gold.ipynb) -- Evaluates  PropBankPreannotator on (JSON format) EDT corpus files. 