"""PySide6 based user interface for AstroCal.

This module defines a simple Qt6 application using PySide6.
It demonstrates how to build scalable layouts with support
for high-DPI displays and a dark theme. Backend calculation
logic should be imported from other modules in the package.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


def init_high_dpi() -> None:
    """Enable Qt high DPI attributes for 4K monitor support."""
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


class MainWindow(QMainWindow):
    """Main application window with tabbed interface."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("AstroCal - PySide6")
        # Default window size, still resizable
        self.resize(1200, 800)

        # Apply global dark theme stylesheet and font size
        self.setStyleSheet(
            """
            QWidget { background-color: #121212; color: #dddddd; font-size: 16px; }
            QTabWidget::pane { border: 1px solid #444444; }
            QTabBar::tab { background: #333333; padding: 8px; }
            QTabBar::tab:selected { background: #555555; }
            """
        )


        self._init_ui()

    def _init_ui(self) -> None:
        """Builds the tabbed user interface."""
        tabs = QTabWidget()
        tabs.addTab(self._create_chart_tab(), "Chart Data")
        tabs.addTab(self._create_bhava_tab(), "Bhava")
        tabs.addTab(self._create_pakshi_tab(), "Panchapakshi")
        tabs.addTab(self._create_calendar_tab(), "Calendar")
        self.setCentralWidget(tabs)

    def _create_chart_tab(self) -> QWidget:
        """First tab displaying placeholder chart data."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        placeholder = QLabel("Chart Data Appears Here")
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)

        example = QTextEdit()
        example.setPlainText("Example chart data...\n")
        layout.addWidget(example)
        return tab

    def _create_bhava_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Bhava details will appear here"))
        return tab

    def _create_pakshi_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Panchapakshi information goes here"))
        return tab

    def _create_calendar_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Calendar view will be placed here"))
        return tab


def main(argv: list[str] | None = None) -> int:
    """Entry point for the PySide6 application."""
    init_high_dpi()
    app = QApplication(argv or sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
