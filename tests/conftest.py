import os
import sys
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QCoreApplication

@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance for tests."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    # Enable high DPI attributes before QApplication is created
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication.instance() or QApplication(sys.argv)
    yield app
    # Teardown - quit application to release resources
    app.quit()
