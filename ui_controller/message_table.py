from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView

from data_objs import ObjectItem


class MessageTableController:
    def __init__(self, ui_widget):
        self.ui_widget = ui_widget
        self.box = None
        self.category = None
        self.mask = None

    def init_ui(self):
        self.ui_widget.setColumnCount(2)
        self.ui_widget.setHorizontalHeaderLabels(['label', 'value'])

        self.ui_widget.setRowCount(3)
        item_label_box = QTableWidgetItem("box")
        # item_label_box.setFlags(QtCore.Qt.ItemIsEnabled)
        self.ui_widget.setItem(0, 0, item_label_box)

        item_label_mask = QTableWidgetItem("mask")
        # item_label_mask.setFlags(QtCore.Qt.ItemIsEnabled)
        self.ui_widget.setItem(1, 0, item_label_mask)

        item_label_category = QTableWidgetItem("category")
        # item_label_category.setFlags(QtCore.Qt.ItemIsEnabled)
        self.ui_widget.setItem(2, 0, item_label_category)

        self.ui_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui_widget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.item_data_box = QTableWidgetItem("")
        self.ui_widget.setItem(0, 1, self.item_data_box)

        self.item_data_mask = QTableWidgetItem("")
        self.ui_widget.setItem(1, 1, self.item_data_mask)

        self.item_data_category = QTableWidgetItem("")
        self.ui_widget.setItem(2, 1, self.item_data_category)

        self.ui_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    def set_obj_msg(self, obj_item: ObjectItem):
        self._set_box(obj_item.original_coord)
        self._set_category(obj_item.category)

    def clear(self):
        self._set_box('')
        self._set_category('')
        self._set_mask('')

    def _set_box(self, data):
        self.box = data
        self.item_data_box.setText(str(data))

    def _set_category(self, data):
        self.category = data
        self.item_data_category.setText(str(data))

    def _set_mask(self, data):
        self.mask = data
        self.item_data_mask.setText(str(data))