Package Structure:

```
hora
   !- data       - contains program configuration data, world cities data, marriage compatibility table
         !- ephe - contains swiss ephimeride compressed JPL data
   !- images     - contains images
   !- lang       - contains language resource files
   !- panchanga  - panchanga module to calculate daily panchanga
   !- horoscope
        !- horoscope.py - horoscope package
        !- chart  - chart package
           !- arudhas.py     - arudhas, argala, virodhargal
           !- ashtavarga.py  - ashtavarga, trikona sodhana, ekadhipatya_sodhana, sodhaya pinda
           !- charts.py      - divisional charts, planet combustion, retrograde
           !- house.py       - aspects, drishti,stronger planets/raasi, kaarakas
           !- yoga.py        - 100+ yogas
           !- raja_yoga.py - raja_yoga and its sub-types
        !- dhasa  - dhasa package
           !- ashtottari.py  - ashtottari dhasa-bhuthi
           !- drig.py        - drigdhasa-bhuthi
           !- kalachakra.py  - kalachakra dhasa-bhuthi
           !- moola.py       - moola dhasa-bhuthi
           !- mudda.py  	  - mudda dhasa-bhuthi
           !- narayana.py    - narayana dhasa-bhuthi
           !- nirayana.py    - nirayana dhasa-bhuthi
           !- patyayini.py   - patyayini dhasa-bhuthi
           !- shoola.py      - shoola dhasa-bhuthi
           !- sudasa.py      - sudasa dhasa-bhuthi
           !- sudharsana_chakra.py   - sudharsana_chakra dhasa-bhuthi
           !- vimsottari.py  - vimsottari dhasa-bhuthi
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
