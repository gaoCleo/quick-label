from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from data_objs import ObjectItem


class ObjectListController:
    def __init__(self, list_widget: QListWidget):
        self.lw = list_widget

    def add_obj(self, obj_item: ObjectItem, color: str):
        icon = QIcon(QPixmap(f'color_icons/{color}.png'))
        list_item = QListWidgetItem(icon, obj_item.category)
        self.lw.addItem(list_item)
        return list_item

    def remove_listitem(self, item: QListWidgetItem):
        self.lw.removeItemWidget(item)
        self.lw.takeItem(self.lw.row(item))
        del item

    def set_selected(self, item: QListWidgetItem):
        self.lw.setCurrentItem(item)

    def cancel_select(self):
        if self.lw.currentItem() is not None:
            self.lw.currentItem().setSelected(False)

    def revise_object(self, obj_item: ObjectItem, color: str):
        if self.lw.currentItem() is not None:
            self.lw.currentItem().setText(obj_item.category)

            icon = QIcon(QPixmap(f'color_icons/{color}.png'))
            self.lw.currentItem().setIcon(icon)
