from PyQt6.QtWidgets import QLineEdit, QApplication, QLabel, QHBoxLayout, QVBoxLayout, QPushButton,\
                            QComboBox, QDialog
from PyQt6.QtCore import Qt
from hora import utils
from hora.panchanga import drik
import datetime
_main_window_width = 550
_main_window_height = 150
_CALCULATE_WAIT_MSG = '<b>Calculating... Results will be updated here. Please wait...</b>'
class ConjunctionDialog(QDialog):
    """
        Planetary Conjunction Dialog
    """
    def __init__(self,current_date_jd,place:drik.Place,planet1=6, chart_title='Planetary Conjunctions',
                 entry_type=0,planet2=4,raasi=None):
        """
            Entry Type: 0=> Planetary Conjunctions; 1=> Planet Entry/Transit 2=> Planet Vakra Gathi Change
        """
        super().__init__()
        self._current_date_jd = current_date_jd
        self._conjunction_date_jd = current_date_jd
        self.Place = place
        self._planet1 = planet1
        self._chart_title = chart_title
        self._entry_type = entry_type
        self._accept_clicked = False
        self._separation_angle_index = 0
        if entry_type==0:
            self._planet2 = planet2
        elif entry_type==1:
            self._raasi = raasi
        self.res = utils.resource_strings
        self._create_ui()
    def _create_ui(self):
        v_layout = QVBoxLayout()
        self._current_date_label = QLabel(self.res['current_date_str'])
        y,m,d,fh = utils.jd_to_gregorian(self._current_date_jd)
        hh,mm,ss = utils.to_dms(fh,as_string=False)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self._current_date_label)
        self._year_text = QLineEdit(str(y));h_layout.addWidget(self._year_text)
        self._month_text = QLineEdit(str(m)); h_layout.addWidget(self._month_text)
        self._day_text = QLineEdit(str(d)); h_layout.addWidget(self._day_text)
        self._after_before_combo = QComboBox(); h_layout.addWidget(self._after_before_combo)
        self._after_before_combo.addItems([self.res['after_str'],self.res['before_str']])
        v_layout.addLayout(h_layout)
        h_layout = QHBoxLayout()
        if self._entry_type==0:
            self._sep_angle_combo = QComboBox()
            self._sep_angle_list = self.res['planet_separation_angle_list'].split(',')
            self._sep_angle_combo.addItems(self._sep_angle_list)
            self._sep_angle_combo.setCurrentIndex(0)
            self._separation_angle = self._sep_angle_combo.currentIndex()*30.
            h_layout.addWidget(self._sep_angle_combo)
        self._planet1_combo = QComboBox()
        if self._entry_type==2:
            self._planet1_list = utils.PLANET_NAMES[2:7]
        else:
            self._planet1_list = utils.PLANET_NAMES[:9]
        self._planet1_combo.addItems(self._planet1_list)
        self._planet1_combo.setCurrentIndex(0)
        if utils.PLANET_NAMES[self._planet1] in self._planet1_list:
            self._planet1_combo.setCurrentText(utils.PLANET_NAMES[self._planet1])
        h_layout.addWidget(self._planet1_combo)
        if self._entry_type==0:
            self._planet2_combo = QComboBox()
            self._planet1_combo.currentIndexChanged.connect(self._update_planet2_list)
            self._update_planet2_list()
            h_layout.addWidget(self._planet2_combo)
        elif self._entry_type==1:
            self._raasi_combo = QComboBox()
            self._raasi_combo.addItems([self.res['raasi_str']]+utils.RAASI_LIST)
            h_layout.addWidget(self._raasi_combo)
        v_layout.addLayout(h_layout)
        self._results_text = QLabel(self._after_before_combo.currentText()+'occurs at:')
        self._results_text.setEnabled(False)
        v_layout.addWidget(self._results_text)
        h_layout = QHBoxLayout()
        self._find_button = QPushButton(self.res['compute_str']); h_layout.addWidget(self._find_button)
        self._find_button.clicked.connect(self._calculate_clicked)
        self._accept_button = QPushButton(self.res['accept_str']); h_layout.addWidget(self._accept_button)
        self._accept_button.clicked.connect(self._accept_and_close)
        self._close_button = QPushButton(self.res['cancel_str']); h_layout.addWidget(self._close_button)
        self._close_button.clicked.connect(self._close_dialog)
        v_layout.addLayout(h_layout)
        self.setLayout(v_layout)
        self.setFixedSize(_main_window_width,_main_window_height)
        self.setWindowTitle(self._chart_title)
        self._results_text.setText('')
        self._accept_button.setEnabled(False)
        #self._calculate_clicked()
    def closeEvent(self, *args, **kwargs):
        self._conjunction_date_jd = self._current_date_jd
        QApplication.restoreOverrideCursor()
        return QDialog.closeEvent(self, *args, **kwargs)
    def _update_planet2_list(self):
        self._planet2_combo.clear()
        _planet2_list = utils.PLANET_NAMES[:9]
        _planet2_list.remove(self._planet1_combo.currentText())
        if self._planet1_combo.currentIndex()==7 or self._planet1_combo.currentIndex()==8:
            _planet2_list = _planet2_list[:6]
        self._planet2_combo.addItems(_planet2_list)
        self._planet2_combo.setCurrentIndex(0)
        if utils.PLANET_NAMES[self._planet2] in _planet2_list:
            self._planet2_combo.setCurrentText(utils.PLANET_NAMES[self._planet2])
    def _calculate_clicked(self):
        self._accept_button.setEnabled(False)
        if self._entry_type==0:
            self.setWindowTitle(self.res['planetary_conjunctions_str'])
            self._find_conjunction_date()
        elif self._entry_type==1:
            self.setWindowTitle(self.res['planet_transit_str'])
            self._find_transit_date()
        else:
            self.setWindowTitle(self.res['vakra_gathi_change_str'])
            self._find_retrogression_change_date()
        self._accept_button.setEnabled(True)
    def _find_retrogression_change_date(self):
        from hora import const
        self._results_text.setText(_CALCULATE_WAIT_MSG)
        QApplication.processEvents()
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self._planet1 = utils.PLANET_NAMES.index(self._planet1_combo.currentText())
        panchanga_place = self.Place
        year = int(self._year_text.text()); month = int(self._month_text.text()); day=int(self._day_text.text())
        direction = 1 if self._after_before_combo.currentIndex()==0 else -1
        panchanga_start_date = drik.Date(year,month,day+1*direction)
        cur_jd,ret_sign = drik.next_planet_retrograde_change_date(self._planet1,panchanga_start_date,panchanga_place,direction=direction)
        retStr=''  if ret_sign == 1 else const._retrogade_symbol
        self._conjunction_date_jd = cur_jd
        results = self._planet1_combo.currentText()+' '
        #print(results)
        y,m,d,fh= utils.jd_to_gregorian(cur_jd)
        results += "{0:4d}-{1:2d}-{2:2d}".format(y,m,d)+' '+utils.to_dms(fh,as_string=True)
        results += ' '+utils.PLANET_NAMES[self._planet1]+retStr
        #print(results)
        self._results_text.setText(results)
        # update the year/month/day edit boxes
        self._year_text.setText(str(y)); self._month_text.setText(str(m)); self._day_text.setText(str(d))
        QApplication.restoreOverrideCursor()        
        
    def _find_conjunction_date(self):
        #from datetime import datetime
        self._separation_angle = self._sep_angle_combo.currentIndex()*30.
        #start_time = datetime.now()
        self._results_text.setText(_CALCULATE_WAIT_MSG)
        QApplication.processEvents()
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self._planet1 = utils.PLANET_NAMES.index(self._planet1_combo.currentText())
        self._planet2 = utils.PLANET_NAMES.index(self._planet2_combo.currentText())
        panchanga_place = self.Place
        year = int(self._year_text.text()); month = int(self._month_text.text()); day=int(self._day_text.text())  
        direction = 1 if self._after_before_combo.currentIndex()==0 else -1
        panchanga_start_date = drik.Date(year,month,day+1*direction)
        ret = drik.next_conjunction_of_planet_pair(self._planet1, self._planet2, panchanga_place, panchanga_start_date, direction=direction,separation_angle=self._separation_angle)
        self._separation_angle_index = self._sep_angle_combo.currentIndex()
        if ret==None:
            self._results_text.setText('Could not find planetary conjunctions for sep angle ',self._separation_angle,'  Try increasing search range')
            QApplication.restoreOverrideCursor()
            return
        else:
            cur_jd,p1_long,p2_long = ret
        #end_time = datetime.now()
        #print("Elapsed", (end_time - start_time).total_seconds(),'seconds')
        self._conjunction_date_jd = cur_jd
        results = self._planet1_combo.currentText()+'/'+self._planet2_combo.currentText()+' '
        y,m,d,fh= utils.jd_to_gregorian(cur_jd)
        results += "{0:4d}-{1:2d}-{2:2d}".format(y,m,d)+' '+utils.to_dms(fh,as_string=True)
        results += ' '+self.res['longitude_str']+' '+\
                    utils.PLANET_NAMES[self._planet1]+':'+utils.to_dms(p1_long,is_lat_long='plong')+' ' + \
                    utils.PLANET_NAMES[self._planet2]+':'+utils.to_dms(p2_long,is_lat_long='plong')
        self._results_text.setText(results)
        # update the year/month/day edit boxes
        self._year_text.setText(str(y)); self._month_text.setText(str(m)); self._day_text.setText(str(d))
        QApplication.restoreOverrideCursor()
        return
    def _find_transit_date(self):
        from datetime import datetime
        start_time = datetime.now()
        self._results_text.setText(_CALCULATE_WAIT_MSG)
        QApplication.processEvents()
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self._planet1 = utils.PLANET_NAMES.index(self._planet1_combo.currentText())
        panchanga_place = self.Place
        year = int(self._year_text.text()); month = int(self._month_text.text()); day=int(self._day_text.text())  
        direction = 1 if self._after_before_combo.currentIndex()==0 else -1
        panchanga_start_date = drik.Date(year,month,day)
        self._raasi = None if self._raasi_combo.currentIndex()==0 else self._raasi_combo.currentIndex()
        cur_jd,p1_long = drik.next_planet_entry_date(self._planet1,panchanga_start_date,panchanga_place,
                                                     direction=direction,raasi=self._raasi)
        end_time = datetime.now()
        print("Elapsed", (end_time - start_time).total_seconds(),'seconds')
        self._conjunction_date_jd = cur_jd
        results = self._planet1_combo.currentText()+' '
        #print(results)
        y,m,d,fh= utils.jd_to_gregorian(cur_jd)
        p1_rasi,p1_long = drik.dasavarga_from_long(p1_long, divisional_chart_factor=1)
        results += "{0:4d}-{1:2d}-{2:2d}".format(y,m,d)+' '+utils.to_dms(fh,as_string=True)
        results += ' '+self.res['longitude_str']+' :'+ utils.RAASI_LIST[p1_rasi]+' ' + utils.to_dms(p1_long,is_lat_long='plong')+' '
        #print(results)
        self._results_text.setText(results)
        # update the year/month/day edit boxes
        self._year_text.setText(str(y)); self._month_text.setText(str(m)); self._day_text.setText(str(d))
        QApplication.restoreOverrideCursor()        
    def _accept_and_close(self):
        self._accept_clicked = True
        #y,m,d,fh = utils.jd_to_gregorian(self._conjunction_date_jd)
        #print(y,m,d,utils.to_dms(fh))
        self.accept()
    def _close_dialog(self):
        self._accept_clicked = False
        self.reject()
def show(current_date_jd,place:drik.Place,planet1=6,planet2=4, chart_title='Planetary Conjunctions',entry_type=0):
    import sys
    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    dlg = ConjunctionDialog(current_date_jd,place,planet1,chart_title,entry_type,planet2)
    ret = dlg.exec()
    print('exec return value',ret)
    return ret
if __name__ == "__main__":
    import sys
    def except_hook(cls, exception, traceback):
        print('exception called')
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    lang = 'ta'; utils.set_language(lang)
    App = QApplication(sys.argv)
    jd = utils.julian_day_number((1996,12,7), (10,34,0))
    place = drik.Place('Chennai,India',13.0878,80.2785,5.5)
    _chart_title = 'Planet entry'
    entry_type = 1
    show(jd, place,entry_type=entry_type,chart_title=_chart_title)
    exit()
    chart = ConjunctionDialog(jd,place,entry_type=entry_type)
    chart.show()
    sys.exit(App.exec())

