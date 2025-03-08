from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QRadioButton, QPushButton, QComboBox
from jhora import utils
class OptionDialog(QDialog):
    """
        General Options Dialog
    """
    def __init__(self, title='', option_label='', options_list=None, multi_selection=None, default_options=None,
                 options_orientation=0):
        super().__init__()
        self.res = utils.resource_strings
        self._title = 'Options' if title.strip() == '' else title
        self._option_label = self.res['select_one_of_options_from_str'] if option_label.strip() == '' else option_label
        self._options_list = options_list if options_list is not None else []
        self._multi_selection = multi_selection
        self._default_options = default_options if default_options is not None else [0]
        self._options_orientation = options_orientation
        self.create_ui()

    def create_ui(self):
        v_layout = QVBoxLayout()
        _label = QLabel(self._option_label)
        v_layout.addWidget(_label)
        
        self._options = []
        
        if len(self._options_list) == 0: 
            return
        
        if self._multi_selection is None:
            if isinstance(self._options_list[0], list):
                if self._options_orientation == 1:  # Vertical
                    for sublist in self._options_list:
                        combobox = QComboBox()
                        combobox.addItems(sublist)
                        self._options.append(combobox)
                        v_layout.addWidget(combobox)
                else:  # Horizontal
                    h_layout = QHBoxLayout()
                    for sublist in self._options_list:
                        combobox = QComboBox()
                        combobox.addItems(sublist)
                        self._options.append(combobox)
                        h_layout.addWidget(combobox)
                    v_layout.addLayout(h_layout)
            else:
                combobox = QComboBox()
                combobox.addItems(self._options_list)
                self._options.append(combobox)
                v_layout.addWidget(combobox)
        elif self._multi_selection:
            for mc in range(len(self._options_list)):
                _caption = self._options_list[mc]
                self._options.append(QCheckBox(_caption))
                if mc in self._default_options: 
                    self._options[mc].setChecked(True)
                v_layout.addWidget(self._options[mc])
        else:
            for mc in range(len(self._options_list)):
                _caption = self._options_list[mc]
                print(mc,_caption,self._default_options)
                self._options.append(QRadioButton(_caption))
                if mc in [self._default_options]:
                    self._options[mc].setChecked(True)
                v_layout.addWidget(self._options[mc])
        
        h_layout = QHBoxLayout()
        self._accept_button = QPushButton(self.res['accept_str'])
        self._accept_button.clicked.connect(self._accept_button_clicked)
        h_layout.addWidget(self._accept_button)
        self._cancel_button = QPushButton(self.res['cancel_str'])
        self._cancel_button.clicked.connect(self._cancel_button_clicked)
        h_layout.addWidget(self._cancel_button)
        v_layout.addLayout(h_layout)
        self.setLayout(v_layout)
        self.setWindowTitle(self._title)
    
    def _accept_button_clicked(self):
        self._accept_clicked = True
        if self._multi_selection is None:
            self._option_string = [cb.currentText() for cb in self._options]
            self._option_index = [cb.currentIndex() + 1 for cb in self._options]
        elif self._multi_selection:
            self._option_string = []
            self._option_index = []
            for mc, rb in enumerate(self._options):
                if rb.isChecked():
                    self._option_string.append(rb.text())
                    self._option_index.append(mc + 1)
        else:
            for mc, rb in enumerate(self._options):
                if rb.isChecked():
                    self._option_string = rb.text()
                    self._option_index = mc + 1
        print(self._option_index, self._option_string)
        self.accept()

    def _cancel_button_clicked(self):
        self._accept_clicked = False
        self._option_string = [] if self._multi_selection is not None else ''
        self._option_index = [] if self._multi_selection is not None else ''
        self.reject()
    
    def closeEvent(self, *args, **kwargs):
        self._option_string = ''
        QApplication.restoreOverrideCursor()
        return QDialog.closeEvent(self, *args, **kwargs)
if __name__ == "__main__":
    import sys
    utils.set_language('ta')
    def except_hook(cls, exception, traceback):
        print('exception called')
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    App = QApplication(sys.argv)
    _title_list = ['solar','amantha','purnimantha']
    _title = '/'.join([utils.resource_strings[ol+'_str'] for ol in _title_list])+' '+utils.resource_strings['month_str']
    option_list = [[utils.resource_strings[ol+'_str']+' '+utils.resource_strings['month_str'] for ol in _title_list],
                   [utils.resource_strings[ol+'_str'] for ol in ['previous','next']]
                  ]
    lm_dlg = OptionDialog(title='Title',options_list=option_list,multi_selection=None,default_options=1)
    lm_dlg.show()
    sys.exit(App.exec())
