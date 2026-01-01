#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) Open Astro Technologies, USA.
# Modified by Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid/PyJHora

# This file is part of the "PyJHora" Python library
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import pandas as pd 
from jhora import const, utils
# Column IDs in the match database
_BOY_STAR_COL=0
_BOY_PAD_COL=1
_GIRL_STAR_COL=2
_GIRL_PAD_COL=3
_VARNA_COL=4
_VASIYA_COL=5
_GANA_COL=6
_STAR_COL=7
_YONI_COL=8
_ADHIPATHI_COL=9
_RASI_COL=10
_NADI_COL=11
_SCORE_COL=12
_MAHEN_COL=13
_VEDHA_COL=14
_RAJJU_COL=15
_SHREE_COL=16
_DATABASE_FILE = const.ROOT_DIR+ '/data/all_nak_pad_boy_girl.csv'
_DATABASE_SOUTH_FILE = const.ROOT_DIR+ '/data/all_nak_pad_boy_girl_south.csv' 
count_stars = utils.count_stars
count_rasis = utils.count_rasis
max_compatibility_score = 36
max_compatibility_score_south = 10
compatibility_list_north = ['varna_match_str','vasiya_match_str','gana_match_str','tara_match_str',
                            'yoni_match_str','adhipathi_match_str','raasi_match_str','naadi_match_str']
compatibility_list_south = ['vasiya_match_str','gana_match_str','tara_match_str',
                            'yoni_match_str','adhipathi_match_str','raasi_match_str']
naalu_porutham_list = ['mahendra_match_str','vedha_match_str','rajju_match_str','sthree_dheerga_match_str']
nakshatra_list = ["Ashwini","Bharani","Krittika","Rohini","Mrigshira","Ardra","Punarvasu","Pushya","Ashlesha",
    "Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyestha",
    "Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Satabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati",
    "Abhijit"]
raasi_list=['Mesham','Rishabam','Mithunam','Katakam','Simmam','Kanni','Thulaam','Vrichigam','Dhanusu','Makaram','Kumbam','Meenam']
nakshathra_results = {3.0:'Utthamam',1.5:'Maddhimam',0.0:'Adhamam'}
nakshathra_max_score = 3.0
nakshathra_categories = ['Janma','Sampat','Vipat','Kshem','Pratyari','Sadhak','Vaadh','Mitra','Athi-Mithra']
NakshathraConst = [
            [3.0, 3.0, 1.5, 3.0, 1.5, 3.0, 1.5, 3.0, 3.0],
            [3.0, 3.0, 1.5, 3.0, 1.5, 3.0, 1.5, 3.0, 3.0],
            [1.5, 1.5, 0.0, 1.5, 0.0, 1.5, 0.0, 1.5, 1.5],
            [3.0, 3.0, 1.5, 3.0, 1.5, 3.0, 1.5, 3.0, 3.0],
            [1.5, 1.5, 0.0, 1.5, 0.0, 1.5, 0.0, 1.5, 1.5],
            [3.0, 3.0, 1.5, 3.0, 1.5, 3.0, 1.5, 3.0, 3.0],
            [1.5, 1.5, 0.0, 1.5, 0.0, 1.5, 0.0, 1.0, 1.0],
            [3.0, 3.0, 1.5, 3.0, 1.5, 3.0, 1.5, 3.0, 3.0],
            [3.0, 3.0, 1.5, 3.0, 1.5, 3.0, 1.5, 3.0, 3.0]
            ]
vasiya_raasi_list = [1,3,2,0,1,3,2,0,1,3,2,0]
yoni_mappings = [0,1,2,3,3,4,5,2,5,6,6,7,8,9,8,9,10,10,4,11,12,11,13,0,13,7,1]
yoni_categories = ['Horse','Elephant','Sheep','Serpant','Dog','Cat','Rat','Cow','Buffalo','Tiger','Deer','Monkey','Mongoose','Lion']
""" In South India yoni - Snake/Rat are enemies. In North India they are not """
yoni_enemies_south = [(0,8),(1,13),(2,11),(3,12),(3,6),(4,10),(5,6),(6,3),(6,5),(7,9),(8,0),(9,7),(10,4),(11,2),(12,3),(13,1)]
YoniArray = [
            [4, 2, 2, 3, 2, 2, 2, 1, 0, 1, 1, 3, 2, 1],
            [2, 4, 3, 3, 2, 2, 2, 2, 3, 1, 2, 3, 2, 0],
            [2, 3, 4, 2, 1, 2, 1, 3, 3, 1, 2, 0, 3, 1],
            [3, 3, 2, 4, 2, 1, 1, 1, 1, 2, 2, 2, 0, 2],
            [2, 2, 1, 2, 4, 2, 1, 2, 2, 1, 0, 2, 1, 1],
            [2, 2, 2, 1, 2, 4, 0, 2, 2, 1, 3, 3, 2, 1],
            [2, 2, 1, 1, 1, 0, 4, 2, 2, 2, 2, 2, 1, 2],
            [1, 2, 3, 1, 2, 2, 2, 4, 3, 0, 3, 2, 2, 1],
            [0, 3, 3, 1, 2, 2, 2, 3, 4, 1, 2, 2, 2, 1],
            [1, 1, 1, 2, 1, 1, 2, 0, 1, 4, 1, 1, 2, 1],
            [1, 2, 2, 2, 0, 3, 2, 3, 2, 1, 4, 2, 2, 1],
            [3, 3, 0, 2, 2, 3, 2, 2, 2, 1, 2, 4, 3, 2],
            [2, 2, 3, 0, 1, 2, 1, 2, 2, 2, 2, 3, 4, 2],
            [1, 0, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 2, 4]
            ]
yoni_results = {0:"Worse",1:'Bad',2:'Neutral',3:'Good',4:'Perfect'}
yoni_max_score = 4
mahendra_porutham_array = [4, 7, 10, 13, 16, 19, 22, 25]
#vedha_pair = [[1,18], [2,17], [3,16], [4,15], [5,23], [6,22], [7,21], [8,20],[9,19], [10,27], [11,26], [12,25], [13,24] ]
vedha_pair_sum = [19,28,37]
head_rajju = [5,14,23] # 5, 5+9, 14+9 (5,(9,9))
neck_rajju = [4,6,13,15,22,24] # 4, 4+2, 6+7, 13+2, 15+7, 22+2 (4,(2,7,2,7,2))
stomach_rajju = [3,7,12,16,21,25] # 3, 3+4, 7+5, 12+4, 16+5, 21+4 (3,(4,5,4,5,4))
waist_rajju = [2,8,11,17,20,26] # 2, 2+6, 8+3, 11+6, 17+3, 20+6 (2, (6,3,6,3,6))
foot_rajju = [1,9,10,18,19,27] # 1, 1+8, 9+1, 10+8, 18+1, 19+8 (1, (8,1,8,1,8)
""" Tamil Panchanga style rajju calculations. Both Aaroga or both avaroga is a match. No match if different """
# head rajju same as north india
neck_aaroga_rajju = [413,22] ; neck_avaroga_rajju = [6,15,24]
stomach_aaroga_rajju = [3,12,21] ; stomach_avaroga_rajju = [7,16,25]
waist_aaroga_rajju = [2,11,20] ; waist_avaroga_rajju = [8,17,26]
foot_aaroga_rajju = [1,10,19] ; foot_avaroga_rajju = [9,18,27]

""" Start 1 from foot, 2 to waist 3 to stomach 4 neck and 5 to head
    then downwards from 6-neck, 7-stomach,8-waist,9-foot
    then upwards from 10-foot ...
"""
varna_categories = ['Brahmin','Kshathirya','Vaishya','Shudra']
VarnaArray = [[1, 0, 0, 0], [1, 1, 0, 0], [1, 1, 1, 0], [1, 1, 1, 1]]
varna_results = {0:'Not Matching',1:'Matching'}
varna_max_score = 1
vasiya_categories = ['Chathushpadha','Manava','Jalachara','Vanachara','Keeta']
VasiyaArray  =[ # From Saravali.de
            [2.0, 0.5, 1.0, 0.0, 2.0],
            [0.5, 2.0, 0.0, 0.0, 0.0],
            [1.0, 0.0, 2.0, 2.0, 2.0],
            [0.0, 0.0, 2.0, 2.0, 0.0],
            [1.0, 0.0, 1.0, 0.0, 2.0]]
VasiyaArray_AstroYogi =[ # From astroyogi.com
            [2.0, 1.0, 1.0, 1.5, 1.0],
            [1.0, 2.0, 1.5, 0.0, 1.0],
            [1.0, 1.5, 2.0, 1.0, 1.0],
            [0.0, 0.0, 0.0, 2.0, 0.0],
            [1.0, 1.0, 1.0, 0.0, 2.0]]
vasiya_results = {0.0:'Poor',0.5:"Neutral",1.0:'Good',2.0:'Perfect'}
vasiya_max_score = 2.0
gana_array = [[6, 6, 0], [5, 6, 0], [1, 0, 6]] ## Based on saravali.de (Maitri) Transposed in V3.1.1
gana_results = {0:'Very Bad',1:'Bad',3:'Average',5:'Good',6:'Perfect'}
gana_max_score = 6
gana_south_deva = [1,5,7,8,13,15,17,22,27,]
gana_south_manushya=[2,4,6,8,11,12,20,21,25,26]
gana_south_rakshasa=[3,9,10,14,16,18,19,23,24]
raasi_adhipathi_mappings = [2,5,3,1,0,3,5,2,4,6,6,4]
raasi_adhipathi_array = [
            [5.0, 5.0, 5.0, 4.0, 5.0, 0.0, 0.0],
            [5.0, 5.0, 4.0, 1.0, 4.0, 0.5, 0.5],
            [5.0, 4.0, 5.0, 0.5, 5.0, 3.0, 0.5],
            [4.0, 1.0, 0.5, 5.0, 0.5, 5.0, 4.0],
            [5.0, 4.0, 5.0, 0.5, 5.0, 0.5, 3.0],
            [0.0, 0.5, 3.0, 5.0, 0.5, 5.0, 5.0],
            [0.0, 0.5, 0.5, 4.0, 3.0, 5.0, 5.0]]
raasi_adhipathi_array_south = [
            [0, 0, 0, 0, 1, 0, 0], # Sun has Jupiter as friend(s)
            [0, 0, 0, 1, 1, 0, 0], # Moon => Mercury and Jupiter
            [0, 0, 0, 1, 0, 1, 0], # Mars => Mercury, Venus
            [0, 1, 1, 0, 1, 1, 1], # Mercury => All but Sun
            [1, 1, 0, 1, 0, 1, 1], # Jupiter => All but Mars
            [0, 0, 1, 1, 1, 0, 1], # Venus => All but Sun/Moon
            [0, 0, 0, 1, 1, 1, 0]] # Saturn => Mercury, Juipter and Venus
raasi_adhipathi_results = {0.0:'Very Bad',0.5:'Bad',1.0:'Below Average',3.0:'Above Average',4.0:'Good',5.0:'Perfect'}
raasi_adhipathi_max_score = 5.0
raasi_array = [
            [7, 0, 7, 7, 0, 0, 7, 0, 0, 7, 7, 0],
            [0, 7, 0, 7, 7, 0, 0, 7, 0, 0, 7, 7],
            [7, 0, 7, 0, 7, 7, 0, 0, 7, 0, 0, 7],
            [7, 7, 0, 7, 0, 7, 7, 0, 0, 7, 0, 0],
            [0, 7, 7, 0, 7, 0, 7, 7, 0, 0, 7, 0],
            [0, 0, 7, 7, 0, 7, 0, 7, 7, 0, 0, 7],
            [7, 0, 0, 7, 7, 0, 7, 0, 7, 7, 0, 0],
            [0, 7, 0, 0, 7, 7, 0, 7, 0, 7, 7, 0],
            [0, 0, 7, 0, 0, 7, 7, 0, 7, 0, 7, 7],
            [7, 0, 0, 7, 0, 0, 7, 7, 0, 7, 0, 7],
            [7, 7, 0, 7, 7, 0, 0, 7, 7, 0, 7, 0],
            [0, 7, 7, 0, 0, 7, 0, 0, 7, 7, 0, 7]
    ]
raasi_results = {0:'Not Matching',7:'Matching;'}
raasi_max_score = 7
NadiArray = [[0, 8, 8], [8, 0, 8], [8, 8, 0]]
naadi_results = {0:'Not Matching',8:'Matching;'}
naadi_max_score = 8
""" TODO: Boy/Girl nak number and rasi number to be uniformly in range 1..27 and 1..12 throughout """
class Ashtakoota:
    """
        To compute Marriage compatibility score Ashtakoota system based on boy and girl's birth star
        @param boy_nakshatra_number: boy's nakshatra_list number [1 to 27]
        @param boy_paadham_number: boy's nakshatra_list paadham number [1 to 4]
        @param girl_nakshatra_number: girl's nakshatra_list number [1 to 27]
        @param girl_paadham_number: girl's nakshatra_list paadham number [1 to 4]
    """
    def __init__(self,boy_nakshatra_number:int,boy_paadham_number:int,girl_nakshatra_number:int,girl_paadham_number:int, method:str="North"):
        self.boy_nakshatra_number=boy_nakshatra_number#-1
        self.girl_nakshatra_number=girl_nakshatra_number#-1
        self.boy_paadham_number = boy_paadham_number
        self.girl_paadham_number = girl_paadham_number
        self.boy_raasi_number=self._raasi_from_nakshatra_pada(boy_nakshatra_number, boy_paadham_number)
        self.girl_raasi_number=self._raasi_from_nakshatra_pada(girl_nakshatra_number, girl_paadham_number)
        self.count_from_girl = count_stars(self.girl_nakshatra_number,self.boy_nakshatra_number)
        self.count_from_boy = count_stars(self.boy_nakshatra_number,self.girl_nakshatra_number)
        self.method=method
    def varna_porutham(self):
        """
            To compute varna koota / Varna Porutham for the given boy/girl birth star combination
            Returns the score in the range [0..3]
        """
        # 0=>Brahmin 1=>Kshatriya 2=>Vaishya 3=>Sudra
        # bv/gv =  Rasi mapping of varna
        bv = vasiya_raasi_list ; gv = bv
        bvk = bv[self.boy_raasi_number-1] ; gvk = gv[self.girl_raasi_number-1]
        if 'south' in self.method.lower(): return VarnaArray[gvk][bvk]==1
        return (VarnaArray[gvk][bvk],varna_max_score)
    def _vasiya_porutham_new(self,use_astroyogi_method=False): #vasiya porutham
        chatushpada = lambda n,r,p: \
                        r in [1,2] or \
                        (r==9) and ( (n==20 and p in[3,4]) or (n==21 and p in[1,2]) ) or  \
                        (r==10) and( (n==21 and p in[3,4]) or (n==22 and p in[1,2]) )
        manava = lambda n,r,p: \
                    r in [3,6,7,11] or \
                    (r==9) and ( (n==19) or (n==20 and p in [1,2]) )
        jalachara = lambda n,r,p: \
                    r in [4,12] or \
                    (r==10) and ( (n==22 and p in [3,4])  or (n==23 and p in [1,2])) 
        vanachara = lambda n,r,p: r==5
        keeta = lambda n,r,p: r==8
        if (chatushpada(self.boy_raasi_number,self.boy_nakshatra_number,self.boy_paadham_number)):
            Bvkpoint = 0
        elif (manava(self.boy_raasi_number,self.boy_nakshatra_number,self.boy_paadham_number)):
            Bvkpoint = 1
        elif (jalachara(self.boy_raasi_number,self.boy_nakshatra_number,self.boy_paadham_number)):
            Bvkpoint = 2
        elif (vanachara(self.boy_raasi_number,self.boy_nakshatra_number,self.boy_paadham_number)):
            Bvkpoint = 3
        else: #Keeta
            Bvkpoint = 4
        if (chatushpada(self.girl_raasi_number,self.girl_nakshatra_number,self.girl_paadham_number)):
            Gvkpoint = 0
        elif (manava(self.girl_raasi_number,self.girl_nakshatra_number,self.girl_paadham_number)):
            Gvkpoint = 1
        elif (jalachara(self.girl_raasi_number,self.girl_nakshatra_number,self.girl_paadham_number)):
            Gvkpoint = 2
        elif (vanachara(self.girl_raasi_number,self.girl_nakshatra_number,self.girl_paadham_number)):
            Gvkpoint = 3
        else: #keeta
            Gvkpoint = 4
        if use_astroyogi_method:
            return (VasiyaArray_AstroYogi[Gvkpoint][Bvkpoint],vasiya_max_score)
        else:
            return (VasiyaArray[Gvkpoint][Bvkpoint],vasiya_max_score)
    def vasiya_porutham_south(self):
        vasiya_list = [[4,7],[3,6],[5],[7,8],[6],[2,11],[5,9],[3],[11],[0,10],[0],[9]]
        #print(self.boy_raasi_number-1,self.girl_raasi_number-1,vasiya_list[self.girl_raasi_number-1])
        return (self.boy_raasi_number-1) in vasiya_list[self.girl_raasi_number-1]  
    def vasiya_porutham(self,use_astroyogi_method=False): #vasiya porutham
        """ TODO: Rasi half does not map to exactly patham 1/2 or 3/4. Rasi half is equal to 4.5 paadham precisely. 
            Correct way to do is get rasi longitude and check if less than 15 or greater than 15
            Approximate way without longitude is here below 
            For example - Dhanus/Sagitarius/9 first half is Moola(1-4), Pooradam (1-2)
                        - Dhanus/Sagitarius/9 second half is Pooradam(3-4), Uthiradam (1-2)
            For example - Makaram/Capricorn/10 first half is Uthiradam(3-4), Sravanam (1-2)
                        - Makaram/Capricorn/10 second half is Sravanam (3-4), Kettai (1-2)
        """
        """
            To compute vasya koota / vasiya porutham for the given boy/girl birth star combination
            Returns the score in the range [0.5,0,5,1.0,2.0]
        """
        if 'south' in self.method.lower(): return self.vasiya_porutham_south()
        chatushpada = lambda r,p: r in[1,2] or (r==9 and p in[3,4]) or (r==10 and p in[1,2])
        manava = lambda r,p: r in[3,6,7,11] or (r==9 and p in[1,2])
        vanachara = lambda r: r == 5
        jalachara = lambda r,p: r in[4,12] or (r==10 and p in[3,4])
        keeta = lambda r: r==8
        #Quadruped  Chatushpada
        if (chatushpada(self.boy_raasi_number,self.boy_paadham_number)):
            Bvkpoint = 0
        elif (manava(self.boy_raasi_number,self.boy_paadham_number)):
            Bvkpoint = 1
        elif (jalachara(self.boy_raasi_number,self.boy_paadham_number)):
            Bvkpoint = 2
        elif (vanachara(self.boy_raasi_number)):
            Bvkpoint = 3
        else: #Keeta
            Bvkpoint = 4
        if (chatushpada(self.girl_raasi_number,self.girl_paadham_number)):
            Gvkpoint = 0
        elif (manava(self.girl_raasi_number,self.girl_paadham_number)):
            Gvkpoint = 1
        elif (jalachara(self.girl_raasi_number,self.girl_paadham_number)):
            Gvkpoint = 2
        elif (vanachara(self.girl_raasi_number)):
            Gvkpoint = 3
        else: #keeta
            Gvkpoint = 4
        if use_astroyogi_method:
            return (VasiyaArray_AstroYogi[Gvkpoint][Bvkpoint],vasiya_max_score)
        else:
            return (VasiyaArray[Gvkpoint][Bvkpoint],vasiya_max_score)
    def dina_porutham(self):
        #if self.method.upper()=="SOUTH": return self.dina_porutham_south()
        return self.nakshathra_porutham()
    def tara_porutham(self):
        #if self.method.upper()=="SOUTH": return self.dina_porutham_south()
        return self.nakshathra_porutham()
    def dina_porutham_south(self):
        """
            Ref: vysyamala.com
            To ensure Dhina Porutham, count the stars beginning from the star of the bride and 
            if the counted number is 2,4,6,8,9,11,13,15,18,20,24,26, it is perfectly compatible.
            When both the bride and groom share Rohini, Arudra, Makha, Vishaka, Shravan, Hasta, Revathi stars 
                then the compatibility is said to be Uthamam (highly compatible).
            While the bride and groom have Ashwini, Bharani, Mrigashira, Krittika, Punarvasu, Uttarashada, Chitra and Anuradha 
                the compatibility is said to be Madhyamam( good compatibility)
            When the bride and groom belongs to the same moon sign, then the groom's Birth Star must precede 
            the bride's Birth Star.
            If the count is 27 while Dina Porutham is considered, it is compatible only when te bride and the groom belong 
            to the same moon sign.
            When counted from the bride's Birth Star, if the groom's Birth Star is the 7th then it is called Vatham. 
            Similarly, when counted from groom's Birth Star, if the bride's Birth Star is 22nd then it is called 
            Vinashika-Vatham and Vinashika are not considered to be compatible factors.            
        """
        count = self.count_from_boy# ProKerala reads from Girl - whereas Tamil Panchangam says countr from by star
        if count in [2,4,6,8,9,11,13,15,17,18,20,21,24,25,26]: return True # 17,21,25 are extra in Tamil Panchangam
        exception_dict = {"12":[2,3,4],"14":[1,2,3],"16":[1,2,4]}
        if any([self.girl_nakshatra_number == int(k) and self.girl_paadham_number in vl for k,vl in exception_dict.items()]):
            return True
        if self.girl_nakshatra_number==self.boy_nakshatra_number:
            if self.girl_nakshatra_number in [1,3,5,10,13,15,20,23] and (self.girl_raasi_number < self.boy_raasi_number or self.girl_paadham_number < self.boy_paadham_number):
                return True
            elif self.girl_raasi_number != self.boy_raasi_number and self.boy_raasi_number < self.girl_raasi_number: # Same star diff rasi
                return True
        if self.girl_raasi_number == self.boy_raasi_number and self.boy_nakshatra_number < self.girl_nakshatra_number:
            return True
        exception_22_list = [(4,25),(7,1),(8,2),(10,4),(12,6),(13,7),(14,8),(17,11),(21,15),(25,19),(26,20),(27,21)]
        if (self.boy_nakshatra_number,self.girl_nakshatra_number) in exception_22_list: return True
        return False
    def nakshathra_porutham(self): #dina porutham
        """
            To compute dina / tara koota / nakshathra porutham for the given boy/girl birth star combination
            Returns the score in the range [0, 1.5, 3.0]
        """
        if 'south' in self.method.lower(): return self.dina_porutham_south()
        res = 0.0
        count = self.count_from_girl # (self.boy_nakshatra_number - self.girl_nakshatra_number)

        if (count <= 0):
            count = count + 27
        count = count % 9
        if count in [3,5,7]: #((count % 2) == 0): #V3.1.1
            res += 1.5
        else:
            res += 0
        count = self.count_from_boy #(self.girl_nakshatra_number - self.boy_nakshatra_number)
        if (count <= 0):
            count = count + 27
        count = count % 9
        if count in [3,5,7]: #((count % 2) == 0): #V3.1.1
            res += 1.5
        else:
            res += 0
        return (res,nakshathra_max_score)
    def gana_porutham_south(self):
        if (self.boy_nakshatra_number in gana_south_deva and self.girl_nakshatra_number in gana_south_deva) or \
           ((self.boy_nakshatra_number in gana_south_manushya and self.girl_nakshatra_number in gana_south_manushya) or \
           self.boy_nakshatra_number in gana_south_deva and self.girl_nakshatra_number in gana_south_manushya) or \
           (self.boy_nakshatra_number in gana_south_manushya and self.girl_nakshatra_number in gana_south_deva) or \
           (self.boy_nakshatra_number in gana_south_rakshasa and self.girl_nakshatra_number in gana_south_rakshasa and \
            self.girl_nakshatra_number > const.gana_threshold_south): return True
        return False
    def gana_porutham(self): #Gana Porutham
        """
            To compute gana koota / Gana Porutham for the given boy/girl birth star combination
            method = 1 => South Indian Style - Prokerala.com formula
            method = 2 => North Indian Style - saravali.de formula
            Returns the score in the range [0, 1, 5, 6]
        """
        if 'south' in self.method.lower(): return self.gana_porutham_south()
        boy_gana = self._find_gana(self.boy_nakshatra_number-1)
        girl_gana = self._find_gana(self.girl_nakshatra_number-1)
        return (gana_array[girl_gana][boy_gana],gana_max_score)
    def _find_gana(self,nak):
        gana=-1
        if (nak in [0,4,6,7,12,14,16,21,26]):
            gana= 0 
        elif (nak in [1,3,5,10,11,19,20,24,25]):
            gana= 1 
        elif (nak in [2,8,9,13,15,17,18,22,23]):
            gana= 2
        return gana
    def yoni_porutham_south(self):
        ga = yoni_mappings[self.girl_nakshatra_number-1] ; ba = yoni_mappings[self.boy_nakshatra_number-1]
        return not any([(ga,ba)==(a,e) for a,e in yoni_enemies_south])
    def yoni_porutham(self): # Yoni Porutham
        """
            To compute yoni koota / Yoni Porutham for the given boy/girl birth star combination
            Returns the score in the range [0..4]
        """
        if 'south' in self.method.lower(): return self.yoni_porutham_south()
        return (YoniArray[yoni_mappings[self.girl_nakshatra_number-1]][yoni_mappings[self.boy_nakshatra_number-1]],yoni_max_score)
    def maitri_porutham(self):
        #if self.method.upper()=="SOUTH": return self.raasi_adhipathi_porutham_south()
        return self.raasi_adhipathi_porutham()
    def raasi_adhipathi_porutham_south(self): #Raasi adhipathi porutham
        """
            To compute maitri koota / Raasi adhipathi porutham for the given boy/girl birth star combination
            Returns the score in the range [0, 0.5, 1.0, 3.0, 4.0, 5.0]
        """
        return raasi_adhipathi_array_south[raasi_adhipathi_mappings[self.girl_raasi_number-1]][raasi_adhipathi_mappings[self.boy_raasi_number-1]]==1
    def raasi_adhipathi_porutham(self): #Raasi adhipathi porutham
        """
            To compute maitri koota / Raasi adhipathi porutham for the given boy/girl birth star combination
            Returns the score in the range [0, 0.5, 1.0, 3.0, 4.0, 5.0]
        """
        if 'south' in self.method.lower(): return self.raasi_adhipathi_porutham_south()
        return (raasi_adhipathi_array[raasi_adhipathi_mappings[self.girl_raasi_number-1]][raasi_adhipathi_mappings[self.boy_raasi_number-1]],raasi_adhipathi_max_score)
    def bahut_porutham(self):
        #if self.method.upper()=="SOUTH": return self.raasi_porutham_south()
        return self.raasi_porutham()
    def raasi_porutham_south(self):
        return count_rasis(self.girl_raasi_number, self.boy_raasi_number) > const.raasi_threshold_south
    def raasi_porutham(self): # Raasi Porutham
        """
            To compute bahut koota / Raasi Porutham for the given boy/girl birth star combination
            Returns the score in the range [0 or 7]
        """
        if 'south' in self.method.lower(): return self.raasi_porutham_south()
        return (raasi_array[self.girl_raasi_number-1][self.boy_raasi_number-1],raasi_max_score)
    def naadi_porutham(self):
        """
            To compute naadi koota for the given boy/girl birth star combination
            Returns the score in the range [0 or 8]
        """
        bvk = [0,1,2,2,1,0,0,1,2,2,1,0,0,1,2,2,1,0,0,1,2,2,1,0,0,1,2] ; gvk = bvk
        bv = bvk[self.boy_nakshatra_number-1] ; gv = gvk[self.girl_nakshatra_number-1]
        if 'south' in self.method.lower(): return NadiArray[bv][gv]==8
        return (NadiArray[bv][gv],naadi_max_score)
    def mahendra_porutham_south(self):
        return self.mahendra_porutham()
    def mahendra_porutham(self):
        """
            Mahendra Prutham: good) when the boy’s birth star is in the positions 
                4th, 7th, 10th, 13th, 16th, 19th, 22nd and 25th from that of the girl’s birth star
            To compute mahendra porutham for the given boy/girl birth star combination
            Returns the score as True or False
        """
        rem = self.count_from_girl #((self.boy_nakshatra_number + 27 - self.girl_nakshatra_number) % 27)+1
        return rem in mahendra_porutham_array
    def vedha_porutham_south(self):
        return self.vedha_porutham()
    def vedha_porutham(self):
        """
            To compute vedha porutham for the given boy/girl birth star combination
            Returns the score as True or False
        """
        bn = self.boy_nakshatra_number
        gn = self.girl_nakshatra_number
        vedha = not (bn+gn in vedha_pair_sum)
        return vedha
    def rajju_porutham(self):
        """
            If the stars of both the girl and the boy are found to be represent the same portion of the body 
            such as head for both or a foot for both then it signifies that 
            there is no agreement between the stars.
            Ref: prokerala.com
            To compute rajju porutham for the given boy/girl birth star combination
            Returns the score as True or False
        """
        if 'south' in self.method.lower(): return self.rajju_porutham_south()
        bn = self.boy_nakshatra_number
        gn = self.girl_nakshatra_number
        rp = (bn in head_rajju) and (gn in head_rajju) or \
             (bn in neck_rajju) and (gn in neck_rajju) or \
             (bn in stomach_rajju) and (gn in stomach_rajju) or \
             (bn in waist_rajju) and (gn in waist_rajju) or \
             (bn in foot_rajju) and (gn in foot_rajju)
        return not rp
    def rajju_porutham_south(self):
        bn = self.boy_nakshatra_number
        gn = self.girl_nakshatra_number
        bn_aaroga = bn in neck_aaroga_rajju+foot_aaroga_rajju+waist_aaroga_rajju+stomach_aaroga_rajju
        gn_aaroga = gn in neck_aaroga_rajju+foot_aaroga_rajju+waist_aaroga_rajju+stomach_aaroga_rajju
        if (bn_aaroga and not gn_aaroga) or (gn_aaroga and not bn_aaroga) : return True
        rp = (bn in head_rajju) and (gn in head_rajju) or \
             (bn in neck_rajju) and (gn in neck_rajju) or \
             (bn in stomach_rajju) and (gn in stomach_rajju) or \
             (bn in waist_rajju) and (gn in waist_rajju) or \
             (bn in foot_rajju) and (gn in foot_rajju)
        return not rp
    def sthree_dheerga_porutham_south(self):
        """
            If the count of the boy’s birth star from the girl’s birth star exceeds 15, then it is a good
            To compute sthree dheerga porutham for the given boy/girl birth star combination
            Returns the score as True or False
        """
        return self.count_from_girl > const.sthree_dheerga_threshold_south
        #return ((self.boy_nakshatra_number + 27 - self.girl_nakshatra_number) % 27)+1 > const.sthree_dheerga_threshold # V3.0.6
    def sthree_dheerga_porutham(self):
        """
            If the count of the boy’s birth star from the girl’s birth star exceeds 15, then it is a good
            To compute sthree dheerga porutham for the given boy/girl birth star combination
            Returns the score as True or False
        """
        if 'south' in self.method.lower(): return self.sthree_dheerga_porutham_south()
        return self.count_from_girl > const.sthree_dheerga_threshold
        #return ((self.boy_nakshatra_number + 27 - self.girl_nakshatra_number) % 27)+1 > const.sthree_dheerga_threshold # V3.0.6
    """
    def compatibility_score_south(self):
        varna_porutham = False
        vasiya_porutham = self.vasiya_porutham_south()
        gana_porutham = self.gana_porutham_south()
        dina_porutham = self.dina_porutham_south() # nakshathra_porutham is same as tara porutham
        yoni_porutham = self.yoni_porutham_south()
        raasi_adhipathi_porutham= self.raasi_adhipathi_porutham_south()
        raasi_porutham= self.raasi_porutham_south()
        naadi_porutham = False
        mahendra_porutham=self.mahendra_porutham_south()
        vedha_porutham=self.vedha_porutham_south()
        rajju_porutham=self.rajju_porutham_south()
        sthree_dheerga_porutham=self.sthree_dheerga_porutham_south()
        compatibility_score = sum([dina_porutham,gana_porutham,mahendra_porutham,sthree_dheerga_porutham,yoni_porutham,\
                                     raasi_porutham,raasi_adhipathi_porutham,vasiya_porutham,rajju_porutham,vedha_porutham])
        return [varna_porutham, vasiya_porutham, gana_porutham, dina_porutham, yoni_porutham, \
                raasi_adhipathi_porutham, raasi_porutham, naadi_porutham,compatibility_score, \
                mahendra_porutham,vedha_porutham,rajju_porutham,sthree_dheerga_porutham]
    """
    def compatibility_score(self):
        """
            To computer total ashta koota score (sum of all eight porutham values)
            Return score ranges from 0 to 36 in steps of 0.5
            @return returns the following values as a list:
            varna_porutham, vasiya_porutham, gana_porutham, nakshathra_porutham, 
            yoni_porutham, raasi_adhipathi_porutham, bahkut_porutham, naadi_porutham,
            compatibility_score,
            mahendra_porutham,vedha_porutham,rajju_porutham,sthree_dheerga_porutham]
        """
        varna_porutham = self.varna_porutham()
        vasiya_porutham = self.vasiya_porutham()
        gana_porutham = self.gana_porutham()
        dina_porutham = self.dina_porutham() # nakshathra_porutham is same as tara porutham
        yoni_porutham = self.yoni_porutham()
        raasi_adhipathi_porutham= self.raasi_adhipathi_porutham()
        raasi_porutham= self.raasi_porutham()
        naadi_porutham = self.naadi_porutham()
        mahendra_porutham=self.mahendra_porutham()
        vedha_porutham=self.vedha_porutham()
        rajju_porutham=self.rajju_porutham()
        sthree_dheerga_porutham=self.sthree_dheerga_porutham()
        def _is_there_minimum_tamil_porutham(skip_varna_checking=const.skip_using_girls_varna_for_minimum_tamil_porutham): # V4.5.5
            if skip_varna_checking: # V4.5.5
                return rajju_porutham and dina_porutham and gana_porutham and raasi_porutham and yoni_porutham
            girl_varna = vasiya_raasi_list[self.girl_raasi_number-1]
            minimum_porutham = rajju_porutham
            if girl_varna==0:
                minimum_porutham = minimum_porutham and dina_porutham
            elif girl_varna==1:
                minimum_porutham = minimum_porutham and gana_porutham
            elif girl_varna==2:
                minimum_porutham = minimum_porutham and raasi_porutham
            else:
                minimum_porutham = minimum_porutham and yoni_porutham
            return minimum_porutham
        if 'south' in self.method.lower():
            compatibility_score = sum([dina_porutham,gana_porutham,mahendra_porutham,sthree_dheerga_porutham,yoni_porutham,\
                                         raasi_porutham,raasi_adhipathi_porutham,vasiya_porutham,rajju_porutham,vedha_porutham])
            minimum_porutham = _is_there_minimum_tamil_porutham()
            return [varna_porutham, vasiya_porutham, gana_porutham, dina_porutham, yoni_porutham, \
                    raasi_adhipathi_porutham, raasi_porutham, naadi_porutham,compatibility_score, \
                    mahendra_porutham,vedha_porutham,rajju_porutham,sthree_dheerga_porutham,minimum_porutham]
        else:
            compatibility_score = varna_porutham[0]+vasiya_porutham[0]+gana_porutham[0]+dina_porutham[0]+yoni_porutham[0]+raasi_adhipathi_porutham[0]+raasi_porutham[0]+naadi_porutham[0]
            return [varna_porutham[0], vasiya_porutham[0], gana_porutham[0], dina_porutham[0], yoni_porutham[0], \
                raasi_adhipathi_porutham[0], raasi_porutham[0], naadi_porutham[0],compatibility_score, \
                mahendra_porutham,vedha_porutham,rajju_porutham,sthree_dheerga_porutham]
    def _raasi_from_nakshatra_pada(self,nakshatra_number,paadha_number):
        nakshatra_duration = 360/27.
        raasi_duration = 360/12.
#        print('nakshatra_duration',nakshatra_duration)
        paadha_duration = nakshatra_duration / 4.
#        print('paadha_duration',paadha_duration)
        total_duration = ((nakshatra_number-1)*nakshatra_duration)+((paadha_number-1)*paadha_duration)+0.5*paadha_duration
#        print('total_duration',total_duration)
        raasi_number = int(total_duration / raasi_duration)+1
#        print('nakshatra_list'+nakshatra_list[nakshatra_number-1]+' paadham-'+str(paadha_number)+' is raasi_list',raasi_list[raasi_number-1])
        return raasi_number
def update_compatibility_database(method='North'):
    import codecs, csv
    outFile = _DATABASE_FILE#'all_nak_pad_boy_girl.csv'
    if 'south' in method.lower():
        outFile = _DATABASE_SOUTH_FILE#'all_nak_pad_boy_girl_south.csv'
    fp = codecs.open(outFile, encoding='utf-8', mode='w')
    csv_writer = csv.writer(fp)
    for bn in range(27):
        for bp in range(4):
            for gn in range(27):
                for gp in range(4):
                    a = Ashtakoota(bn+1,bp+1,gn+1,gp+1,method=method)
                    results = [bn+1,bp+1,gn+1,gp+1]+ a.compatibility_score()
                    print('processing',bn+1,bp+1,gn+1,gp+1,results)
                    #print(results, file=fp)
                    csv_writer.writerow(results)
    fp.close()
class Match:    
    def __init__(self,boy_nakshatra_number:int=None,boy_paadham_number:int=None,girl_nakshatra_number:int=None,girl_paadham_number:int=None, \
                 minimum_score:float=const.compatibility_minimum_score_north,check_for_mahendra_porutham:bool=False,check_for_vedha_porutham:bool=False,check_for_rajju_porutham:bool=False,\
                 check_for_shreedheerga_porutham:bool=False,method="North"):
        db_file = _DATABASE_FILE
        self.minimum_score = minimum_score
        if 'south' in method.lower(): 
            db_file = _DATABASE_SOUTH_FILE
            self.minimum_score = const.compatibility_minimum_score_south
        if os.path.exists(db_file):
            self.data_file = db_file
        else:
            Exception("database file:"+db_file+" not found.")
        self.match_db=pd.read_csv(db_file,header=None,encoding='utf-8')
        self._gender = 'Female'
        self.boy_nakshatra_number = boy_nakshatra_number
        self.boy_paadham_number = boy_paadham_number
        self.girl_nakshatra_number = girl_nakshatra_number
        self.girl_paadham_number = girl_paadham_number
        #self.minimum_score = minimum_score
        self.check_for_mahendra_porutham = check_for_mahendra_porutham
        self.check_for_vedha_porutham = check_for_vedha_porutham
        self.check_for_rajju_porutham = check_for_rajju_porutham
        self.check_for_shreedheerga_porutham= check_for_shreedheerga_porutham
    def get_matching_partners(self):
        boy_nak_given = self.boy_nakshatra_number is not None and self.boy_nakshatra_number >=1 and self.boy_nakshatra_number <=27
        boy_pad_given = self.boy_paadham_number is not None and self.boy_paadham_number >=1 and self.boy_paadham_number <=4
        #boy_info_given = boy_nak_given or boy_pad_given 
        girl_nak_given = self.girl_nakshatra_number is not None and self.girl_nakshatra_number >=1 and self.girl_nakshatra_number <=27
        girl_pad_given = self.girl_paadham_number is not None and self.girl_paadham_number >=1 and self.girl_paadham_number<=4
        #girl_info_given = girl_nak_given or girl_pad_given
        #print(boy_nak_given,boy_pad_given,girl_nak_given,girl_pad_given,self.minimum_score,\
        #      self.check_for_mahendra_porutham,self.check_for_vedha_porutham,self.check_for_rajju_porutham,self.check_for_shreedheerga_porutham)
        search_criteria = (self.match_db[_SCORE_COL]>=self.minimum_score)
        if boy_nak_given:
            self._gender = 'Male'
            search_criteria = search_criteria & (self.match_db[_BOY_STAR_COL]==self.boy_nakshatra_number)
            if boy_pad_given:
                search_criteria = search_criteria & (self.match_db[_BOY_PAD_COL]==self.boy_paadham_number)
        if girl_nak_given:
            self._gender = 'Female'
            search_criteria = search_criteria & (self.match_db[_GIRL_STAR_COL]==self.girl_nakshatra_number)
            if girl_pad_given:
                search_criteria = search_criteria & (self.match_db[_GIRL_PAD_COL]==self.girl_paadham_number)
        #print('search_results',self.match_db.index[search_criteria].tolist())
        if self.check_for_mahendra_porutham==True:
            search_criteria  = search_criteria & (self.match_db[_MAHEN_COL]==self.check_for_mahendra_porutham)
            #print('mahen search_results',self.match_db.index[search_criteria].tolist())
        if self.check_for_vedha_porutham==True:
            search_criteria = search_criteria & (self.match_db[_VEDHA_COL]==self.check_for_vedha_porutham)
            #print('vedha search_results',self.match_db.index[search_criteria].tolist())
        if self.check_for_rajju_porutham==True:
            search_criteria = search_criteria & (self.match_db[_RAJJU_COL]==self.check_for_rajju_porutham)
            #print('rajju search_results',self.match_db.index[search_criteria].tolist())
        if self.check_for_shreedheerga_porutham==True:
            search_criteria = search_criteria & (self.match_db[_SHREE_COL]==self.check_for_shreedheerga_porutham)
        temp_results = self.match_db.index[search_criteria].tolist()
        #print('after shree dheerga temp_results',temp_results)
        temp_partners = []
        for n1 in temp_results:
            if self._gender.lower()=='male':
                p1 = self.match_db.iloc[n1][_GIRL_PAD_COL]
                nak =  self.match_db.iloc[n1][_GIRL_STAR_COL]
            else:
                p1 = self.match_db.iloc[n1][_BOY_PAD_COL]
                nak =  self.match_db.iloc[n1][_BOY_STAR_COL]
            #if temp_partners and nak==temp_partners[-1][0]:
            #    temp_partners[-1] = (temp_partners[-1][0],temp_partners[-1][1],p1,temp_partners[-1][3])
            #else:
            temp_partners.append((nak,p1,n1)) 
        #print('temp_partners',temp_partners)
        matching_partners = []
        for nak,p1,idx in temp_partners:
            ettu_porutham_results = list(self.match_db.iloc[idx][_VARNA_COL:_SCORE_COL])
            compatibility_score = self.match_db.iloc[idx][_SCORE_COL]
            naalu_porutham_results = list(self.match_db.iloc[idx][_MAHEN_COL:])
            #print(nak,p1,naalu_porutham_results)
            matching_partners.append((nak,p1,ettu_porutham_results,compatibility_score,naalu_porutham_results)) 
        #print(len(matching_partners),' matching stars found for',self.boy_nakshatra_number,self.boy_paadham_number,self.girl_nakshatra_number,self.girl_paadham_number,\
        #      self.check_for_mahendra_porutham,self.check_for_vedha_porutham,self.check_for_rajju_porutham,self.check_for_shreedheerga_porutham)
        return matching_partners
if __name__ == "__main__":
    #m = Match(girl_nakshatra_number=15,girl_paadham_number=1,method='South')
    #print(m.get_matching_partners())
    #exit()
    a = Ashtakoota(13,1,2,1,method='South')
    print(a.compatibility_score())
    exit()
    update_compatibility_database()
    update_compatibility_database('South')
    exit()
    for bn in range(1,28):
        for bp in range(1,5):
            for gn in range(1,28):
                for gp in range(1,5):
                    a = Ashtakoota(bn,1,gn,1)
                    d1 = a.yoni_porutham()
                    d2 = a.yoni_porutham_south()
                    print(bn,bp,gn,gp,str(d1[0] in [1,2,3,4]).upper(),str(d2).upper())
    exit() 
    boy_nakshatra_number = 12
    boy_paadham_number = 3
    girl_nakshatra_number = 15
    girl_paadham_number = 1
    """
    check_for_mahendra_porutham=True
    check_for_vedha_porutham=True
    check_for_rajju_porutham=True
    check_for_shreedheerga_porutham=True
    m = Match(boy_nakshatra_number=boy_nakshatra_number,boy_paadham_number=boy_paadham_number,girl_nakshatra_number=girl_nakshatra_number,girl_paadham_number=girl_paadham_number,\
              check_for_mahendra_porutham=check_for_mahendra_porutham,check_for_vedha_porutham=check_for_vedha_porutham,\
              check_for_rajju_porutham=check_for_rajju_porutham,check_for_shreedheerga_porutham=check_for_shreedheerga_porutham)
    mp = m.get_matching_partners()
    print(mp)
    """
    ak = Ashtakoota(boy_nakshatra_number,boy_paadham_number,girl_nakshatra_number,girl_paadham_number)
    print('mahendra',ak.mahendra_porutham())
    print('shree deerga',ak.sthree_dheerga_porutham())
    print('rajju',ak.rajju_porutham())
    print('vedha',ak.vedha_porutham())
    print('varna_porutham',ak.varna_porutham())
    print('vasiya_porutham',ak.vasiya_porutham())
    print('vasiya_porutham new',ak._vasiya_porutham_new())
    print('tara/dina/nakshatra',ak.nakshathra_porutham())
    print('yoni',ak.yoni_porutham())
    print('maitri/raasi adhipathi',ak.raasi_adhipathi_porutham())
    print('gana',ak.gana_porutham())
    print('bahut',ak.raasi_porutham())
    print('naadi',ak.naadi_porutham())
    print()
    exit()
    a = Ashtakoota(boy_nakshatra_number,boy_paadham_number,girl_nakshatra_number,girl_paadham_number)
    ettu_porutham_results,compatibility_score,naalu_porutham_results = a.compatibility_score()
    ettu_poruthham_list = ['varna porutham', 'vasiya porutham', 'gana porutham', 'nakshathra porutham', 'yoni porutham', 'adhipathi porutham', 'raasi porutham', 'naadi porutham']
    naalu_porutham_list = ['mahendra porutham','vedha porutham','rajju porutham','sthree dheerga porutham']
    format_str = '%-40s%-20s%-20s'#\n'
    for p,porutham in enumerate(ettu_poruthham_list):
        print(format_str % (porutham,str(ettu_porutham_results[p][0]),str(ettu_porutham_results[p][1])))
    for p,porutham in enumerate(naalu_porutham_list):
        print(format_str % (porutham,str(naalu_porutham_results[p]),''))
    print(format_str % ('Overall Compatibility Score:', str(compatibility_score) +' out of '+ str(max_compatibility_score),''))
    exit()
