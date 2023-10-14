import os
import string
import numpy as np
import pandas as pd 

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
_DATABASE_FILE = '../data/all_nak_pad_boy_girl.csv'

max_compatibility_score = 36
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
yoni_mappings = [0,1,2,3,3,4,5,2,5,
                  6,6,7,8,9,8,9,10,10,
                  4,11,12,11,13,0,13,7,1,
                  12]
yoni_categories = ['Horse','Elephant','Sheep','Serpant','Dog','Cat','Rat','Cow','Buffalo','Tiger','Deer','Monkey','Mongoose','Lion']
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
head_rajju = [5,14,23] # 5, 5+9, 14+9 (5,(9))
neck_rajju = [4,6,13,15,22,24] # 4, 4+2, 6+7, 13+2, 15+7, 22+2 (4,(2,7,2,7,2))
stomach_rajju = [3,7,12,16,21,25] # 3, 3+4, 7+5, 12+4, 16+5, 21+4 (3,(4,5,4,5,4))
waist_rajju = [2,8,11,17,20,26] # 2, 2+6, 8+3, 11+6, 17+3, 20+6 (2, (6,3,6,3,6))
foot_rajju = [1,9,10,18,19,27] # 1, 1+8, 9+1, 10+8, 18+1, 19+8 (1, (8,1,8,1,8)
varna_categories = ['Brahmin','Kshathirya','Vaishya','Shudra']
VarnaArray = [[1, 0, 0, 0], [1, 1, 0, 0], [1, 1, 1, 0], [1, 1, 1, 1]]
varna_results = {0:'Not Matching',1:'Matching'}
varna_max_score = 1
vasiya_categories = ['Chathushpadha','Manava','Jalachara','Vanachara','Keeta']
VasiyaArray  =[
            [2.0, 0.5, 1.0, 0.0, 2.0],
            [0.5, 2.0, 0.0, 0.0, 0.0],
            [1.0, 0.0, 2.0, 2.0, 2.0],
            [0.0, 0.0, 2.0, 2.0, 0.0],
            [1.0, 0.0, 1.0, 0.0, 2.0]]
vasiya_results = {0.0:'Poor',0.5:"Neutral",1.0:'Good',2.0:'Perfect'}
vasiya_max_score = 2.0
gana_array = [[6, 5, 1], [6, 6, 0], [0, 0, 6]] ## Based on saravali.de (Maitri)
gana_results = {0:'Very Bad',1:'Bad',3:'Average',5:'Good',6:'Perfect'}
gana_max_score = 6
raasi_adhipathi_mappings = [2,5,3,1,0,3,5,2,4,6,6,4]
raasi_adhipathi_array = [
            [5.0, 5.0, 5.0, 4.0, 5.0, 0.0, 0.0],
            [5.0, 5.0, 4.0, 1.0, 4.0, 0.5, 0.5],
            [5.0, 4.0, 5.0, 0.5, 5.0, 3.0, 0.5],
            [4.0, 1.0, 0.5, 5.0, 0.5, 5.0, 4.0],
            [5.0, 4.0, 5.0, 0.5, 5.0, 0.5, 3.0],
            [0.0, 0.5, 3.0, 5.0, 0.5, 5.0, 5.0],
            [0.0, 0.5, 0.5, 4.0, 3.0, 5.0, 5.0]]
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
class Ashtakoota:
    """
        To compute Marriage compatibility score Ashtakoota system based on boy and girl's birth star
        @param boy_nakshatra_number: boy's nakshatra_list number [1 to 27]
        @param boy_paadham_number: boy's nakshatra_list paadham number [1 to 4]
        @param girl_nakshatra_number: girl's nakshatra_list number [1 to 27]
        @param girl_paadham_number: girl's nakshatra_list paadham number [1 to 4]
    """
    def __init__(self,boy_nakshatra_number,boy_paadham_number,girl_nakshatra_number,girl_paadham_number):
        self.boy_nakshatra_number=boy_nakshatra_number-1
        self.girl_nakshatra_number=girl_nakshatra_number-1
        self.boy_paadham_number = boy_paadham_number
        self.girl_paadham_number = girl_paadham_number
        self.boy_raasi_number=self._raasi_from_nakshatra_pada(boy_nakshatra_number, boy_paadham_number)
        self.girl_raasi_number=self._raasi_from_nakshatra_pada(girl_nakshatra_number, girl_paadham_number)
    def varna_porutham(self): # Varna Porutham
        """
            To compute varna koota / Varna Porutham for the given boy/girl birth star combination
            Returns the score in the range [0..3]
        """
        Bvkpoint = 3
        Gvkpoint = 3
        if (self.boy_raasi_number in [4,8,12]):
            Bvkpoint = 0 # Brahmin
        elif (self.boy_raasi_number in [1,5,9]):
            Bvkpoint = 1 #Kshatriya
        elif (self.boy_raasi_number in [2,6,10]):
            Bvkpoint = 2 # Vaishya
        if (self.girl_raasi_number in [4,8,12]):
            Gvkpoint = 0 # Brahmin
        elif (self.girl_raasi_number in [1,5,9]):
            Gvkpoint = 1 # Kshatriya
        elif (self.girl_raasi_number in [2,6,10]):
            Gvkpoint = 2 # Vaishya
#        print(Gvkpoint,Bvkpoint,VarnaArray[Gvkpoint][Bvkpoint])
        return (VarnaArray[Gvkpoint][Bvkpoint],varna_max_score)

    def vasiya_porutham(self): #vasiya porutham
        """
            To compute vasya koota / vasiya porutham for the given boy/girl birth star combination
            Returns the score in the range [0.5,0,5,1.0,2.0]
        """
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
#        print(Gvkpoint,Bvkpoint,VasiyaArray[Gvkpoint][Bvkpoint])
        return (VasiyaArray[Gvkpoint][Bvkpoint],vasiya_max_score)
    def nakshathra_porutham(self): #dina porutham
        """
            To compute dina / tara koota / nakshathra porutham for the given boy/girl birth star combination
            Returns the score in the range [0, 1.5, 3.0]
        """
        res = 0.0
        count = (self.boy_nakshatra_number - self.girl_nakshatra_number)

        if (count <= 0):
            count = count + 27
        count = count % 9
        if ((count % 2) == 0):
            res += 1.5
        else:
            res += 0
        count = (self.girl_nakshatra_number - self.boy_nakshatra_number)
        if (count <= 0):
            count = count + 27
        count = count % 9
        if ((count % 2) == 0):
            res += 1.5
        else:
            res += 0
        return (res,nakshathra_max_score)
    def gana_porutham(self): #Gana Porutham
        """
            To compute gana koota / Gana Porutham for the given boy/girl birth star combination
            Returns the score in the range [0, 1, 5, 6]
        """
        boy_gana = self._find_gana(self.boy_nakshatra_number)
        girl_gana = self._find_gana(self.girl_nakshatra_number)
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
    def yoni_porutham(self): # Yoni Porutham
        """
            To compute yoni koota / Yoni Porutham for the given boy/girl birth star combination
            Returns the score in the range [0..4]
        """
        return (YoniArray[yoni_mappings[self.girl_nakshatra_number]][yoni_mappings[self.boy_nakshatra_number]],yoni_max_score)
    def raasi_adhipathi_porutham(self): #Raasi adhipathi porutham
        """
            To compute maitri koota / Raasi adhipathi porutham for the given boy/girl birth star combination
            Returns the score in the range [0, 0.5, 1.0, 3.0, 4.0, 5.0]
        """
        return (raasi_adhipathi_array[raasi_adhipathi_mappings[self.girl_raasi_number-1]][raasi_adhipathi_mappings[self.boy_raasi_number-1]],raasi_adhipathi_max_score)
    def raasi_porutham(self): # Raasi Porutham
        """
            To compute bahut koota / Raasi Porutham for the given boy/girl birth star combination
            Returns the score in the range [0 or 7]
        """
        return (raasi_array[self.girl_raasi_number-1][self.boy_raasi_number-1],raasi_max_score)
    def naadi_porutham(self):
        """
            To compute naadi koota for the given boy/girl birth star combination
            Returns the score in the range [0 or 8]
        """
        bv = 2
        gv = 2 
        if (self.boy_nakshatra_number in [0,5,6,11,12,17,18,23,24]):
            bv = 0
        if (self.girl_nakshatra_number in [0,5,6,11,12,17,18,23,24]):
            gv = 0
        if (self.boy_nakshatra_number in [1,4,7,10,13,16,19,22,25]):
            bv = 1
        if (self.girl_nakshatra_number in [1,4,7,10,13,16,19,22,25]):
            gv = 1
        return (NadiArray[gv][bv],naadi_max_score)
    def mahendra_porutham(self):
        """
            To compute mahendra porutham for the given boy/girl birth star combination
            Returns the score as True or False
        """
        rem = (self.girl_nakshatra_number + 27 - self.boy_nakshatra_number) % 27
        return rem in mahendra_porutham_array        
    def vedha_porutham(self):
        """
            To compute vedha porutham for the given boy/girl birth star combination
            Returns the score as True or False
        """
        bn = self.boy_nakshatra_number+1
        gn = self.girl_nakshatra_number+1
        vedha = not (bn+gn in vedha_pair_sum)
        return vedha
    def rajju_porutham(self):
        """
            To compute rajju porutham for the given boy/girl birth star combination
            Returns the score as True or False
        """
        bn = self.boy_nakshatra_number+1
        gn = self.girl_nakshatra_number+1
        if (bn in head_rajju) and (gn in head_rajju):
            return False
        elif (bn in neck_rajju) and (gn in neck_rajju):
            return False
        elif (bn in stomach_rajju) and (gn in stomach_rajju):
            return False
        elif (bn in waist_rajju) and (gn in waist_rajju):
            return False
        elif (bn in foot_rajju) and (gn in foot_rajju):
            return False
        else:
            return True
    def sthree_dheerga_porutham(self):
        """
            To compute sthree dheerga porutham for the given boy/girl birth star combination
            Returns the score as True or False
        """
        return ( (self.boy_nakshatra_number + 27 - self.girl_nakshatra_number) % 27 > 13) # > 9)
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
        vasya_porutham = self.vasiya_porutham()
        gana_porutham = self.gana_porutham()
        nakshathra_porutham = self.nakshathra_porutham() # nakshathra_porutham is same as tara porutham
        yoni_porutham = self.yoni_porutham()
        raasi_adhipathi_porutham= self.raasi_adhipathi_porutham()
        raasi_porutham= self.raasi_porutham()
        naadi_porutham = self.naadi_porutham()
        compatibility_score = varna_porutham[0]+vasya_porutham[0]+gana_porutham[0]+nakshathra_porutham[0]+yoni_porutham[0]+raasi_adhipathi_porutham[0]+raasi_porutham[0]+naadi_porutham[0]
        mahendra_porutham=self.mahendra_porutham()
        vedha_porutham=self.vedha_porutham()
        rajju_porutham=self.rajju_porutham()
        sthree_dheerga_porutham=self.sthree_dheerga_porutham()
        return [varna_porutham, vasya_porutham, gana_porutham, nakshathra_porutham, yoni_porutham, raasi_adhipathi_porutham, raasi_porutham, naadi_porutham],compatibility_score,[mahendra_porutham,vedha_porutham,rajju_porutham,sthree_dheerga_porutham]
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
def _generate_full_compatability_matrix():
  import codecs
  outFile = 'all_nak_pad_boy_girl.txt'
  fp = codecs.open(outFile, encoding='utf-8', mode='w')
  for bn in range(27):
      for bp in range(4):
          for gn in range(27):
              for gp in range(4):
                  a = Ashtakoota(bn+1,bp+1,gn+1,gp+1)
                  # [total,m,v,r,s] = a.compatibility_score()[8:]
                  results = a.compatibility_score()
                  print('processing',bn+1,bp+1,gn+1,gp+1)
                  print([bn+1,bp+1,gn+1,gp+1],results, file=fp)
  fp.close()
class Match:    
    def __init__(self,boy_nakshatra_number:int=None,boy_paadham_number:int=None,girl_nakshatra_number:int=None,girl_paadham_number:int=None, \
                 minimum_score:float=18.0,check_for_mahendra_porutham:bool=True,check_for_vedha_porutham:bool=True,check_for_rajju_porutham:bool=True,\
                 check_for_shreedheerga_porutham:bool=True):
        db_file = _DATABASE_FILE
        if os.path.exists(db_file):
            self.data_file = db_file
        else:
            Exception("database file:"+db_file+" not found.")
        _world_city_db_df=pd.read_csv(db_file,header=None,encoding='utf-8')
        self.match_db = _world_city_db_df
        self._gender = 'Female'
        self.boy_nakshatra_number = boy_nakshatra_number
        self.boy_paadham_number = boy_paadham_number
        self.girl_nakshatra_number = girl_nakshatra_number
        self.girl_paadham_number = girl_paadham_number
        self.minimum_score = minimum_score
        self.check_for_mahendra_porutham = check_for_mahendra_porutham
        self.check_for_vedha_porutham = check_for_vedha_porutham
        self.check_for_rajju_porutham = check_for_rajju_porutham
        self.check_for_shreedheerga_porutham= check_for_shreedheerga_porutham
    def get_matching_partners(self):
        boy_nak_given = self.boy_nakshatra_number != None and self.boy_nakshatra_number >=0 and self.boy_nakshatra_number <27
        boy_pad_given = self.boy_paadham_number != None and self.boy_paadham_number >=0 and self.boy_paadham_number <4
        boy_info_given = boy_nak_given or boy_pad_given 
        girl_nak_given = self.girl_nakshatra_number != None and self.girl_nakshatra_number >=0 and self.girl_nakshatra_number <27
        girl_pad_given = self.girl_paadham_number != None and self.girl_paadham_number >-0 and self.girl_paadham_number<4
        girl_info_given = girl_nak_given or girl_pad_given
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
        if self.check_for_mahendra_porutham==True:
            search_criteria  = search_criteria & (self.match_db[_MAHEN_COL]==self.check_for_mahendra_porutham)
        if self.check_for_vedha_porutham==True:
            search_criteria = search_criteria & (self.match_db[_VEDHA_COL]==self.check_for_vedha_porutham)
        if self.check_for_rajju_porutham==True:
            search_criteria = search_criteria & (self.match_db[_RAJJU_COL]==self.check_for_rajju_porutham)
        if self.check_for_shreedheerga_porutham==True:
            search_criteria = search_criteria & (self.match_db[_SHREE_COL]==self.check_for_shreedheerga_porutham)
        temp_results = self.match_db.index[search_criteria].tolist()
        temp_partners = []
        for n1 in temp_results:
            if self._gender.lower()=='male':
                p1 = self.match_db.iloc[n1][_GIRL_PAD_COL]
                nak =  self.match_db.iloc[n1][_GIRL_STAR_COL]
            else:
                p1 = self.match_db.iloc[n1][_BOY_PAD_COL]
                nak =  self.match_db.iloc[n1][_BOY_STAR_COL]
            if temp_partners and nak==temp_partners[-1][0]:
                temp_partners[-1] = (temp_partners[-1][0],temp_partners[-1][1],p1,temp_partners[-1][3])
            else:
                temp_partners.append((nak,p1,p1,n1)) 
        results = []
        matching_partners = []
        for nak,p1,p2,idx in temp_partners:
            ettu_porutham_results = list(self.match_db.iloc[idx][_VARNA_COL:_SCORE_COL])
            compatibility_score = self.match_db.iloc[idx][_SCORE_COL]
            naalu_porutham_results = list(self.match_db.iloc[idx][_MAHEN_COL:])
            matching_partners.append((nak,p1,p2,ettu_porutham_results,compatibility_score,naalu_porutham_results)) 
        print(len(matching_partners),' matching stars found for',self.boy_nakshatra_number,self.boy_paadham_number,self.girl_nakshatra_number,self.girl_paadham_number,\
              self.check_for_mahendra_porutham,self.check_for_vedha_porutham,self.check_for_rajju_porutham,self.check_for_shreedheerga_porutham)
        return matching_partners
if __name__ == "__main__":
    #_generate_full_compatability_matrix()
    #exit()
    boy_nakshatra_number = None
    boy_paadham_number = None
    girl_nakshatra_number = 15
    girl_paadham_number = 1
    check_for_mahendra_porutham=False
    check_for_vedha_porutham=False
    check_for_rajju_porutham=False
    check_for_shreedheerga_porutham=False
    m = Match(boy_nakshatra_number=boy_nakshatra_number,boy_paadham_number=boy_paadham_number,girl_nakshatra_number=girl_nakshatra_number,girl_paadham_number=girl_paadham_number,\
              check_for_mahendra_porutham=check_for_mahendra_porutham,check_for_vedha_porutham=check_for_vedha_porutham,\
              check_for_rajju_porutham=check_for_rajju_porutham,check_for_shreedheerga_porutham=check_for_shreedheerga_porutham)
    mp = m.get_matching_partners()
    mpl = len(mp)
    #print(mpl,' matching stars found for',boy_nakshatra_number,boy_paadham_number,girl_nakshatra_number,girl_paadham_number,check_for_mahendra_porutham,check_for_vedha_porutham,check_for_rajju_porutham,check_for_shreedheerga_porutham)
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
