from pyside_app.main import MainWindow
from PySide6.QtWidgets import QTabWidget


def test_mainwindow_tabs(qapp):
    window = MainWindow()
    central = window.centralWidget()
    assert isinstance(central, QTabWidget)
    assert central.count() == 4
    titles = [central.tabText(i) for i in range(central.count())]
    assert titles == ["Chart Data", "Bhava", "Panchapakshi", "Calendar"]
