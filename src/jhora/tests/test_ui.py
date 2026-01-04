import sys, os
import datetime
from PyQt6.QtWidgets import (QApplication, QWidget, QGridLayout, QPushButton, QCompleter, QMessageBox,
                            QLineEdit, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QDialog)
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QPoint, pyqtSlot
from jhora.panchanga import drik, pancha_paksha
from jhora import utils, const
from PyQt6.QtGui import QFont, QFontMetrics, QPainter, QColor, QPen, QPixmap, QIcon, QKeyEvent
from jhora.ui.panchangam import PanchangaInfoDialog

_SHOW_MUHURTHA_OR_SHUBHA_HORA = 1 # 0=Muhurtha 1=Shubha Hora
_sunrise_icon = os.path.abspath(const._IMAGES_PATH) + const._sep + "sunrise1.png"
_sunset_icon = os.path.abspath(const._IMAGES_PATH) + const._sep + "sunset1.png"
_pournami_icon = os.path.abspath(const._IMAGES_PATH) + const._sep + "pournami.png"
_amavasai_icon = os.path.abspath(const._IMAGES_PATH) + const._sep + "amavasai.png"
_shukla_paksha_icon = os.path.abspath(const._IMAGES_PATH) + const._sep + "shukla_paksha.png"
_krishna_paksha_icon = os.path.abspath(const._IMAGES_PATH) + const._sep + "krishna_paksha.png"
_info_label1_font_size = 6#8
_info_label2_font_size = 6 if _SHOW_MUHURTHA_OR_SHUBHA_HORA==1 else 5
_info_label3_font_size =6#8
_ICON_SIZE = 12
_top_left_font_size = 9; _top_right_font_size = 9
_bottom_left_font_size = 9; _bottom_right_font_size = 9
_center_left_font_size = 12; _center_right_font_size = 16
_calendar_cell_width = 100;_calendar_cell_height = 80 
_label_offset_x = 2; _label_offset_y = 1
#_info_label1_font_size = 6
_info_label1_width = 325
_HEADER_CELL_HEIGHT = 20; _HEADER_COLOR='green'; _HEADER_LABEL_COLOR = 'maroon'
_KEY_COLOR = 'brown'; _VALUE_COLOR = 'blue'
_KEY_LENGTH=50; _VALUE_LENGTH=50; _HEADER_LENGTH=100
_HEADER_FORMAT_ = '<b><span style="color:'+_HEADER_COLOR+';">{:.'+str(_HEADER_LENGTH)+'}</span></b><br>'
_KEY_VALUE_FORMAT_ = '<span style="color:'+_KEY_COLOR+';">{:.'+str(_KEY_LENGTH)+'}</span><span style="color:'+\
        _VALUE_COLOR+';">{:.'+str(_VALUE_LENGTH)+'}</span><br>'
previous_month_color = "orange"; default_color = "lightyellow"
input_day_color = "lightgreen"; next_month_color = "lightblue"
_top_left_label_color = 'magenta'; _top_right_label_color = 'blue'
_middle_left_label_color = 'red'; _middle_right_label_color = 'black'
_bottom_left_label_color = 'green'; _bottom_right_label_color = 'blue'
_cell_border_line_color = 'brown'; _cell_border_line_thickness = 1

class CustomLabel(QLabel):
    clicked = pyqtSignal()  # Signal for click event

    def __init__(self, parent=None):
        super().__init__(parent)
        self.texts = {}
        self.font_sizes = {
            "top_left": _top_left_font_size, "top_right": _top_right_font_size,
            "middle_left":_center_left_font_size,"middle_right": _center_right_font_size,
            "bottom_left": _bottom_left_font_size, "bottom_right": _bottom_right_font_size ,
            "center":_center_right_font_size
        }
        self.colors = {
            "top_left": QColor(_top_left_label_color), "top_right": QColor(_top_right_label_color),
            "middle_left": QColor(_middle_left_label_color),"middle_right": QColor(_middle_right_label_color),
            "bottom_left": QColor(_bottom_left_label_color), "bottom_right": QColor(_bottom_right_label_color),
            "center":QColor(_middle_right_label_color),
        }
        self.setStyleSheet("border: "+str(_cell_border_line_thickness)+"px solid "+_cell_border_line_color+";")
    def set_texts(self, text_pos):
        """Set texts at specified positions."""
        self.texts = text_pos
        self.update()

    def paintEvent(self, event):
        try:
            super().paintEvent(event)
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QColor(Qt.GlobalColor.black))
            for pos, value in self.texts.items():
                alignment = self.get_alignment(pos)
                cell_width = self.width() // 2
                cell_height = self.height() // 3
                cell_x = (0 if 'left' in pos else self.width() // 2)
                cell_y = (0 if 'top' in pos else self.height() // 3 if 'middle' in pos else 2 * self.height() // 3)
                cell_y = self.height()//2 if 'center' in pos else cell_y
                # Adjust the size of the bounding rect to ensure it fully fits within the grid cell
                text_rect = QRect(cell_x, cell_y, cell_width, cell_height)
                rect = QRect(cell_x+_label_offset_x,cell_y+_label_offset_y,
                             text_rect.width()-_label_offset_x,text_rect.height()-_label_offset_y
                             )
                # Set font size based on position
                font = painter.font()
                font_size = self.font_sizes.get(pos, 9)
                pen_color = self.colors.get(pos,QColor('black')); painter.setPen(pen_color)
                font.setPointSize(font_size); font.setBold(True)
                painter.setFont(font)
                # Check if the value is a tuple (icon_path, text)
                if isinstance(value, tuple):
                    icon_path, text = value
                    icon = QPixmap(icon_path).scaled(_ICON_SIZE, _ICON_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    icon_rect = QRect(cell_x, cell_y, _ICON_SIZE, _ICON_SIZE)
                    painter.drawPixmap(icon_rect, icon)
                    rect.setLeft(icon_rect.right())  # Add some space between icon and text
                else:
                    text = value
                painter.drawText(rect, int(alignment), str(text))
                painter.setPen(QPen())
            painter.end()
        except Exception as e:
            print(f"VedicCalendar: CustomLabel paintEvent - An error occurred: {e}")
    
    def get_alignment(self, pos):
        if "top" in pos:
            vertical = Qt.AlignmentFlag.AlignTop
        elif "bottom" in pos:
            vertical = Qt.AlignmentFlag.AlignBottom
        else:
            vertical = Qt.AlignmentFlag.AlignVCenter
            
        if "left" in pos:
            horizontal = Qt.AlignmentFlag.AlignLeft
        elif "right" in pos:
            horizontal = Qt.AlignmentFlag.AlignRight
        else:
            horizontal = Qt.AlignmentFlag.AlignHCenter
            
        return horizontal | vertical

    def mousePressEvent(self, event):
        self.clicked.emit()  # Emit signal when label is clicked

class VedicCalendar(QWidget):
    def __init__(self,start_date:drik.Date=None,place:drik.Place=None, language='ta',use_purnimanta_system=None,
                 use_world_city_database=const.check_database_for_world_cities,
                 use_internet_for_location_check=const.use_internet_for_location_check):
        """
            @param use_purnimanta_system: None => Solar Calendar, False=>Amantha, True=>Purnimantha 
        """
        super().__init__()
        self._language = language
        self.use_world_city_database = use_world_city_database
        utils.set_language(const.available_languages[language])
        utils.use_database_for_world_cities(self.use_world_city_database)
        self.use_internet_for_location_check = use_internet_for_location_check
        self._use_purnimanta_system = use_purnimanta_system
        self.res = utils.resource_strings
        self.start_date = start_date; self.start_place=place
        self.selected_cell = None; self.previous_month_cell=None; self.next_month_cell=None
        self.setWindowTitle(self.res['calendar_str']+' '+const._APP_VERSION)
        self.setWindowIcon(QIcon(const._IMAGE_ICON_PATH))
        self.col_min = 0; self.row_min = 0; self.col_max = 6; self.row_max = 6
        self.initUI()
        self.setFocus()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        if self.start_date is None:
            current_date_str = datetime.datetime.now().strftime('%Y,%m,%d')
        else:
            year,month,day = self.start_date
            current_date_str = str(year)+','+str(month)+','+str(day)
        self.date_text = QLineEdit(self)
        self.date_text.setFixedWidth(100)
        self.date_text.setText(current_date_str)
        self.date_text.editingFinished.connect(self.computeCalendar)
        if self.start_place is None and self.use_internet_for_location_check:
            loc = utils.get_place_from_user_ip_address()
            print('loc from IP address',loc)
            if len(loc)==4:
                print('setting values from loc')
                self.start_place = drik.Place(loc[0],loc[1],loc[2],loc[3])
        self._place_text = QLineEdit(self)
        self._place_text.setFixedWidth(150)
        completer = QCompleter(utils.world_cities_dict.keys())
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._place_text.setCompleter(completer)
        self._place_text.textChanged.connect(self._resize_place_text_size)
        if self.use_internet_for_location_check: self._place_text.editingFinished.connect(lambda: self._get_location(self._place_text.text()))
        self._place_text.setToolTip('Enter place of birth, country name')
        self._lat_text = QLineEdit(self)
        self._lat_text.setFixedWidth(80)
        self._long_text = QLineEdit(self)
        self._long_text.setFixedWidth(80)
        self._tz_text = QLineEdit(self)
        self._tz_text.setFixedWidth(80)
        if isinstance(self.start_place,drik.Place):
            self._place_text.setText(self.start_place.Place)
            self._lat_text.setText(str(self.start_place.latitude))
            self._long_text.setText(str(self.start_place.longitude))
            self._tz_text.setText(str(self.start_place.timezone))
        self._dob_label = QLabel('Date:')
        input_layout.addWidget(self._dob_label)
        input_layout.addWidget(self.date_text)
        self._place_label = QLabel('Place Name:')
        input_layout.addWidget(self._place_label)
        input_layout.addWidget(self._place_text)
        self._lat_label = QLabel('Latitude:')
        input_layout.addWidget(self._lat_label)
        input_layout.addWidget(self._lat_text)
        self._long_label = QLabel('Longitude:')
        input_layout.addWidget(self._long_label)
        input_layout.addWidget(self._long_text)
        self._tz_label = QLabel('TimeZone Hours:')
        input_layout.addWidget(self._tz_label)
        input_layout.addWidget(self._tz_text)
        self._lang_combo = QComboBox()
        self._lang_combo.addItems(const.available_languages.keys())
        self._lang_combo.setCurrentText(self._language)
        self._lang_combo.activated.connect(self._change_language)
        self._lang_combo.setToolTip('Choose language for display')
        input_layout.addWidget(self._lang_combo)
        self._calendar_combo = QComboBox()
        _calendar_list = [self.res[s]+' '+self.res['calendar_str'] for s in ['solar_str','amantha_str','purnimantha_str']]
        self._calendar_combo.addItems(_calendar_list)
        self._calendar_combo.activated.connect(self._change_language)
        _calendar_index = 0 if self._use_purnimanta_system is None else (2 if self._use_purnimanta_system else 1)
        self._calendar_combo.setCurrentIndex(_calendar_index)
        input_layout.addWidget(self._calendar_combo)
        self.compute_btn = QPushButton(self.res['calendar_str'], self)
        self.compute_btn.clicked.connect(self.computeCalendar)
        input_layout.addWidget(self.compute_btn)

        main_layout.addLayout(input_layout)

        h_layout = QHBoxLayout()
        self._info_label1 = QLabel("Information:")
        self._info_label1.setFixedWidth(_info_label1_width)
        self._info_label1.setStyleSheet("border: 1px solid black; font-size: "+str(_info_label1_font_size)+" pt")
        # Use setTextFormat and setTextInteractionFlags to make the link clickable
        self._info_label1.setTextFormat(Qt.TextFormat.RichText)
        self._info_label1.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self._info_label1.setOpenExternalLinks(False)  # Disable opening links in the default browser
        h_layout.addWidget(self._info_label1)
        v_layout = QVBoxLayout()
        self.header_label = QLabel('')
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_label.setStyleSheet("border: 1px solid black; font-weight: bold; font-size: "+str(12)+"pt")
        v_layout.setSpacing(0); v_layout.setContentsMargins(0,0,0,0)
        v_layout.addWidget(self.header_label)
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.cells = []; self.jd = []

        headers = ['<b><span style="color:'+_HEADER_COLOR+';">'+str(h)+'</span></b>' for h in utils.DAYS_SHORT_NAMES]
        self.day_labels = ['' for _ in utils.DAYS_SHORT_NAMES]
        for col, header in enumerate(headers):
            self.day_labels[col] = QLabel(header)
            self.day_labels[col].setFixedHeight(_HEADER_CELL_HEIGHT)  # Set a fixed height for the header
            self.day_labels[col].setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center align the text
            _cell_style = "border: "+str(_cell_border_line_thickness)+"px solid "+_cell_border_line_color+";"
            self.day_labels[col].setStyleSheet(_cell_style)
            self.grid_layout.addWidget(self.day_labels[col], 0, col)

        for row in range(1, 8):
            week = []; jd_week = []
            for col in range(7):
                cell = CustomLabel(self)
                cell.setMinimumSize(_calendar_cell_width, _calendar_cell_height)
                cell.setVisible(False)
                cell.clicked.connect(lambda r=row, c=col: self.cell_clicked(r, c))
                self.grid_layout.addWidget(cell, row, col)
                week.append(cell); jd_week.append(None)
            self.cells.append(week); self.jd.append(jd_week)

        v_layout.addLayout(self.grid_layout)
        h_layout.addLayout(v_layout)
        main_layout.addLayout(h_layout)
        self.move(50,50)
        self.setLayout(main_layout)
        self.computeCalendar()
    def keyPressEvent(self, event: QKeyEvent):
        _DEBUG_ = False
        try:
            row_min = self.row_min; row_max = self.row_max; col_min = self.col_min; col_max = self.col_max
            def _check_if_valid_cell(next_cell):
                next_row,next_col = next_cell
                _, previous_month_col = self.previous_month_cell
                _, next_month_col = self.next_month_cell
                _invalid_cell = (next_row == row_min and next_col < previous_month_col) or \
                                (next_row == row_max and next_col > next_month_col) or \
                                (next_row < row_min or next_row > row_max) or \
                                (next_col < col_min or next_col > col_max)
                return not _invalid_cell
            current_row,current_col = self.selected_cell
            next_cell = self.selected_cell
            if event.key() == Qt.Key.Key_Up:
                next_cell = (current_row-1,current_col) if current_row != row_min else (row_max,current_col)
            elif event.key() == Qt.Key.Key_Down:
                next_cell = (current_row+1,current_col) if current_row != row_max else (row_min,current_col)
            elif event.key() == Qt.Key.Key_Left:
                next_cell = (current_row,current_col-1) if current_col != col_min else (current_row-1,col_max)
            elif event.key() == Qt.Key.Key_Right:
                next_cell = (current_row,current_col+1) if current_col != col_max else (current_row+1,col_min)
            else:
                super().keyPressEvent(event)
            if _check_if_valid_cell(next_cell):
                next_row,next_col = next_cell
                self.cell_clicked(next_row+1, next_col) 
        except Exception as e:
            tb = sys.exc_info()[2]
            print(f"VedicCalendar:keyEventPressed: - An error occurred: {e}",'line number',tb.tb_lineno)
    @pyqtSlot(str)
    def _on_show_more_link_clicked(self, link,jd, place):
        if link == "show_more":
            try:
                _info_dialog = QDialog(self) 
                _info_dialog.setWindowTitle(self.res['panchangam_str'])
                dialog_layout = QVBoxLayout()
                from jhora.ui import panchangam
                panchangam._SHOW_SPECIAL_TITHIS = True
                panchanga_widget = PanchangaInfoDialog(language=self._language,jd=jd,place=place)
                dialog_layout.addWidget(panchanga_widget)
                _info_dialog.setLayout(dialog_layout)
                _info_dialog.exec()
            except Exception as e:
                print(f"VedicCalendar:_on_show_more_link_clicked: An error occurred: {e}")
    def _change_language(self):
        self._language = self._lang_combo.currentText()
        _calendar_index = self._calendar_combo.currentIndex()
        if _calendar_index ==0:
            self._use_purnimanta_system = None
        elif _calendar_index ==1:
            self._use_purnimanta_system = False
        else: #_calendar_index ==2:
            self._use_purnimanta_system = True
        
        utils.set_language(const.available_languages[self._language])
        self.res = utils.resource_strings
        self.setWindowTitle(self.res['calendar_str']+' '+const._APP_VERSION)
        self.computeCalendar()
        
    def _reshade_cells(self):
        for row in range(7):
            for col in range(7):
                cell = self.cells[row][col]
                if cell.isVisible():
                    _cell_style = "border: "+str(_cell_border_line_thickness)+"px solid "+_cell_border_line_color+"; "
                    if (row,col)==self.selected_cell:
                        _cell_style +=  f"background-color: {input_day_color}"
                    elif (row,col)==self.previous_month_cell:
                        _cell_style +=  f"background-color: {previous_month_color}"
                    elif (row,col)==self.next_month_cell:
                        _cell_style +=  f"background-color: {next_month_color}"
                    else:
                        _cell_style +=  f"background-color: {default_color}"
                    cell.setStyleSheet(_cell_style)
    def _resize_place_text_size(self):
        pt = self._place_text.text()
        f = QFont("", 0)
        fm = QFontMetrics(f)
        pw = fm.boundingRect(pt).width()
        ph = fm.height()
        self._place_text.setFixedSize(pw, ph)
        self._place_text.adjustSize()

    def _get_location(self, place_name):
        #print('get_location',place_name)
        result = utils.get_location(place_name)
        #print('RESULT', result)
        if result:
            self._place_name, self._latitude, self._longitude, self._time_zone = result
            self._place_text.setText(self._place_name)
            self._lat_text.setText(str(self._latitude))
            self._long_text.setText(str(self._longitude))
            self._tz_text.setText(str(self._time_zone))
            #print(self._place_name, self._latitude, self._longitude, self._time_zone)
        else:
            msg = place_name + " could not be found in OpenStreetMap.\nTry entering latitude and longitude manually.\nOr try entering nearest big city"
            print(msg)
            QMessageBox.about(self, "City not found", msg)
            self._lat_text.setText('')
            self._long_text.setText('')
        self._resize_place_text_size()

    def _get_days_panchanga_info(self,row,col):
        jd = self.jd[row][col]
        if jd is not None:
            place = self.start_place; y,m,d,_ = utils.jd_to_gregorian(jd); date_in = drik.Date(y,m,d)
            _tithi_returned = drik.tithi(jd, place); _tit = _tithi_returned[0]
            _tithi_icon = _pournami_icon if (_tit==15 or (len(_tithi_returned)>3 and _tithi_returned[3]==15))\
                    else (_amavasai_icon if (_tit==30 or (len(_tithi_returned)>3 and _tithi_returned[3]==30))\
                    else '' )
            _tithi = utils.TITHI_SHORT_LIST[_tit-1]
            _paksha = 0 if _tit<=15 else  1
            kp_icon = _shukla_paksha_icon if _paksha==0 else  _krishna_paksha_icon
            _srise = utils.to_dms(drik.sunrise(jd, place)[0],round_to_minutes=True).strip()
            _sset = utils.to_dms(drik.sunset(jd, place)[0],round_to_minutes=True).strip()
            _nak = utils.NAKSHATRA_SHORT_LIST[drik.nakshatra(jd, place)[0]-1]
            _lang = const.available_languages[self._language]
            if self._use_purnimanta_system is None:
                tm,td = drik.tamil_solar_month_and_date(date_in, place)
                spl_month_text = utils.MONTH_LIST[tm]+' '+str(td)
                _samvatsara = drik.samvatsara(date_in, place, zodiac=0)
                year_str = utils.YEAR_LIST[_samvatsara]
            else:
                maasam_no,td,_lunar_year,adhik_maasa,nija_maasa = drik.lunar_month_date(jd,place,
                                                        use_purnimanta_system=self._use_purnimanta_system)
                adhik_maasa_str = ''; 
                if adhik_maasa:
                    adhik_maasa_str = self.res['adhika_maasa_str']
                """ Check if current month is Nija Maasa """
                nija_month_str = ''
                if nija_maasa:
                    nija_month_str = self.res['nija_month_str']
                spl_month_text = utils.MONTH_LIST[maasam_no-1]+' '+ adhik_maasa_str+nija_month_str+' '+str(td)
                year_str = utils.YEAR_LIST[_lunar_year]
            _panchanga_dict = {'top_left': (kp_icon,_tithi), 'middle_left':(_tithi_icon,str(td)),
                               'middle_right':('',str(d)), 'bottom_left': _nak,
                               'top_right': (_sunrise_icon,_srise), 'bottom_right':(_sunset_icon,_sset)}
            header_text = year_str+' '+str(y)+' '+ utils.MONTH_LIST_EN[m-1]+' '+str(d)+' '+utils.DAYS_LIST[drik.vaara(jd)]+' '+\
                          spl_month_text+' '+ utils.PAKSHA_LIST[_paksha]+' ' + \
                          utils.TITHI_LIST[_tit-1]
            return _panchanga_dict, header_text
    def _update_resources(self):
        msgs = self.res
        self._dob_label.setText(msgs['date_of_birth_str'])
        self._dob_label.setToolTip(msgs['dob_tooltip_str'])
        self._place_label.setText(msgs['place_str'])
        self._place_label.setToolTip(msgs['place_tooltip_str'])
        self._lat_label.setText(msgs['latitude_str'])
        self._lat_label.setToolTip(msgs['latitude_tooltip_str'])
        self._long_label.setText(msgs['longitude_str'])
        self._long_label.setToolTip(msgs['longitude_tooltip_str'])
        self._tz_label.setText(msgs['timezone_offset_str'])
        self._tz_label.setToolTip(msgs['timezone_tooltip_str'])
        self.compute_btn.setText(msgs['calendar_str'])
        _calendar_list = [self.res[s]+' '+self.res['calendar_str'] for s in ['solar_str','amantha_str','purnimantha_str']]
        _cal_index = self._calendar_combo.currentIndex()
        self._calendar_combo.clear()
        self._calendar_combo.addItems(_calendar_list)
        self._calendar_combo.setCurrentIndex(_cal_index)
    def computeCalendar(self):
        try:
            self._update_resources()
            date_str = self.date_text.text()
            place_name = self._place_text.text()
            latitude = float(self._lat_text.text())
            longitude = float(self._long_text.text())
            timezone = float(self._tz_text.text())
            self.start_place = drik.Place(place_name, latitude, longitude, timezone)
            year, month, day = utils.get_year_month_day_from_date_format(date_str)#map(int,date_str.split(","))#
            selected_date = drik.Date(year,month,day)
            _jd = utils.julian_day_number((year, month, 1), (10, 0, 0))
            sunrise_hours = drik.sunrise(_jd,self.start_place)[0]
            _jd = utils.julian_day_number((year, month, 1), (sunrise_hours, 0, 0))
            first_day = drik.Date(year, month, 1)
            previous_month_end = utils.previous_panchanga_day(first_day, minus_days=1)
            if month == 12:
                last_day = 31
                next_month_start = drik.Date(year+1,1,1)
            else:
                last_day = utils.next_panchanga_day(drik.Date(year,(month+1)%13,1), -1)
                next_month_start = utils.next_panchanga_day(last_day, add_days=1)
                last_day = last_day.day
            _jd -= 1; current_date = previous_month_end
            start_day = drik.vaara(_jd)
            reached_end_of_month = False
            [self.cells[row][col].setVisible(False) for col in range(7) for row in range(7)]
            for row in range(7):
                for col in range(7):
                    cell = self.cells[row][col]
                    cell.clear()
                    if reached_end_of_month:
                        break
                    if row * 7 + col >= start_day:
                        _year,_month,_day,_ = utils.jd_to_gregorian(_jd)
                        sunrise_hours = drik.sunrise(_jd,self.start_place)[0]
                        _jd = utils.julian_day_number((_year, _month, _day), (sunrise_hours, 0, 0))
                        self.jd[row][col]=_jd; self.row_max = row
                        cell.setVisible(True)
                        panchanga_dict,_ = self._get_days_panchanga_info(row,col)
                        if panchanga_dict is not None: cell.set_texts(panchanga_dict)
                        _cell_style = "border: "+str(_cell_border_line_thickness)+"px solid "+_cell_border_line_color+"; "
                        if current_date == selected_date:
                            _cell_style += f"background-color: {input_day_color}"
                            self.selected_cell = (row+1,col)
                        elif current_date == previous_month_end:
                            _cell_style += f"background-color: {previous_month_color}"
                            self.previous_month_cell = (row,col)
                        elif current_date == next_month_start:
                            _cell_style += f"background-color: {next_month_color}"
                            self.next_month_cell = (row,col)
                        else:
                            _cell_style += f"background-color: {default_color}"
                        cell.setStyleSheet(_cell_style)
                            
                        reached_end_of_month = (current_date == next_month_start)
                        current_date = utils.next_panchanga_day(current_date, add_days=1)
                        _jd += 1
            if self.selected_cell is not None:
                self.cell_clicked(self.selected_cell[0], self.selected_cell[1])
        except Exception as e:
            print(f"VedicCalendar:computeCalendar: An error occurred: {e}")

    def cell_clicked(self,row,col):
        try:
            self.selected_cell = (row-1,col)
            jd = self.jd[row-1][col]; place = self.start_place
            self._reshade_cells()
            sep_str = '\n'
            info_list = self._fill_information_label1(jd,place).split(sep_str)
            _,header_text = self._get_days_panchanga_info(row-1,col)
            #print(jd,utils.jd_to_gregorian(jd),header_text)
            self.header_label.setText('<b><span style="color:'+_HEADER_LABEL_COLOR+';">'+str(header_text)+'</span></b>')
            for c,day in enumerate(utils.DAYS_SHORT_NAMES):
                _cell_style = "border: "+str(_cell_border_line_thickness)+"px solid "+_cell_border_line_color+";"
                self.day_labels[c].setStyleSheet(_cell_style)
                self.day_labels[c].setText('<b><span style="color:'+_HEADER_COLOR+';">'+str(day)+'</span></b>')
            font = QFont(); font.setPointSize(_info_label1_font_size); self._info_label1.setFont(font)
            self._info_label1.setText(sep_str.join(info_list[:]))
            y,m,d,_ = utils.jd_to_gregorian(self.jd[row-1][col])
            self.date_text.setText(str(y)+','+str(m)+','+str(d))
            if self.selected_cell == self.previous_month_cell or self.selected_cell==self.next_month_cell:
                self.computeCalendar()
        except Exception as e:
            tb = sys.exc_info()[2]
            print(f"VedicCalendar:cell_clicked: An error occurred: {e}",'line number',tb.tb_lineno)
    def _fill_information_label1(self,jd,place,show_more_link=True):
        try:
            info_str = ''; format_str = _KEY_VALUE_FORMAT_
            from jhora.ui import panchangam
            panchangam._SHOW_SPECIAL_TITHIS = False
            info_str = PanchangaInfoDialog._fill_information_label1(self,show_more_link=False, jd=jd, place=place,
                                                                    ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE)
            if show_more_link:
                info_str += format_str.format('<a href="show_more">Show more</a>','')
                try:
                    self._info_label1.linkActivated.disconnect()
                except TypeError:
                    pass
                self._info_label1.linkActivated.connect(lambda link: self._on_show_more_link_clicked(link, jd, place))
            return info_str
        except Exception as e:
            tb = sys.exc_info()[2]
            print(f"An error occurred: {e}",'line number',tb.tb_lineno)
if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        lang = 'Tamil'
        #start_date = (-3101,1,22); start_place = drik.Place('Ujjain,India',23.18,75.77,5.5)
        start_date = None; start_place = None
        ex = VedicCalendar(start_date=start_date,place=start_place,language=lang,use_purnimanta_system=None)
        ex.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"An error occurred: {e}")
