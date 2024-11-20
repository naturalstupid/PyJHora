from PyQt6.QtWidgets import QMenu, QDialog, QVBoxLayout, QLabel, QPushButton, QWidget, QApplication
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._menu_dict = {
            "Option 1": [],
            "XXX": [],  # Assuming you have other options here
            "Option 2": []
        }
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

    def showContextMenu(self, pos):
        menu = QMenu(self)
        self.build_menu(menu, self._menu_dict)
        menu.exec(self.mapToGlobal(pos))

    def build_menu(self, menu, data):
        print('build menu')
        for key, value in data.items():
            print(key,value)
            if isinstance(value, dict):
                submenu = QMenu(key, self)
                self.build_menu(submenu, value)
                menu.addMenu(submenu)
            else:
                action = QAction(key, self)
                action.setData(value)
                action.triggered.connect(lambda checked, k=key: self.set_menu_data(k))
                menu.addAction(action)

    def set_menu_data(self, key):
        print('key',key)
        if key == "XXX":
            data = self.show_prasna_dialog()
            if len(data) > 0:
                action = self.sender()
                action.setData(data)
        else:
            action = self.sender()
            alt_data = action.data()
            alt_data_2d = [] # Replace this with your actual conversion method
            self.setData(data=self.data, arudha_lagna_data=alt_data_2d,
                         chart_title=self._chart_title, chart_title_font_size=self._chart_title_font_size)
            self.update()

    def show_prasna_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Dialog for XXX")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("This is a custom dialog for XXX"))

        button = QPushButton("OK")
        button.clicked.connect(dialog.accept)
        layout.addWidget(button)

        dialog.setLayout(layout)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return ["dummy_data"]  # Replace with actual data gathered from the dialog
        return []

    def setData(self, data, arudha_lagna_data, chart_title, chart_title_font_size):
        # Implement your setData method here
        pass

    def update(self):
        # Implement your update method here
        pass

if __name__ == "__main__":
    import sys
    def except_hook(cls, exception, traceback):
        print('exception called')
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())
