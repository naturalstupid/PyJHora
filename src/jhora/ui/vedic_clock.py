import sys, os
import math
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy, QHBoxLayout
from PyQt6.QtCore import QTimer, QDateTime, Qt, QTimeZone, QPoint
from PyQt6.QtGui import QFont, QFontMetrics, QPainter, QPen, QPixmap, QPainterPath, QBrush, QColor
from jhora.panchanga import drik
from jhora import utils, const

# Define constants for various parameters of Analog Clock
_CLOCK_SIZE = 500
_CENTER_X = 250
_CENTER_Y = 250
_DAY_COLOR = QColor(255, 255, 224, 127)
_NIGHT_COLOR = QColor(211, 211, 211, 127)
_DAY_NIGHT_ANGLE_OFFSET = 80
_OUTER_CIRCLE_RADIUS = 180
_CAPTION_RADIUS_INCREMENT = 15
_CAPTION_ANGLE_SHIFT = 15 # degrees
_CAPTION_COLOR = Qt.GlobalColor.darkBlue
_OUTER_LABEL_STEP = 5
_OUTER_LABEL_COLOR = Qt.GlobalColor.darkMagenta
_OUTER_TICK_STEP = 1
_INNER_CIRCLE_RADIUS = 100
_INNER_LABEL_STEP = 5
_INNER_LABEL_COLOR = Qt.GlobalColor.darkGreen
_INNER_TICK_STEP = 1
_TICK_MARK_LENGTH = 10
_LABEL_TICK_MARK_LENGTH = 20
_LABEL_OFFSET = 20
_LABEL_AT_ZERO_DEGREES = 30 # Value of Label at Zero degrees
_SUNRISE_LABEL_DEGREES = 180 # Degree of the 0 label
_HAND_PEN_WIDTH = 3
_GHATI_HAND_LENGTH = 150
_GHATI_HAND_COLOR = Qt.GlobalColor.red
_PHALA_HAND_LENGTH = 170
_PHALA_HAND_COLOR = Qt.GlobalColor.blue
_VIGHATI_HAND_LENGTH = 80
_VIGHATI_HAND_COLOR = Qt.GlobalColor.green
_TIMER_FREQUENCY = 400  # = one second
_ANGLE_FACTOR = 6  # (360/60)
_IMAGE_ICON = os.path.abspath(const._IMAGES_PATH) + const._sep + "lord_ganesha1.jpg"
_SUNRISE_ICON = os.path.abspath(const._IMAGES_PATH) + const._sep + "sunrise.png"
_SUNSET_ICON = os.path.abspath(const._IMAGES_PATH) + const._sep + "sunset.png"
_ICON_SIZE = 64
_DAYNIGHT_STR_COLOR = Qt.GlobalColor.darkGreen
_day_night_radius_factor = 0.7

class VedicAnalogClock(QWidget):
    """
        force_equal_day_night_ghati = True will force equal 30 ghatis for day and night.
        This feature is for experimental purpose. 
        Some panchang websites like drikpanchang may force 30 ghatis for both day and night
        so that sunset is always equals to 30 ghati. 
        But traditionally vedic praharas are unequal when day/nights are unequal
        So use this function with caution. 
        Also enabling this feature in vedic clock will show unqual hand movements
    """

    def __init__(self, jd=None, place=None,language='ta',force_equal_day_night_ghati=False):
        super().__init__()
        utils.set_language(language)
        self.res = utils.resource_strings
        self.jd = jd; self.place = place
        self.force_equal_day_night_ghati = force_equal_day_night_ghati
        self.captions = [self.res[cap+'_str'] for cap in const.periods_of_the_day]
        self._day_night_str = [self.res['daytime_str'],self.res['nighttime_str']]
        self._get_drik_info()
        self.setWindowTitle(self.res['vedic_clock_str'])
        self.setFixedSize(_CLOCK_SIZE, _CLOCK_SIZE)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(_TIMER_FREQUENCY)  # Update every second
        # Load the icon
        self.icon = QPixmap(_IMAGE_ICON).scaled(_ICON_SIZE, _ICON_SIZE, Qt.AspectRatioMode.KeepAspectRatio)
        self.painter = QPainter(self)
        self.show()
        self.repaint()
    def closeEvent(self, *args, **kwargs):
        self.timer.stop()
        return QWidget.closeEvent(self, *args, **kwargs)
    def _get_current_date_time(self):
        current_datetime = QDateTime.currentDateTime()
        local_time_zone_hours = self.place.timezone
        time_zone = QTimeZone(int(local_time_zone_hours * 3600))
        return current_datetime.toTimeZone(time_zone)
    def _get_drik_info(self):
        if self.place is None:
            loc = utils.get_place_from_user_ip_address()
            self.place = drik.Place(loc[0], loc[1], loc[2], loc[3])
        current_datetime = self._get_current_date_time()
        if self.jd is None:
            self.jd = utils.julian_day_number(drik.Date(current_datetime.date().year(),
                                                        current_datetime.date().month(),
                                                        current_datetime.date().day()),
                                              (current_datetime.time().hour(),
                                               current_datetime.time().minute(),
                                               current_datetime.time().second()))
        self._day_length = drik.day_length(self.jd, self.place); self._night_length = drik.night_length(self.jd, self.place)
        _day_duration = self._day_length + self._night_length
        self._ghati_per_hour = 60 / _day_duration
        self._today_sunrise = drik.sunrise(self.jd, self.place)[0]; self._today_sunset = drik.sunset(self.jd,self.place)[0]
        self._day_ghati_per_hour = 30 / self._day_length; self._night_ghati_per_hour = 30 / self._night_length
        ssvt = self.get_vedic_time_equal_day_night_ghati(self._today_sunset) if self.force_equal_day_night_ghati \
                                            else self.get_vedic_time(self._today_sunset)
        ssgt = ssvt[0]+ssvt[1]/60+ssvt[2]/3600; ssdeg = ssgt*_ANGLE_FACTOR
        self._sunset_degrees = math.ceil(ssdeg)
    def get_vedic_time_equal_day_night_ghati(self,float_hours=None):
        if float_hours is None: 
            current_datetime = self._get_current_date_time()
            float_hours = current_datetime.time().hour() + current_datetime.time().minute() / 60 + \
                      current_datetime.time().second() / 3600 +current_datetime.time().msec() / 3600000
        if float_hours <= self._today_sunset and float_hours >= self._today_sunrise:
            ghati_hours = float_hours - self._today_sunrise
            if ghati_hours < 0:
                ghati_hours += 24
            total_ghati = ghati_hours * self._day_ghati_per_hour
        else:
            total_ghati = 30 + (float_hours-self._today_sunset)*self._night_ghati_per_hour if float_hours>=self._today_sunset \
                            else 60 - (self._today_sunrise-float_hours)*self._night_ghati_per_hour
        total_ghati = total_ghati % 60  # Reset to 0 after 60 ghatis
        ghati = int(total_ghati)
        phala = int((total_ghati - ghati) * 60)
        vighati = int(((total_ghati - ghati) * 60 - phala) * 60)
    
        return int(ghati), int(phala), int(vighati)
    def get_vedic_time(self,float_hours=None):
        if float_hours is None: 
            current_datetime = self._get_current_date_time()
            float_hours = current_datetime.time().hour() + current_datetime.time().minute() / 60 + \
                      current_datetime.time().second() / 3600 +current_datetime.time().msec() / 3600000
        local_hours_since_sunrise = float_hours - self._today_sunrise
        if local_hours_since_sunrise < 0:
            local_hours_since_sunrise += 24
        
        total_ghati = local_hours_since_sunrise * self._ghati_per_hour
        total_ghati = total_ghati % 60  # Reset to 0 after 60 ghatis
    
        ghati = int(total_ghati)
        phala = int((total_ghati - ghati) * 60)
        vighati = int(((total_ghati - ghati) * 60 - phala) * 60)
        return ghati,phala,vighati
    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            # Draw the background semicircles
            self.drawCircles(painter)
            # Draw fixed captions
            self.drawFixedCaptions(painter)
    
            # Paint the big circle for ghati and phala
            self.drawLabels(painter, _CENTER_X, _CENTER_Y, _OUTER_CIRCLE_RADIUS, _OUTER_LABEL_STEP,_OUTER_LABEL_COLOR)  # Outer labels
            self.drawTickMarks(painter, _CENTER_X, _CENTER_Y, _OUTER_CIRCLE_RADIUS, _OUTER_TICK_STEP)  # Outer tick marks
    
            # Draw the tick marks
            self.drawTickMarks(painter, _CENTER_X, _CENTER_Y, _OUTER_CIRCLE_RADIUS, _OUTER_TICK_STEP)
    
            # Calculate angles for clock hands
            ghati, phala, vighati = self.get_vedic_time_equal_day_night_ghati() if self.force_equal_day_night_ghati \
                                            else self.get_vedic_time()
    
            # Draw ghati hand (small) - Red
            ghati_angle = _ANGLE_FACTOR * ghati
            self.drawHand(painter, _CENTER_X, _CENTER_Y, _GHATI_HAND_LENGTH, ghati_angle, _GHATI_HAND_COLOR)
    
            # Draw phala hand (big) - Blue
            phala_angle = _ANGLE_FACTOR * phala
            self.drawHand(painter, _CENTER_X, _CENTER_Y, _PHALA_HAND_LENGTH, phala_angle, _PHALA_HAND_COLOR)
    
            self.drawLabels(painter, _CENTER_X, _CENTER_Y, _INNER_CIRCLE_RADIUS, _INNER_LABEL_STEP, _INNER_LABEL_COLOR)  # Inner labels
            self.drawTickMarks(painter, _CENTER_X, _CENTER_Y, _INNER_CIRCLE_RADIUS, _INNER_TICK_STEP)  # Inner tick marks
    
            # Draw vighati hand
            vighati_angle = _ANGLE_FACTOR * vighati
            self.drawHand(painter, _CENTER_X, _CENTER_Y, _VIGHATI_HAND_LENGTH, vighati_angle, _VIGHATI_HAND_COLOR)
            # Draw the icon at the center
            icon_size = self.icon.size()
            icon_x = _CENTER_X - icon_size.width() // 2
            icon_y = _CENTER_Y - icon_size.height() // 2
            # Create a circular mask
            mask = QPainterPath()
            mask.addEllipse(icon_x, icon_y, icon_size.width(), icon_size.height())
            painter.setClipPath(mask)
            
            # Draw the masked icon
            painter.drawPixmap(icon_x, icon_y, self.icon.scaled(_ICON_SIZE, _ICON_SIZE, Qt.AspectRatioMode.KeepAspectRatioByExpanding))
        except Exception as e:
            print(f"Error during paint event: {e}")
    def drawCircles(self,painter):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw the outer circle
        painter.setBrush(_NIGHT_COLOR)  # very light grey
        painter.drawEllipse(_CENTER_X - _OUTER_CIRCLE_RADIUS, _CENTER_Y - _OUTER_CIRCLE_RADIUS, 
                            2 * _OUTER_CIRCLE_RADIUS, 2 * _OUTER_CIRCLE_RADIUS)

        # Draw the annular region
        painter.setBrush(_DAY_COLOR)  # light yellow
        start_angle = _SUNRISE_LABEL_DEGREES * 16
        sweep_length = - self._sunset_degrees * 16
        painter.drawPie(_CENTER_X - _OUTER_CIRCLE_RADIUS, _CENTER_Y - _OUTER_CIRCLE_RADIUS,
                        2 * _OUTER_CIRCLE_RADIUS, 2 * _OUTER_CIRCLE_RADIUS, start_angle, sweep_length)

        # Draw the inner circle
        painter.setBrush(self.palette().window().color())  # fill with the widget's background color
        painter.drawEllipse(_CENTER_X - _INNER_CIRCLE_RADIUS, _CENTER_Y - _INNER_CIRCLE_RADIUS, 
                            2 * _INNER_CIRCLE_RADIUS, 2 * _INNER_CIRCLE_RADIUS)
        
        # Draw "Day" label
        day_angle = (_SUNRISE_LABEL_DEGREES+_DAY_NIGHT_ANGLE_OFFSET); day_angle_rad = day_angle * (math.pi / 180)
        day_x = int(_CENTER_X + (_INNER_CIRCLE_RADIUS + _day_night_radius_factor*(_OUTER_CIRCLE_RADIUS - _INNER_CIRCLE_RADIUS) / 2) * math.cos(day_angle_rad))
        day_y = int(_CENTER_Y + (_INNER_CIRCLE_RADIUS + _day_night_radius_factor*(_OUTER_CIRCLE_RADIUS - _INNER_CIRCLE_RADIUS) / 2) * math.sin(day_angle_rad))
        painter.setPen(QPen(_DAYNIGHT_STR_COLOR))
        painter.drawText(day_x, day_y, self._day_night_str[0])
        # Draw "Night" label
        night_angle_rad = (180 + day_angle+(90 -_DAY_NIGHT_ANGLE_OFFSET)) * (math.pi / 180)
        night_x = int(_CENTER_X + (_INNER_CIRCLE_RADIUS + _day_night_radius_factor*(_OUTER_CIRCLE_RADIUS - _INNER_CIRCLE_RADIUS) / 2) * math.cos(night_angle_rad))
        night_y = int(_CENTER_Y + (_INNER_CIRCLE_RADIUS + _day_night_radius_factor*(_OUTER_CIRCLE_RADIUS - _INNER_CIRCLE_RADIUS) / 2) * math.sin(night_angle_rad))
        painter.setPen(QPen(_DAYNIGHT_STR_COLOR))
        painter.drawText(night_x, night_y, self._day_night_str[1])

    # Draw _SUNRISE_ICON
        sunrise_icon = QPixmap(_SUNRISE_ICON)
        sunrise_x = int(_CENTER_X + (_OUTER_CIRCLE_RADIUS + 20) * math.cos(start_angle / 16 * math.pi / 180))
        sunrise_y = int(_CENTER_Y + (_OUTER_CIRCLE_RADIUS + 20) * math.sin(start_angle / 16 * math.pi / 180))
        painter.drawPixmap(QPoint(int(sunrise_x) - sunrise_icon.width() // 2, int(sunrise_y) - sunrise_icon.height() // 2), sunrise_icon)
    
        # Correct the calculation of the sunset angle
        sunset_angle = (_SUNRISE_LABEL_DEGREES + self._sunset_degrees) * 16
        sunset_icon = QPixmap(_SUNSET_ICON)
        sunset_x = int(_CENTER_X + (_OUTER_CIRCLE_RADIUS + 20) * math.cos(sunset_angle / 16 * math.pi / 180))
        sunset_y = int(_CENTER_Y + (_OUTER_CIRCLE_RADIUS + 20) * math.sin(sunset_angle / 16 * math.pi / 180))
        painter.drawPixmap(QPoint(int(sunset_x) - sunset_icon.width() // 2, int(sunset_y) - sunset_icon.height() // 2), sunset_icon)
    def drawTickMarks(self, painter, centerX, centerY, radius, step):
        for i in range(0, 60, step):
            angle = _ANGLE_FACTOR * i
            x1 = centerX + int(radius * math.cos(math.radians(angle)))
            y1 = centerY + int(radius * math.sin(math.radians(angle)))
            if i % 5 == 0:  # Label tick mark
                x2 = centerX + int((radius - _LABEL_TICK_MARK_LENGTH) * math.cos(math.radians(angle)))
                y2 = centerY + int((radius - _LABEL_TICK_MARK_LENGTH) * math.sin(math.radians(angle)))
            else:  # Regular tick mark
                x2 = centerX + int((radius - _TICK_MARK_LENGTH) * math.cos(math.radians(angle)))
                y2 = centerY + int((radius - _TICK_MARK_LENGTH) * math.sin(math.radians(angle)))
            painter.drawLine(x1, y1, x2, y2)

    def drawLabels(self, painter, centerX, centerY, radius, step,label_color):
        painter.setPen(QPen(label_color))
        font = QFont(); font.setBold(True); painter.setFont(font)
        for i in range(0, 61, step):
            angle = _ANGLE_FACTOR * i
            x = centerX + int((radius - _LABEL_OFFSET) * math.cos(math.radians(angle))) - 10
            y = centerY + int((radius - _LABEL_OFFSET) * math.sin(math.radians(angle))) + 10
            label = (i + _LABEL_AT_ZERO_DEGREES) % 60
            painter.drawText(x, y, f"{label}")
        
    def drawFixedCaptions(self, painter):
        num_captions = len(self.captions)
        angle_step = 360 / num_captions
        painter.setPen(QPen(_CAPTION_COLOR))
        for i in range(num_captions):
            angle = math.radians(_SUNRISE_LABEL_DEGREES + i * angle_step+_CAPTION_ANGLE_SHIFT)
            angle_degrees = i * angle_step

            # Calculate the position just outside the outer circle
            x = _CENTER_X + int((_OUTER_CIRCLE_RADIUS + _CAPTION_RADIUS_INCREMENT) * math.cos(angle))
            y = _CENTER_Y + int((_OUTER_CIRCLE_RADIUS + _CAPTION_RADIUS_INCREMENT) * math.sin(angle))

            # Save the painter state
            painter.save()

            # Translate and rotate the painter to align text with the circle's perimeter
            painter.translate(x, y)
            
            if angle_degrees <= 180:
                painter.rotate(angle_degrees - 90)
            else:
                painter.rotate(angle_degrees +  90)
            # Draw the text
            painter.drawText(-10, 0, self.captions[i])  # Adjust to center text

            # Restore the painter state
            painter.restore()
    def drawHand(self, painter, centerX, centerY, length, angle, color, arrowSize=10):
        pen = QPen(color, _HAND_PEN_WIDTH)
        painter.setPen(pen)
        
        # Calculate the end point of the arrow
        endX = centerX + int(length * math.cos(math.radians(angle + _SUNRISE_LABEL_DEGREES)))
        endY = centerY + int(length * math.sin(math.radians(angle + _SUNRISE_LABEL_DEGREES)))
    
        # Draw the shaft of the arrow
        painter.drawLine(centerX, centerY, endX, endY)
    
        # Calculate the two points for the arrowhead, making sure the tip points outward
        angleRad = math.radians(angle + _SUNRISE_LABEL_DEGREES)
        leftX = endX + int(arrowSize * math.cos(angleRad + math.pi - math.pi / 6))
        leftY = endY + int(arrowSize * math.sin(angleRad + math.pi - math.pi / 6))
        rightX = endX + int(arrowSize * math.cos(angleRad + math.pi + math.pi / 6))
        rightY = endY + int(arrowSize * math.sin(angleRad + math.pi + math.pi / 6))
    
        # Draw the arrowhead
        painter.drawLine(endX, endY, leftX, leftY)
        painter.drawLine(endX, endY, rightX, rightY)
        painter.drawLine(leftX, leftY, rightX, rightY)

################ Digital Clock ##############
_CLOCK_LABEL_WIDTH = 150
_CAPTION_FONT_SIZE = 12; _CLOCK_FONT_SIZE = 12
_LOCAL_CLOCK_COLOR = 'red'; _VEDIC_CLOCK_COLOR = 'green'

class VedicDigitalClock(QWidget):
    """
        force_equal_day_night_ghati = True will force equal 30 ghatis for day and night.
        This feature is for experimental purpose. 
        Some panchang websites like drikpanchang may force 30 ghatis for both day and night
        so that sunset is always equals to 30 ghati. 
        But traditionally vedic praharas are unequal when day/nights are unequal
        So use this function with caution. 
        Also enabling this feature in vedic clock will show unqual hand movements
    """
    def __init__(self, language='en', jd=None, place=None,adjust_label_widths=False,show_local_clock=False,
                 show_clock_caption=False,show_clock_label=True,horizontal_clocks=False,
                 force_equal_day_night_ghati=False):
        super().__init__()
        utils.set_language(language)
        self.res = utils.resource_strings
        self.force_equal_day_night_ghati = force_equal_day_night_ghati
        self.jd = jd; self.place = place
        self._get_drik_info()
        self.adjust_label_widths = adjust_label_widths
        self.show_local_clock = show_local_clock
        self.show_clock_caption = show_clock_caption; self.show_clock_label = show_clock_label
        self.horizontal_clocks = horizontal_clocks
        self.initUI()
    def initUI(self):
        layout = QHBoxLayout() if self.horizontal_clocks else QVBoxLayout()

        if self.show_clock_caption: 
            if self.show_local_clock:self.local_caption = QLabel(self.res['local_clock_str'], self)
            self.vedic_caption = QLabel(utils.resource_strings['vedic_clock_str'], self)
        if self.show_clock_label:
            if self.show_local_clock:self.local_format_label = QLabel(f"{self.res['hours_str']}:{self.res['minutes_str']}:{self.res['seconds_str']}", self)
            self.vedic_format_label = QLabel(f"{self.res['ghati_str']}:{self.res['pala_str']}:{self.res['vighati_str']}", self)
        if self.show_local_clock: self.local_time_label = QLabel(self)
        self.vedic_time_label = QLabel(self)
        if self.show_clock_caption and self.show_clock_label:
            for label in [self.local_caption, self.local_format_label, self.vedic_caption, self.vedic_format_label]:
                if label:
                    label.setFont(QFont("Arial", _CAPTION_FONT_SIZE, QFont.Weight.Bold))
                    label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vedic_time_label.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.vedic_time_label.setLineWidth(2)
        self.vedic_time_label.setFont(QFont("Arial", _CLOCK_FONT_SIZE, QFont.Weight.Bold))
        self.vedic_time_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.vedic_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vedic_time_label.setStyleSheet("color: "+_LOCAL_CLOCK_COLOR+"; min-width: 120px; max-width: 120px;")
        if self.show_local_clock:
            self.local_time_label.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
            self.local_time_label.setLineWidth(2)
            self.local_time_label.setFont(QFont("Arial", _CLOCK_FONT_SIZE, QFont.Weight.Bold))
            self.local_time_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.local_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.local_time_label.setStyleSheet("color: "+_LOCAL_CLOCK_COLOR+"; min-width: 120px; max-width: 120px;")
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            #separator.setFrameShadow(QFrame.Shadow.Sunken)
            #separator.sizePolicy().setHorizontalPolicy(QSizePolicy.Policy.Fixed)
        self.vedic_time_label.setStyleSheet("color: "+_VEDIC_CLOCK_COLOR+"; min-width: 120px; max-width: 120px;")
        if self.show_clock_caption: layout.addWidget(self.local_caption)
        if self.show_local_clock:
            if self.show_clock_label: layout.addWidget(self.local_format_label)
            layout.addWidget(self.local_time_label)
            layout.addWidget(separator)
        if self.show_clock_caption: layout.addWidget(self.vedic_caption)
        if self.show_clock_label: layout.addWidget(self.vedic_format_label)
        layout.addWidget(self.vedic_time_label)
        
        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.setWindowTitle(self.res['vedic_clock_str'])
        self.show()
    def closeEvent(self, *args, **kwargs):
        self.timer.stop()
        return QWidget.closeEvent(self, *args, **kwargs)
    def _get_current_date_time(self):
        current_datetime = QDateTime.currentDateTime()
        local_time_zone_hours = self.place.timezone
        time_zone = QTimeZone(int(local_time_zone_hours * 3600))
        return current_datetime.toTimeZone(time_zone)
    def _get_drik_info(self):
        if self.place is None:
            loc = utils.get_place_from_user_ip_address()
            self.place = drik.Place(loc[0], loc[1], loc[2], loc[3])
        current_datetime = self._get_current_date_time()
        if self.jd is None:
            self.jd = utils.julian_day_number(drik.Date(current_datetime.date().year(),
                                                        current_datetime.date().month(),
                                                        current_datetime.date().day()),
                                              (current_datetime.time().hour(),
                                               current_datetime.time().minute(),
                                               current_datetime.time().second()))
        self._day_length = drik.day_length(self.jd, self.place); self._night_length = drik.night_length(self.jd, self.place)
        _day_duration = self._day_length + self._night_length
        self._ghati_per_hour = 60 / _day_duration
        self._today_sunrise = drik.sunrise(self.jd, self.place)[0]; self._today_sunset = drik.sunset(self.jd,self.place)[0]
        self._day_ghati_per_hour = 30 / self._day_length; self._night_ghati_per_hour = 30 / self._night_length
        ssvt = self.get_vedic_time_equal_day_night_ghati(self._today_sunset) if self.force_equal_day_night_ghati \
                                        else self.get_vedic_time(self._today_sunset)
        ssgt = ssvt[0]+ssvt[1]/60+ssvt[2]/3600; ssdeg = ssgt*_ANGLE_FACTOR
        self._sunset_degrees = math.ceil(ssdeg)
    def get_vedic_time_equal_day_night_ghati(self,float_hours=None):
        if float_hours is None: 
            current_datetime = self._get_current_date_time()
            float_hours = current_datetime.time().hour() + current_datetime.time().minute() / 60 + \
                      current_datetime.time().second() / 3600 +current_datetime.time().msec() / 3600000
        if float_hours <= self._today_sunset and float_hours >= self._today_sunrise:
            ghati_hours = float_hours - self._today_sunrise
            if ghati_hours < 0:
                ghati_hours += 24
            total_ghati = ghati_hours * self._day_ghati_per_hour
        else:
            total_ghati = 30 + (float_hours-self._today_sunset)*self._night_ghati_per_hour if float_hours>=self._today_sunset \
                            else 60 - (self._today_sunrise-float_hours)*self._night_ghati_per_hour
        total_ghati = total_ghati % 60  # Reset to 0 after 60 ghatis
        ghati = int(total_ghati)
        phala = int((total_ghati - ghati) * 60)
        vighati = int(((total_ghati - ghati) * 60 - phala) * 60)
    
        return int(ghati), int(phala), int(vighati)
    def get_vedic_time(self,float_hours=None):
        if float_hours is None: 
            current_datetime = self._get_current_date_time()
            float_hours = current_datetime.time().hour() + current_datetime.time().minute() / 60 + \
                      current_datetime.time().second() / 3600 +current_datetime.time().msec() / 3600000
        local_hours_since_sunrise = float_hours - self._today_sunrise
        if local_hours_since_sunrise < 0:
            local_hours_since_sunrise += 24
        
        total_ghati = local_hours_since_sunrise * self._ghati_per_hour
        total_ghati = total_ghati % 60  # Reset to 0 after 60 ghatis
    
        ghati = int(total_ghati)
        phala = int((total_ghati - ghati) * 60)
        vighati = int(((total_ghati - ghati) * 60 - phala) * 60)
        return ghati,phala,vighati
    def update_time(self):
        current_datetime = self._get_current_date_time()
        # Calculate angles for clock hands
        vedic_time = self.get_vedic_time_equal_day_night_ghati() if self.force_equal_day_night_ghati \
                                        else self.get_vedic_time()
        self.vedic_time_label.setText(f'{vedic_time[0]:02}:{vedic_time[1]:02}:{vedic_time[2]:02}')
        if self.show_local_clock: self.local_time_label.setText(current_datetime.time().toString("HH:mm:ss"))
    def adjust_font_size_to_width(self, label):
        font = label.font()
        font_metrics = QFontMetrics(font)
        max_width = _CLOCK_LABEL_WIDTH  # Ensure the font fits within the clock's width
        while font_metrics.horizontalAdvance(label.text()) > max_width:
            font.setPointSize(font.pointSize() - 1)
            font_metrics = QFontMetrics(font)
        label.setFont(font)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dob = drik.Date(1996,12,7); tob = (10,34,0); place = drik.Place('Chennai,India',13.0878,80.2785,5.5)
    jd = utils.julian_day_number(dob,tob)
    jd = None; place = None
    #clock_widget = VedicDigitalClock(language='ta', jd=jd,place=place,show_local_clock=True)#,force_equal_day_night_ghati=True)
    clock_widget = VedicAnalogClock(language='ta', jd=jd,place=place)#,force_equal_day_night_ghati=True)
    sys.exit(app.exec())
