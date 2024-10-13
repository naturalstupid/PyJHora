#### Compatibility - Class and Functions
##### Import
```
import os
import string
import numpy as np
import pandas as pd 
```
##### class Ashtakoota
    """
        To compute Marriage compatibility score Ashtakoota system based on boy and girl's birth star
        @param boy_nakshatra_number: boy's nakshatra_list number [1 to 27]
        @param boy_paadham_number: boy's nakshatra_list paadham number [1 to 4]
        @param girl_nakshatra_number: girl's nakshatra_list number [1 to 27]
        @param girl_paadham_number: girl's nakshatra_list paadham number [1 to 4]
    """
##### Methods
##### varna\_porutham()
    """
        To compute varna koota / Varna Porutham for the given boy/girl birth star combination
        Returns the score in the range [0..3]
    """
##### vasiya\_porutham()
    """
        To compute vasya koota / vasiya porutham for the given boy/girl birth star combination
        Returns the score in the range [0.5,0,5,1.0,2.0]
    """
##### nakshathra\_porutham()
    """
        To compute dina / tara koota / nakshathra porutham for the given boy/girl birth star combination
        Returns the score in the range [0, 1.5, 3.0]
    """
##### gana\_porutham()
    """
        To compute gana koota / Gana Porutham for the given boy/girl birth star combination
        Returns the score in the range [0, 1, 5, 6]
    """
##### yoni\_porutham()
    """
        To compute yoni koota / Yoni Porutham for the given boy/girl birth star combination
        Returns the score in the range [0..4]
    """
##### raasi\_adhipathi\_porutham()
    """
        To compute maitri koota / Raasi adhipathi porutham for the given boy/girl birth star combination
        Returns the score in the range [0, 0.5, 1.0, 3.0, 4.0, 5.0]
    """
##### raasi\_porutham()
    """
        To compute bahut koota / Raasi Porutham for the given boy/girl birth star combination
        Returns the score in the range [0 or 7]
    """
##### naadi\_porutham()
    """
        To compute naadi koota for the given boy/girl birth star combination
        Returns the score in the range [0 or 8]
    """
##### mahendra\_porutham()
    """
        To compute mahendra porutham for the given boy/girl birth star combination
        Returns the score as True or False
    """
##### vedha\_porutham()
    """
        To compute vedha porutham for the given boy/girl birth star combination
        Returns the score as True or False
    """
##### rajju\_porutham()
    """
        To compute rajju porutham for the given boy/girl birth star combination
        Returns the score as True or False
    """
##### sthree\_dheerga\_porutham()
    """
        To compute sthree dheerga porutham for the given boy/girl birth star combination
        Returns the score as True or False
    """
##### compatibility\_score()
```
    To computer total ashta koota score (sum of all eight porutham values)
    Return score ranges from 0 to 36 in steps of 0.5
    @return returns the following values as a list:
    [varna_porutham, vasiya_porutham, gana_porutham, nakshathra_porutham, 
    yoni_porutham, raasi_adhipathi_porutham, bahkut_porutham, naadi_porutham,
    compatibility_score,
    mahendra_porutham,vedha_porutham,rajju_porutham,sthree_dheerga_porutham]
```
##### class Match
##### Parameters
```
	boy_nakshatra_number : int = None
	boy_paadham_number : int = None
	girl_nakshatra_number : int=None
	girl_paadham_number : int=None
	minimum_score : float=18.0 
	check_for_mahendra_porutham : bool=True
	check_for_vedha_porutham : bool=True
	check_for_rajju_porutham : bool=True
   check_for_shreedheerga_porutham : bool=True
```
##### Methods
##### get\_matching\_partners()

