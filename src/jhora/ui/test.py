import sys
from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QMainWindow, QLabel, QWidget, \
                            QHBoxLayout, QProgressBar, QHeaderView, QStyledItemDelegate
from PyQt5.QtGui import QBrush, QColor, QIcon, QMovie
from PyQt5.QtCore import QTimer, QDateTime, Qt, QSize, QRect
from datetime import datetime, timedelta
from jhora import const

IMAGE_PATH = const._IMAGES_PATH + const._sep

class CustomDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        QStyledItemDelegate.paint(self, painter, option, index)

        if not index.parent().isValid():  # Only draw border for parent items
            parent_index = index
            parent_rect = option.widget.visualRect(parent_index)
            rect = parent_rect

            # Calculate the rectangle encompassing all children
            for i in range(option.widget.model().rowCount(parent_index)):
                child_index = option.widget.model().index(i, 0, parent_index)
                child_rect = option.widget.visualRect(child_index)
                rect = rect.united(child_rect)

            # Draw the border around the combined area of parent and children
            painter.save()
            painter.setPen(QColor(0, 0, 0))
            painter.drawRect(rect)
            painter.restore()

class CustomHeaderView(QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        painter.setPen(Qt.GlobalColor.black)
        text = self.model().headerData(logicalIndex, self.orientation(), Qt.ItemDataRole.DisplayRole)
        if text:
            text_rect = QRect(rect)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
        painter.restore()

class QCustomTreeWidget(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(0)
        self.current_highlighted_row = None
        self.current_parent_row = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_datetime)
        self.timer.start(1000)  # Check every second
        delegate = CustomDelegate()
        self.setItemDelegate(delegate)
        self.original_row_settings = {}

    def align_header_labels(self):
        header = self.header()
        for col in range(self.columnCount()):
            header_item = header.item(col)
            header_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    def populate_tree(self, headers, parent_level_list, parent_level_labels, child_level_list):
        try:
            # Set custom header view
            custom_header = CustomHeaderView(Qt.Orientation.Horizontal, self)
            self.setHeader(custom_header)
            headers = [self.format_cell_value(h, new_line="\n") for h in headers]
            self.setColumnCount(len(headers))
            self.setHeaderLabels(headers)

            for parent_data, labels_data, children_data in zip(parent_level_list, parent_level_labels, child_level_list):
                self.add_text_above_parent_row(labels_data)
                parent_item = QTreeWidgetItem(self)
                self.set_item_data(parent_item, parent_data)
                for child_data in children_data:
                    child_item = QTreeWidgetItem(parent_item)
                    self.set_item_data(child_item, child_data)
                    self.original_row_settings[id(child_item)] = child_data

            self.resize_all_columns()
            self.header().setStretchLastSection(False)
        except Exception as e:
            print(f"An error occurred during populate_tree: {e}")

    def format_cell_value(self, cell, new_line='<br>'):
        """Helper function to format cell values by handling new lines in strings and tuples."""
        if isinstance(cell, str):
            return cell.replace('\\n', new_line)
        elif isinstance(cell, tuple):
            return tuple(self.format_cell_value(item) for item in cell)
        else:
            return str(cell)

    def resize_all_columns(self):
        """Resize columns of the tree widget to fit contents."""
        try:
            for column in range(self.columnCount()):
                self.resizeColumnToContents(column)
        except Exception as e:
            print(f"An error occurred during resize_all_columns: {e}")

    def add_text_above_parent_row(self, labels):
        try:
            # Create an intermediate item to hold the combined text
            intermediate_item = QTreeWidgetItem()
            intermediate_item.setFlags(intermediate_item.flags() & ~Qt.ItemIsSelectable)

            # Create a single QLabel with the combined text
            label_text = ""
            for label_data in labels:
                if isinstance(label_data, str):
                    label_text += self.format_cell_value(label_data)
                elif isinstance(label_data, tuple):
                    text, icon_path = label_data[0], label_data[1] if len(label_data) > 1 else None
                    label_text += self.format_cell_value(text)
                    # Add icon if provided
                    if icon_path:
                        label_text += f'<img src="{IMAGE_PATH + icon_path}" width="16" height="16"> '

            label = QLabel(label_text)
            label.setTextFormat(Qt.RichText)  # Use rich text format for HTML handling
            label.setStyleSheet("border: 1px solid black; padding: 5px;")

            # Add the QLabel to the intermediate item
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.addWidget(label)
            layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
            container.setLayout(layout)

            self.addTopLevelItem(intermediate_item)
            self.setItemWidget(intermediate_item, 0, container)
            # Span the QLabel across all columns
            intermediate_item.setFirstColumnSpanned(True)
        except Exception as e:
            print(f"An error occurred during add_text_above_parent_row: {e}")

    def set_item_data(self, item, data):
        try:
            for column, value in enumerate(data):
                if isinstance(value, str):
                    item.setText(column, self.format_cell_value(value, new_line="\n"))
                    item.setForeground(column, QColor("black"))  # Text color
                elif isinstance(value, tuple):
                    if len(value) == 2:
                        icon_path, text = value
                        item.setText(column, self.format_cell_value(text, new_line="\n"))
                        item.setIcon(column, QIcon(IMAGE_PATH + icon_path))
                        item.setForeground(column, QColor("black"))  # Text color
                    elif len(value) == 3:
                        icon_path, text, background_color = value
                        item.setText(column, self.format_cell_value(text, new_line="\n"))
                        item.setIcon(column, QIcon(IMAGE_PATH + icon_path))
                        item.setBackground(column, QBrush(QColor(background_color)))
                        item.setForeground(column, QColor("black"))  # Text color
                elif isinstance(value, float):
                    progress = QProgressBar()
                    progress.setValue(int(value * 100 if column == 8 else value))
                    progress.setStyleSheet("QProgressBar { border: 1px solid black; } QProgressBar::chunk { background-color: lightgreen; }")
                    self.setItemWidget(item, column, progress)
        except Exception as e:
            print(f"An error occurred during set_item_data: {e}")

    def check_datetime(self):
        try:
            current_datetime = QDateTime.currentDateTime()
            self.expand_row_with_datetime(current_datetime)
        except Exception as e:
            print(f"An error occurred during check_datetime: {e}")

def expand_row_with_datetime(self, current_datetime):
    try:
        if self.current_highlighted_row:
            parent_item = self.current_highlighted_row.parent()
            parent_row_idx = self.indexOfTopLevelItem(parent_item)
            child_row_idx = parent_item.indexOfChild(self.current_highlighted_row)
            original_data = self.original_row_settings.get(id(self.current_highlighted_row), [])
            self.set_item_data(self.current_highlighted_row, original_data)
            # Remove sandclock icon from previous row
            self.setItemWidget(self.current_highlighted_row, 0, None)

        def is_matching_row(item):
            from_datetime = QDateTime.fromString(item.text(0), "yyyy-MM-dd HH:mm:ss")
            to_datetime = QDateTime.fromString(item.text(1), "yyyy-MM-dd HH:mm:ss")
            return from_datetime <= current_datetime <= to_datetime

        def highlight_row(item):
            for i in range(self.columnCount()):
                item.setBackground(i, QBrush(QColor("yellow")))
            # Create a new QLabel for the sandclock GIF
            label = QLabel()
            movie = QMovie(IMAGE_PATH + "sandclock.gif")
            movie.setScaledSize(QSize(32, 32))  # Set the size of the GIF
            label.setMovie(movie)
            movie.start()
            self.setItemWidget(item, 0, label)

            # Expand the parent of the matching row
            if item.parent():
                item.parent().setExpanded(True)

        def traverse_tree(item):
            if not item.childCount() and is_matching_row(item):  # Only consider child items
                return item
            for i in range(item.childCount()):
                matching_child = traverse_tree(item.child(i))
                if matching_child:
                    return matching_child
            return None

        root_item = self.invisibleRootItem()
        self.current_highlighted_row = None
        self.current_parent_row = None
        for i in range(root_item.childCount()):
            parent_item = root_item.child(i)
            matching_row = traverse_tree(parent_item)
            if matching_row:
                self.current_highlighted_row = matching_row
                highlight_row(matching_row)
                self.current_parent_row = parent_item
                break

        # Collapse all other parents
        for i in range(root_item.childCount()):
            parent_item = root_item.child(i)
            if parent_item != self.current_parent_row:
                parent_item.setExpanded(False)

        # Resize columns to fit contents
        self.resize_all_columns()

    except Exception as e:
        print(f"An error occurred during expand_row_with_datetime: {e}")
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1200, 800)  # Set initial size of the window

        self.tree_widget = QCustomTreeWidget()
        self.setCentralWidget(self.tree_widget)

headers =  ['முதல்', 'வரை', 'காலம்', 'முக்கிய\\nபறவை', 'முக்கிய\\nசெயல்பாடு', 'துணை\\nபறவை', 'துணை\\nசெயல்பாடு', 'உறவு', 'சக்தி', 'விளைவு', 'மதிப்பீடு']
parent_level_list =  [[('day_sun.png', '2024-12-28 07:25:13'), '2024-12-28 09:12:50', '1.79 மணிநேரம்', ('crow.png', 'காகம்'), ('dying.png', 'இறக்கிறது', 'red'), '', '', '', '', '', ''], [('day_sun.png', '2024-12-28 09:12:50'), '2024-12-28 11:00:26', '1.79 மணிநேரம்', ('crow.png', 'காகம்'), ('sleeping.png', 'தூங்குகிறது', 'orange'), '', '', '', '', '', ''], [('day_sun.png', '2024-12-28 11:00:26'), '2024-12-28 12:48:03', '1.79 மணிநேரம்', ('crow.png', 'காகம்'), ('ruling.png', 'ஆள்கிறது', 'dark green'), '', '', '', '', '', ''], [('day_sun.png', '2024-12-28 12:48:03'), '2024-12-28 14:35:40', '1.79 மணிநேரம்', ('crow.png', 'காகம்'), ('walking.png', 'நடக்கிறது', 'light green'), '', '', '', '', '', ''], [('day_sun.png', '2024-12-28 14:35:40'), '2024-12-28 16:23:16', '1.79 மணிநேரம்', ('crow.png', 'காகம்'), ('eating.png', 'உண்கிறது', 'yellow'), '', '', '', '', '', ''], [('moon_with_star.png', '2024-12-28 16:23:16'), '2024-12-28 19:23:42', '3.01 மணிநேரம்', ('crow.png', 'காகம்'), ('sleeping.png', 'தூங்குகிறது', 'orange'), '', '', '', '', '', ''], [('moon_with_star.png', '2024-12-28 19:23:42'), '2024-12-28 22:24:08', '3.01 மணிநேரம்', ('crow.png', 'காகம்'), ('walking.png', 'நடக்கிறது', 'light green'), '', '', '', '', '', ''], [('moon_with_star.png', '2024-12-28 22:24:08'), '2024-12-29 01:24:34', '3.01 மணிநேரம்', ('crow.png', 'காகம்'), ('dying.png', 'இறக்கிறது', 'red'), '', '', '', '', '', ''], [('moon_with_star.png', '2024-12-29 01:24:34'), '2024-12-29 04:25:00', '3.01 மணிநேரம்', ('crow.png', 'காகம்'), ('ruling.png', 'ஆள்கிறது', 'dark green'), '', '', '', '', '', ''], [('moon_with_star.png', '2024-12-29 04:25:00'), '2024-12-29 07:25:26', '3.01 மணிநேரம்', ('crow.png', 'காகம்'), ('eating.png', 'உண்கிறது', 'yellow'), '', '', '', '', '', '']]
child_level_list =  [[[('day_sun.png', '2024-12-28 07:25:13'), '2024-12-28 07:52:07', '27 நிமிடங்கள்', ('crow.png', 'காகம்'), ('dying.png', 'இறக்கிறது', 'red'), ('crow.png', 'காகம்'), ('dying.png', 'இறக்கிறது', 'red'), ('', 'சமம்', 'yellow'), 0.04, ('', 'மிகவும்\\nமோசமானது', 'red'), 1.0], [('day_sun.png', '2024-12-28 07:52:07'), '2024-12-28 08:10:03', '18 நிமிடங்கள்', ('crow.png', 'காகம்'), ('dying.png', 'இறக்கிறது', 'red'), ('vulture.png', 'கழுகு'), ('sleeping.png', 'தூங்குகிறது', 'orange'), ('', 'எதிரி', 'orange'), 0.08, ('', 'மிகவும்\\nமோசமானது', 'red'), 1.0], [('day_sun.png', '2024-12-28 08:10:03'), '2024-12-28 08:27:59', '18 நிமிடங்கள்', ('crow.png', 'காகம்'), ('dying.png', 'இறக்கிறது', 'red'), ('cock.png', 'சேவல்'), ('ruling.png', 'ஆள்கிறது', 'dark green'), ('', 'நண்பன்', 'light green'), 0.2, ('', 'சராசரி', 'yellow'), 3.0], [('day_sun.png', '2024-12-28 08:27:59'), '2024-12-28 08:50:25', '22 நிமிடங்கள்', ('crow.png', 'காகம்'), ('dying.png', 'இறக்கிறது', 'red'), ('owl.png', 'ஆந்தை'), ('walking.png', 'நடக்கிறது', 'light green'), ('', 'நண்பன்', 'light green'), 0.12, ('', 'மோசமானது', 'orange'), 2.0], [('day_sun.png', '2024-12-28 08:50:25'), '2024-12-28 09:12:50', '22 நிமிடங்கள்', ('crow.png', 'காகம்'), ('dying.png', 'இறக்கிறது', 'red'), ('peacock.png', 'மயில்'), ('eating.png', 'உண்கிறது', 'yellow'), ('', 'எதிரி', 'orange'), 0.16, ('', 'மிகவும்\\nமோசமானது', 'red'), 1.0]], [[('day_sun.png', '2024-12-28 09:12:50'), '2024-12-28 09:30:46', '18 நிமிடங்கள்', ('crow.png', 'காகம்'), ('sleeping.png', 'தூங்குகிறது', 'orange'), ('crow.png', 'காகம்'), ('sleeping.png', 'தூங்குகிறது', 'orange'), ('', 'சமம்', 'yellow'), 0.16, ('', 'மோசமானது', 'orange'), 2.0], [('day_sun.png', '2024-12-28 09:30:46'), '2024-12-28 09:48:42', '18 நிமிடங்கள்', ('crow.png', 'காகம்'), ('sleeping.png', 'தூங்குகிறது', 'orange'), ('vulture.png', 'கழுகு'), ('ruling.png', 'ஆள்கிறது', 'dark green'), ('', 'எதிரி', 'orange'), 0.4, ('', 'சராசரி', 'yellow'), 3.0], [('day_sun.png', '2024-12-28 09:48:42'), '2024-12-28 10:11:07', '22 நிமிடங்கள்', ('crow.png', 'காகம்'), ('sleeping.png', 'தூங்குகிறது', 'orange'), ('cock.png', 'சேவல்'), ('walking.png', 'நடக்கிறது', 'light green'), ('', 'நண்பன்', 'light green'), 0.24, ('', 'சராசரி', 'yellow'), 3.0], [('day_sun.png', '2024-12-28 10:11:07'), '2024-12-28 10:33:32', '22 நிமிடங்கள்', ('crow.png', 'காகம்'), ('sleeping.png', 'தூங்குகிறது', 'orange'), ('owl.png', 'ஆந்தை'), ('eating.png', 'உண்கிறது', 'yellow'), ('', 'நண்பன்', 'light green'), 0.32, ('', 'சராசரி', 'yellow'), 4.0], [('day_sun.png', '2024-12-28 10:33:32'), '2024-12-28 11:00:26', '27 நிமிடங்கள்', ('crow.png', 'காகம்'), ('sleeping.png', 'தூங்குகிறது', 'orange'), ('peacock.png', 'மயில்'), ('dying.png', 'இறக்கிறது', 'red'), ('', 'எதிரி', 'orange'), 0.08, ('', 'மிகவும்\\nமோசமானது', 'red'), 1.0]], [[('day_sun.png', '2024-12-28 11:00:26'), '2024-12-28 11:18:22', '18 நிமிடங்கள்', ('crow.png', 'காகம்'), ('ruling.png', 'ஆள்கிறது', 'dark green'), ('crow.png', 'காகம்'), ('ruling.png', 'ஆள்கிறது', 'dark green'), ('', 'சமம்', 'yellow'), 1.0, ('', 'மிகவும்\\nநல்லது', 'dark green'), 10.0], [('day_sun.png', '2024-12-28 11:18:22'), '2024-12-28 11:40:48', '22 நிமிடங்கள்', ('crow.png', 'காகம்'), ('ruling.png', 'ஆள்கிறது', 'dark green'), ('vulture.png', 'கழுகு'), ('walking.png', 'நடக்கிறது', 'light green'), ('', 'எதிரி', 'orange'), 0.6, ('', 'சராசரி', 'yellow'), 5.0], [('day_sun.png', '2024-12-28 11:40:48'), '2024-12-28 12:03:13', '22 நிமிடங்கள்', ('crow.png', 'காகம்'), ('ruling.png', 'ஆள்கிறது', 'dark green'), ('cock.png', 'சேவல்'), ('eating.png', 'உண்கிறது', 'yellow'), ('', 'நண்பன்', 'light green'), 0.8, ('', 'மிகவும்\\nநல்லது', 'dark green'), 9.0], [('day_sun.png', '2024-12-28 12:03:13'), '2024-12-28 12:30:07', '27 நிமிடங்கள்', ('crow.png', 'காகம்'), ('ruling.png', 'ஆள்கிறது', 'dark green'), ('owl.png', 'ஆந்தை'), ('dying.png', 'இறக்கிறது', 'red'), ('', 'நண்பன்', 'light green'), 0.2, ('', 'சராசரி', 'yellow'), 3.0], [('day_sun.png', '2024-12-28 12:30:07'), '2024-12-28 12:48:03', '18 நிமிடங்கள்', ('crow.png', 'காகம்'), ('ruling.png', 'ஆள்கிறது', 'dark green'), ('peacock.png', 'மயில்'), ('sleeping.png', 'தூங்குகிறது', 'orange'), ('', 'எதிரி', 'orange'), 0.4, ('', 'சராசரி', 'yellow'), 3.0]], [[('day_sun.png', '2024-12-28 12:48:03'), '2024-12-28 13:10:28', '22 நிமிடங்கள்', ('crow.png', 'காகம்'), ('walking.png', 'நடக்கிறது', 'light green'), ('crow.png', 'காகம்'), ('walking.png', 'நடக்கிறது', 'light green'), ('', 'சமம்', 'yellow'), 0.36, ('', 'சராசரி', 'yellow'), 4.0], [('day_sun.png', '2024-12-28 13:10:28'), '2024-12-28 13:32:53', '22 நிமிடங்கள்', ('crow.png', 'காகம்'), ('walking.png', 'நடக்கிறது', 'light green'), ('vulture.png', 'கழுகு'), ('eating.png', 'உண்கிறது', 'yellow'), ('', 'எதிரி', 'orange'), 0.48, ('', 'சராசரி', 'yellow'), 4.0], [('day_sun.png', '2024-12-28 13:32:53'), '2024-12-28 13:59:47', '27 நிமிடங்கள்', ('crow.png', 'காகம்'), ('walking.png', 'நடக்கிறது', 'light green'), ('cock.png', 'சேவல்'), ('dying.png', 'இறக்கிறது', 'red'), ('', 'நண்பன்', 'light green'), 0.12, ('', 'மோசமானது', 'orange'), 2.0], [('day_sun.png', '2024-12-28 13:59:47'), '2024-12-28 14:17:43', '18 நிமிடங்கள்', ('crow.png', 'காகம்'), ('walking.png', 'நடக்கிறது', 'light green'), ('owl.png', 'ஆந்தை'), ('sleeping.png', 'தூங்குகிறது', 'orange'), ('', 'நண்பன்', 'light green'), 0.24, ('', 'சராசரி', 'yellow'), 3.0], [('day_sun.png', '2024-12-28 14:17:43'), '2024-12-28 14:35:40', '18 நிமிடங்கள்', ('crow.png', 'காகம்'), ('walking.png', 'நடக்கிறது', 'light green'), ('peacock.png', 'மயில்'), ('ruling.png', 'ஆள்கிறது', 'dark green'), ('', 'எதிரி', 'orange'), 0.6, ('', 'சராசரி', 'yellow'), 5.0]], [[('day_sun.png', '2024-12-28 14:35:40'), '2024-12-28 14:58:05', '22 நிமிடங்கள்', ('crow.png', 'காகம்'), ('eating.png', 'உண்கிறது', 'yellow'), ('crow.png', 'காகம்'), ('eating.png', 'உண்கிறது', 'yellow'), ('', 'சமம்', 'yellow'), 0.64, ('', 'நல்லது', 'light green'), 6.0], [('day_sun.png', '2024-12-28 14:58:05'), '2024-12-28 15:24:59', '27 நிமிடங்கள்', ('crow.png', 'காகம்'), ('eating.png', 'உண்கிறது', 'yellow'), ('vulture.png', 'கழுகு'), ('dying.png', 'இறக்கிறது', 'red'), ('', 'எதிரி', 'orange'), 0.16, ('', 'மிகவும்\\nமோசமானது', 'red'), 1.0], [('day_sun.png', '2024-12-28 15:24:59'), '2024-12-28 15:42:55', '18 நிமிடங்கள்', ('crow.png', 'காகம்'), ('eating.png', 'உண்கிறது', 'yellow'), ('cock.png', 'சேவல்'), ('sleeping.png', 'தூங்குகிறது', 'orange'), ('', 'நண்பன்', 'light green'), 0.32, ('', 'சராசரி', 'yellow'), 4.0], [('day_sun.png', '2024-12-28 15:42:55'), '2024-12-28 16:00:51', '18 நிமிடங்கள்', ('crow.png', 'காகம்'), ('eating.png', 'உண்கிறது', 'yellow'), ('owl.png', 'ஆந்தை'), ('ruling.png', 'ஆள்கிறது', 'dark green'), ('', 'நண்பன்', 'light green'), 0.8, ('', 'மிகவும்\\nநல்லது', 'dark green'), 9.0], [('day_sun.png', '2024-12-28 16:00:51'), '2024-12-28 16:23:16', '22 நிமிடங்கள்', ('crow.png', 'காகம்'), ('eating.png', 'உண்கிறது', 'yellow'), ('peacock.png', 'மயில்'), ('walking.png', 'நடக்கிறது', 'light green'), ('', 'எதிரி', 'orange'), 0.48, ('', 'சராசரி', 'yellow'), 4.0]], [[('moon_with_star.png', '2024-12-28 16:23:16'), '2024-12-28 16:45:49', '23 நிமிடங்கள்', ('crow.png', 'காகம்'), ('sleeping.png', 'தூங்குகிறது', 'orange'), ('crow.png', 'காகம்'), ('sleeping.png', 'தூங்குகிறது', 'orange'), ('', 'சமம்', 'yellow'), 0.16, ('', 'மோசமானது', 'orange'), 2.0], [('moon_with_star.png', '2024-12-28 16:45:49'), '2024-12-28 17:30:56', '45 நிமிடங்கள்', ('crow.png', 'காகம்'), ('sleeping.png', 'தூங்குகிறது', 'orange'), ('owl.png', 'ஆந்தை'), ('walking.png', 'நடக்கிறது', 'light green'), ('', 'நண்பன்', 'light green'), 0.24, ('', 'சராசரி', 'yellow'), 3.0], [('moon_with_star.png', '2024-12-28 17:30:56'), '2024-12-28 17:45:58', '15 நிமிடங்கள்', ('crow.png', 'காகம்'), ('sleeping.png', 'தூங்குகிறது', 'orange'), ('vulture.png', 'கழுகு'), ('dying.png', 'இறக்கிறது', 'red'), ('', 'நண்பன்', 'light green'), 0.08, ('', 'மோசமானது', 'orange'), 2.0], [('moon_with_star.png', '2024-12-28 17:45:58'), '2024-12-28 18:46:07', '60 நிமிடங்கள்', ('crow.png', 'காகம்'), ('sleeping.png', 'தூங்குகிறது', 'orange'), ('peacock.png', 'மயில்'), ('ruling.png', 'ஆள்கிறது', 'dark green'), ('', 'எதிரி', 'orange'), 0.4, ('', 'சராசரி', 'yellow'), 3.0], [('moon_with_star.png', '2024-12-28 18:46:07'), '2024-12-28 19:23:42', '38 நிமிடங்கள்', ('crow.png', 'காகம்'), ('sleeping.png', 'தூங்குகிறது', 'orange'), ('cock.png', 'சேவல்'), ('eating.png', 'உண்கிறது', 'yellow'), ('', 'எதிரி', 'orange'), 0.32, ('', 'மோசமானது', 'orange'), 2.0]], [[('moon_with_star.png', '2024-12-28 19:23:42'), '2024-12-28 20:08:49', '45 நிமிடங்கள்', ('crow.png', 'காகம்'), ('walking.png', 'நடக்கிறது', 'light green'), ('crow.png', 'காகம்'), ('walking.png', 'நடக்கிறது', 'light green'), ('', 'சமம்', 'yellow'), 0.36, ('', 'சராசரி', 'yellow'), 4.0], [('moon_with_star.png', '2024-12-28 20:08:49'), '2024-12-28 20:23:51', '15 நிமிடங்கள்', ('crow.png', 'காகம்'), ('walking.png', 'நடக்கிறது', 'light green'), ('owl.png', 'ஆந்தை'), ('dying.png', 'இறக்கிறது', 'red'), ('', 'நண்பன்', 'light green'), 0.12, ('', 'மோசமானது', 'orange'), 2.0], [('moon_with_star.png', '2024-12-28 20:23:51'), '2024-12-28 21:23:59', '60 நிமிடங்கள்', ('crow.png', 'காகம்'), ('walking.png', 'நடக்கிறது', 'light green'), ('vulture.png', 'கழுகு'), ('ruling.png', 'ஆள்கிறது', 'dark green'), ('', 'நண்பன்', 'light green'), 0.6, ('', 'நல்லது', 'light green'), 7.0], [('moon_with_star.png', '2024-12-28 21:23:59'), '2024-12-28 22:01:35', '38 நிமிடங்கள்', ('crow.png', 'காகம்'), ('walking.png', 'நடக்கிறது', 'light green'), ('peacock.png', 'மயில்'), ('eating.png', 'உண்கிறது', 'yellow'), ('', 'எதிரி', 'orange'), 0.48, ('', 'சராசரி', 'yellow'), 4.0], [('moon_with_star.png', '2024-12-28 22:01:35'), '2024-12-28 22:24:08', '23 நிமிடங்கள்', ('crow.png', 'காகம்'), ('walking.png', 'நடக்கிறது', 'light green'), ('cock.png', 'சேவல்'), ('sleeping.png', 'தூங்குகிறது', 'orange'), ('', 'எதிரி', 'orange'), 0.24, ('', 'மிகவும்\\nமோசமானது', 'red'), 1.0]], [[('moon_with_star.png', '2024-12-28 22:24:08'), '2024-12-28 22:39:10', '15 நிமிடங்கள்', ('crow.png', 'காகம்'), ('dying.png', 'இறக்கிறது', 'red'), ('crow.png', 'காகம்'), ('dying.png', 'இறக்கிறது', 'red'), ('', 'சமம்', 'yellow'), 0.04, ('', 'மிகவும்\\nமோசமானது', 'red'), 1.0], [('moon_with_star.png', '2024-12-28 22:39:10'), '2024-12-28 23:39:19', '60 நிமிடங்கள்', ('crow.png', 'காகம்'), ('dying.png', 'இறக்கிறது', 'red'), ('owl.png', 'ஆந்தை'), ('ruling.png', 'ஆள்கிறது', 'dark green'), ('', 'நண்பன்', 'light green'), 0.2, ('', 'சராசரி', 'yellow'), 3.0], [('moon_with_star.png', '2024-12-28 23:39:19'), '2024-12-29 00:16:54', '38 நிமிடங்கள்', ('crow.png', 'காகம்'), ('dying.png', 'இறக்கிறது', 'red'), ('vulture.png', 'கழுகு'), ('eating.png', 'உண்கிறது', 'yellow'), ('', 'நண்பன்', 'light green'), 0.16, ('', 'சராசரி', 'yellow'), 3.0], [('moon_with_star.png', '2024-12-29 00:16:54'), '2024-12-29 00:39:28', '23 நிமிடங்கள்', ('crow.png', 'காகம்'), ('dying.png', 'இறக்கிறது', 'red'), ('peacock.png', 'மயில்'), ('sleeping.png', 'தூங்குகிறது', 'orange'), ('', 'எதிரி', 'orange'), 0.08, ('', 'மிகவும்\\nமோசமானது', 'red'), 1.0], [('moon_with_star.png', '2024-12-29 00:39:28'), '2024-12-29 01:24:34', '45 நிமிடங்கள்', ('crow.png', 'காகம்'), ('dying.png', 'இறக்கிறது', 'red'), ('cock.png', 'சேவல்'), ('walking.png', 'நடக்கிறது', 'light green'), ('', 'எதிரி', 'orange'), 0.12, ('', 'மிகவும்\\nமோசமானது', 'red'), 1.0]], [[('moon_with_star.png', '2024-12-29 01:24:34'), '2024-12-29 02:24:43', '60 நிமிடங்கள்', ('crow.png', 'காகம்'), ('ruling.png', 'ஆள்கிறது', 'dark green'), ('crow.png', 'காகம்'), ('ruling.png', 'ஆள்கிறது', 'dark green'), ('', 'சமம்', 'yellow'), 1.0, ('', 'மிகவும்\\nநல்லது', 'dark green'), 10.0], [('moon_with_star.png', '2024-12-29 02:24:43'), '2024-12-29 03:02:18', '38 நிமிடங்கள்', ('crow.png', 'காகம்'), ('ruling.png', 'ஆள்கிறது', 'dark green'), ('owl.png', 'ஆந்தை'), ('eating.png', 'உண்கிறது', 'yellow'), ('', 'நண்பன்', 'light green'), 0.8, ('', 'மிகவும்\\nநல்லது', 'dark green'), 9.0], [('moon_with_star.png', '2024-12-29 03:02:18'), '2024-12-29 03:24:51', '23 நிமிடங்கள்', ('crow.png', 'காகம்'), ('ruling.png', 'ஆள்கிறது', 'dark green'), ('vulture.png', 'கழுகு'), ('sleeping.png', 'தூங்குகிறது', 'orange'), ('', 'நண்பன்', 'light green'), 0.4, ('', 'சராசரி', 'yellow'), 5.0], [('moon_with_star.png', '2024-12-29 03:24:51'), '2024-12-29 04:09:58', '45 நிமிடங்கள்', ('crow.png', 'காகம்'), ('ruling.png', 'ஆள்கிறது', 'dark green'), ('peacock.png', 'மயில்'), ('walking.png', 'நடக்கிறது', 'light green'), ('', 'எதிரி', 'orange'), 0.6, ('', 'சராசரி', 'yellow'), 5.0], [('moon_with_star.png', '2024-12-29 04:09:58'), '2024-12-29 04:25:00', '15 நிமிடங்கள்', ('crow.png', 'காகம்'), ('ruling.png', 'ஆள்கிறது', 'dark green'), ('cock.png', 'சேவல்'), ('dying.png', 'இறக்கிறது', 'red'), ('', 'எதிரி', 'orange'), 0.2, ('', 'மிகவும்\\nமோசமானது', 'red'), 1.0]], [[('moon_with_star.png', '2024-12-29 04:25:00'), '2024-12-29 05:02:35', '38 நிமிடங்கள்', ('crow.png', 'காகம்'), ('eating.png', 'உண்கிறது', 'yellow'), ('crow.png', 'காகம்'), ('eating.png', 'உண்கிறது', 'yellow'), ('', 'சமம்', 'yellow'), 0.64, ('', 'நல்லது', 'light green'), 6.0], [('moon_with_star.png', '2024-12-29 05:02:35'), '2024-12-29 05:25:09', '23 நிமிடங்கள்', ('crow.png', 'காகம்'), ('eating.png', 'உண்கிறது', 'yellow'), ('owl.png', 'ஆந்தை'), ('sleeping.png', 'தூங்குகிறது', 'orange'), ('', 'நண்பன்', 'light green'), 0.32, ('', 'சராசரி', 'yellow'), 4.0], [('moon_with_star.png', '2024-12-29 05:25:09'), '2024-12-29 06:10:15', '45 நிமிடங்கள்', ('crow.png', 'காகம்'), ('eating.png', 'உண்கிறது', 'yellow'), ('vulture.png', 'கழுகு'), ('walking.png', 'நடக்கிறது', 'light green'), ('', 'நண்பன்', 'light green'), 0.48, ('', 'நல்லது', 'light green'), 6.0], [('moon_with_star.png', '2024-12-29 06:10:15'), '2024-12-29 06:25:17', '15 நிமிடங்கள்', ('crow.png', 'காகம்'), ('eating.png', 'உண்கிறது', 'yellow'), ('peacock.png', 'மயில்'), ('dying.png', 'இறக்கிறது', 'red'), ('', 'எதிரி', 'orange'), 0.16, ('', 'மிகவும்\\nமோசமானது', 'red'), 1.0], [('moon_with_star.png', '2024-12-29 06:25:17'), '2024-12-29 07:25:26', '60 நிமிடங்கள்', ('crow.png', 'காகம்'), ('eating.png', 'உண்கிறது', 'yellow'), ('cock.png', 'சேவல்'), ('ruling.png', 'ஆள்கிறது', 'dark green'), ('', 'எதிரி', 'orange'), 0.8, ('', 'நல்லது', 'light green'), 7.0]]]
parent_level_labels =  [[('கிருஷ்ண பட்சம்', ''), ('சனிக்கிழமை', ''), ('பகல் நேரம்', 'day_sun.png'), ('நக்ஷத்ர பக்ஷி : காகம்', 'crow.png'), ('படு பக்ஷி : சேவல்', 'cock.png'), ('பரண பக்ஷி : மயில்', 'peacock.png')], [('கிருஷ்ண பட்சம்', ''), ('சனிக்கிழமை', ''), ('பகல் நேரம்', 'day_sun.png'), ('நக்ஷத்ர பக்ஷி : காகம்', 'crow.png'), ('படு பக்ஷி : சேவல்', 'cock.png'), ('பரண பக்ஷி : மயில்', 'peacock.png')], [('கிருஷ்ண பட்சம்', ''), ('சனிக்கிழமை', ''), ('பகல் நேரம்', 'day_sun.png'), ('நக்ஷத்ர பக்ஷி : காகம்', 'crow.png'), ('படு பக்ஷி : சேவல்', 'cock.png'), ('பரண பக்ஷி : மயில்', 'peacock.png')], [('கிருஷ்ண பட்சம்', ''), ('சனிக்கிழமை', ''), ('பகல் நேரம்', 'day_sun.png'), ('நக்ஷத்ர பக்ஷி : காகம்', 'crow.png'), ('படு பக்ஷி : சேவல்', 'cock.png'), ('பரண பக்ஷி : மயில்', 'peacock.png')], [('கிருஷ்ண பட்சம்', ''), ('சனிக்கிழமை', ''), ('பகல் நேரம்', 'day_sun.png'), ('நக்ஷத்ர பக்ஷி : காகம்', 'crow.png'), ('படு பக்ஷி : சேவல்', 'cock.png'), ('பரண பக்ஷி : மயில்', 'peacock.png')], [('கிருஷ்ண பட்சம்', ''), ('சனிக்கிழமை', ''), ('இரவு நேரம்', 'moon_with_star.png'), ('நக்ஷத்ர பக்ஷி : காகம்', 'crow.png'), ('படு பக்ஷி : சேவல்', 'cock.png'), ('பரண பக்ஷி : சேவல்', 'cock.png')], [('கிருஷ்ண பட்சம்', ''), ('சனிக்கிழமை', ''), ('இரவு நேரம்', 'moon_with_star.png'), ('நக்ஷத்ர பக்ஷி : காகம்', 'crow.png'), ('படு பக்ஷி : சேவல்', 'cock.png'), ('பரண பக்ஷி : சேவல்', 'cock.png')], [('கிருஷ்ண பட்சம்', ''), ('சனிக்கிழமை', ''), ('இரவு நேரம்', 'moon_with_star.png'), ('நக்ஷத்ர பக்ஷி : காகம்', 'crow.png'), ('படு பக்ஷி : சேவல்', 'cock.png'), ('பரண பக்ஷி : சேவல்', 'cock.png')], [('கிருஷ்ண பட்சம்', ''), ('சனிக்கிழமை', ''), ('இரவு நேரம்', 'moon_with_star.png'), ('நக்ஷத்ர பக்ஷி : காகம்', 'crow.png'), ('படு பக்ஷி : சேவல்', 'cock.png'), ('பரண பக்ஷி : சேவல்', 'cock.png')], [('கிருஷ்ண பட்சம்', ''), ('சனிக்கிழமை', ''), ('இரவு நேரம்', 'moon_with_star.png'), ('நக்ஷத்ர பக்ஷி : காகம்', 'crow.png'), ('படு பக்ஷி : சேவல்', 'cock.png'), ('பரண பக்ஷி : சேவல்', 'cock.png')]]
# Usage example
app = QApplication(sys.argv)

#headers = ["From Date/Time", "To Date/Time", "Column 3", "Column 4", "Column 5", "Column 6"]
window = MainWindow()#headers, parent_level_list, parent_level_labels, child_level_list)
window.tree_widget.populate_tree(headers, parent_level_list, parent_level_labels, child_level_list)
window.show()
sys.exit(app.exec_())
