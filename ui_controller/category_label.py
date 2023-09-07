from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QListWidget, QListWidgetItem


class LabelController:
    def __init__(self, lw: QListWidget):
        self.lw = lw

    def init_ui(self, color: str, category: str):
        self.add_category_label(color, category)

    def add_category_label(self, color: str, category: str):
        icon = QIcon(QPixmap(f'color_icons/{color}.png'))
        list_item = QListWidgetItem(icon, category)
        self.lw.addItem(list_item)