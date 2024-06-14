from PyQt5.QtCore import QObject


class EventAllFilter(QObject):
    def eventFilter(self, obj, event):
        return False