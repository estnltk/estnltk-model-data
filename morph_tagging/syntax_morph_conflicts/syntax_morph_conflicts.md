## Morfo-süntaksi konfliktid

Siin on toodud hulk süntaksi-morfo konfliktide tabelist leitud konflikte. 

 - *Error rate (transactions)* on antud tüüpi vigade osakaal kõigist antud deprel-i esinemistest transaktsioonide andmebaasis.
 - *Impact (transactions)* on antud tüüpi vigade osakaal kõigist transaktsioonide andmebaasis olevatest tippudest (*transaction head*).
 - *Error rate (syntax-morph conflicts)* on antud tüüpi vigade osakaal kõigist antud deprel-i esinemistest süntaksi-morfoloogia konfliktide tabelis.
 - *Impact (syntax-morph conflicts)* on antud tüüpi vigade osakaal kõigist süntaksi-morfoloogia tabelis olevatest konfliktidest. 
 
Error rate ja impact on skaleeritud 1:100000. 


| description | deprel | case | error rate (transactions) | impact (transactions) | error rate (syntax-morph conflicts) | impact (syntax-morph conflicts)
|---|---|---|---|---|---|---
| kui nsubj ei ole nimetavas/osastavas käändes | nsubj | ^(nom\|part) | 68.2 | 32 | 7865 | 1471
| kui nsubj:cop ei ole nimetavas/osastavas käändes | nsubj:cop | ^(nom\|part) | 10.9 | 0.01 | 3288 | 0.46
| kui obj ei ole nimetavas/omastavas/osastavas käändes| obj | ^(nom\|gen\|part) | 893 | 193.5 | 22765 | 8884
| kui advcl on käändes | advcl | ^0 | 131.7 | 8.7 | 35506 | 399
| kui advmod on käändes | advmod | ^0 | 4.37 | 0.81 | 181.7 | 37.1
| kui xcomp on käändes | xcomp | ^0 | 121 | 10.4 | 34653 | 478.3
| kui obl on nimetavas käändes| obl | nom | 137.8 | 42.6 | 12242 | 1958