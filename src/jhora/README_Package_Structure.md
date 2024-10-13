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
        !- main.py - horoscope package (used mainly by the UI programs)
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
        	! sudharsan_chakra.py - Sudarshana Chakra dhasa-bhukthi
              ! - annual - Annual Dhasa package
                 !- mudda.py  	  - mudda dhasa-bhuthi
                 !- patyayini.py   - patyayini dhasa-bhukthi
              ! - graha - Graha Dhasa package
              	!- aayu.py        - aayu dhasa-bhukthi
                 !- ashtottari.py  - ashtottari dhasa-bhukthi
                 !- buddhi_gathi.py - Buddhi Gathi dhasa bhukthi
                 !- chathuraseethi_sama.py - chathura seethi sama dhasa
                 !- dwadasottari.py - dwadasottari dhasa
                 !- dwisapathi.py  - dwisatpathi dhasa
                 !- kaala.py       - kaala dhasa
                 !- karaka.py      - karaka dhasa
                 !- karana_chathuraseethi_sama.py - karana chathura seethi sama dhasa
                 !- naisargika.py  - naisargika dhasa
                 !- panchottari.py - panchottari dhasa-bhukthi
                 !- saptharishi_nakshathra.py - Saptharishi Nakshathra dhasa-bhukthi
                 !- sataatbika.py  - sataatbika dhasa-bhukthi
                 !- shastihayani.py - shastihayani dhasa-bhukthi (also called Shashti Sama dasa)
                 !- shattrimsa_sama.py - shattrimsa sama dhasa-bhukthi
                 !- shodasottari.py - shodasottari dhasa bhukthi
                 !- tara.py        - tara dhasa-bhuthi
                 !- tithi_ashtottari.py  - tithi ashtottari dhasa-bhuthi
                 !- tithi_yogini.py  - tithi yogini dhasa-bhuthi
                 !- vimsottari.py  - vimsottari dhasa-bhuthi
                 !- yoga_vimsottari.py  - yoga vimsottari dhasa-bhuthi
                 !- yogini.py      - yogini dhasa-bhuthi
           ! - raasi - Raasi Dhasa Package
                 !- brahma.py      - brahma dhasa
                 !- chakra.py       - chakra dhasa
                 !- chara.py       - chara dhasa
                 !- drig.py        - drigdhasa-bhuthi
                 !- kalachakra.py  - kalachakra dhasa-bhuthi
                 !- kendradhi_rasi.py - kendradhi rasi dhasa
                 !- lagnamsaka.py     - lagnamsaka dhasa
                 !- mandooka.py      - mandooka dhasa
                 !- moola.py       - moola dhasa-bhuthi (Also called Lagna Kendradi Rasi Dhasa)
                 !- narayana.py    - narayana dhasa-bhuthi
                 !- navamsa.py     - navamsa dhasa-bhuthi
                 !- nirayana.py    - nirayana dhasa-bhuthi
                 !- padhanadhamsa.py - padhanadhamsa dhasa-bhukthi
                 !- paryaaya.py    - Paryaaya dhsasa-bhukthi
                 !- shoola.py      - shoola dhasa-bhukthi
                 !- sthira/py      - sthira dhasa bhukthi
                 !- sudasa.py      - sudasa dhasa-bhuthi
                 !- tara_lagna.py   - tara lagna dhasa-bhuthi
                 !- trikona/py     - trikona dhasa-bhuthi
                 !- varnada.py	  - varnada dhasa-bhuthi
                 !- yogardha.py    - yogardha dhasa-bhuthi
        !- match  - marriage compatibility package
           !- compatibility.py  - marriage compatibility
        !- prediction  - basic prediction package
           !- general.py  - general prediction - experimental work
           !- longevity.py - longevity predictions - experimental work
           !- naadi_marriage.py - maadi marriage predictions - experimental work
        !- transit  - tajaka package
           !- tajaka.py      - annual, monthly and 60 hour charts, muntha, vargeeya balas, tajaka lord 
           !- tajaka_yoga.py - tajaka yogas
           !- saham.py       - 36 sahams
   !- ui  - user interface package
      !- horo_chart.py         - simple horoscope chart Raasi/Navamsa and calendar information
      !- horo_chart_tabs.py    - horoscope with lot of details
      !- match_ui.py           - ui for marriage compatibility
      !- chart_styles.py       - Widget class for kundali chart style
      !- label_grid.py         - Widget for custom table of QLabels
      !- vakra_gathi.py        - fun plot of retrogession of planet as seen from earth
      !- vratha_finder.py      - Widget for finding vratha dates
      !- conjunction_dialog.py - Widget for finding conjunction dates of planets
   !- utils.py             - utility functions
   !- const.py             - constants related to PyHora package        
   !- tests  - unit/integration tests
      !- unit_tests.py           - unit tests for the features based on examples from the book
      !- pvr_tests.py            - Exercise problems from book.
```
