Package Structure:

```
hora
   !- data       - contains program configuration data, world cities data, marriage compatibility table
         !- ephe - contains swiss ephimeride compressed JPL data
   !- images     - contains images
   !- lang       - contains language resource files
   !- panchanga  - panchanga module to calculate daily panchanga
   		!- drik.py - all panchanga functions such as sunrise to planet positions
   		!- drik1.py - panchanga functions through Calendar Class - !!! NOT FULLY IMPLEMENTED !!!
   		!- khanda_khaadyaka.py - planet positions using khanda khaadyaka method - !!! NOT FULLY IMPLEMENTED !!!
   		!- surya_sidhantha.py - planet positions using surya sidhantha method - !!! NOT FULLY IMPLEMENTED !!!
   		!- vratha.py  - to find speacial vratha days such as amavasya, srartha etc
   !- horoscope
        !- main.py - horoscope package
        !- prediction.py - general predictions
        !- chart  - chart package
           !- arudhas.py     - arudhas, argala, virodhargal
           !- ashtavarga.py  - ashtavarga, trikona sodhana, ekadhipatya_sodhana, sodhaya pinda
           !- charts.py      - divisional charts, planet combustion, retrograde
           !- dosha.py       - doshas
           !- house.py       - aspects, drishti,stronger planets/raasi, kaarakas
           !- raja_yoga.py   - raja_yoga and its sub-types
           !- sphuta.py      - sphutas: tri, chatu, pancha, prana, deha, mrityu, sooshma tri, beeja, kshetra, tithi, yoga, rahu tithi.
           !- strength.py    - Harsha, Pancha Vargeeya, Dwadhasa Vargeeya, Shad bala, Bhava bala
           !- yoga.py        - 100+ yogas
        !- dhasa  - dhasa package
           !- ashtottari.py  - ashtottari dhasa-bhuthi
           !- brahma.py      - brahma dhasa
           !- chara.py       - chara dhasa
           !- chathuraseethi_sama.py - chathura seethi sama dhasa
           !- drig.py        - drigdhasa-bhuthi
           !- dwadasottari.py - dwadasottari dhasa
           !- dwisapathi.py  - dwisatpathi dhasa
           !- kalachakra.py  - kalachakra dhasa-bhuthi
           !- karaka.py      - karaka dhasa
           !- kendradhi_rasi.py - kendradhi rasi dhasa
           !- lagnamsaka.py     - lagnamsaka dhasa
           !- mandooka.py      - mandooka dhasa
           !- moola.py       - moola dhasa-bhuthi
           !- mudda.py  	  - mudda dhasa-bhuthi
           !- naisargika.py  - naisargika dhasa
           !- narayana.py    - narayana dhasa-bhuthi
           !- navamsa.py     - navamsa dhasa-bhuthi
           !- nirayana.py    - nirayana dhasa-bhuthi
           !- padhanadhamsa.py - padhanadhamsa dhasa-bhukthi
           !- panchottari.py - panchottari dhasa-bhukthi
           !- paryaaya.py    - Paryaaya dhsasa-bhukthi
           !- patyayini.py   - patyayini dhasa-bhukthi
           !- sataatbika.py  - sataatbika dhasa-bhukthi
           !- shastihayani.py - shastihayani dhasa-bhukthi
           !- shattrimsa_sama.py - shattrimsa sama dhasa-bhukthi
           !- shodasottari.py - shodasottari dhasa bhukthi
           !- shoola.py      - shoola dhasa-bhukthi
           !- sthira/py      - sthira dhasa bhukthi
           !- sudasa.py      - sudasa dhasa-bhuthi
           !- sudharsana_chakra.py   - sudharsana_chakra dhasa-bhuthi
           !- tara_lagna.py   - tara lagna dhasa-bhuthi
           !- tara.py        - tara dhasa-bhuthi
           !- trikona/py     - trikona dhasa-bhuthi
           !- varnada.py	  - varnada dhasa-bhuthi
           !- vimsottari.py  - vimsottari dhasa-bhuthi
           !- yogardha.py    - yogardha dhasa-bhuthi
           !- yogini.py      - yogini dhasa-bhuthi
        !- match  - marriage compatibility package
           !- compatibility.py  - marriage compatibility
        !- transit  - tajaka package
           !- tajaka.py      - annual, monthly and 60 hour charts, muntha, vargeeya balas, tajaka lord 
           !- tajaka_yoga.py - tajaka yogas
           !- saham.py       - 36 sahams
   !- ui  - user interface package
      !- horo_chart.py         - simple horoscope chart Raasi/Navamsa and calendar information
      !- horo_chart_tabs.py    - horoscope with lot of details
      !- match_ui.py           - ui for marriage compatibility
   !- utils.py             - utility functions
   !- const.py             - constants related to PyHora package        
   !- tests  - unit/integration tests
      !- unit_tests.py           - unit tests for the features based on examples from the book
      !- pvr_tests.py            - Exercise problems from book.
```
