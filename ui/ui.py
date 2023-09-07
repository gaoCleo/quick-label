# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1086, 675)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.view = DrawableView(self.centralwidget)
        self.view.setObjectName("view")
        self.verticalLayout_4.addWidget(self.view)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.btn_add_box = QtWidgets.QPushButton(self.centralwidget)
        self.btn_add_box.setObjectName("btn_add_box")
        self.horizontalLayout_6.addWidget(self.btn_add_box)
        self.btn_revise = QtWidgets.QPushButton(self.centralwidget)
        self.btn_revise.setObjectName("btn_revise")
        self.horizontalLayout_6.addWidget(self.btn_revise)
        self.btn_delete_obj = QtWidgets.QPushButton(self.centralwidget)
        self.btn_delete_obj.setObjectName("btn_delete_obj")
        self.horizontalLayout_6.addWidget(self.btn_delete_obj)
        self.btn_ok = QtWidgets.QPushButton(self.centralwidget)
        self.btn_ok.setObjectName("btn_ok")
        self.horizontalLayout_6.addWidget(self.btn_ok)
        self.horizontalLayout_6.setStretch(0, 1)
        self.horizontalLayout_6.setStretch(1, 1)
        self.horizontalLayout_6.setStretch(2, 1)
        self.verticalLayout_4.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_3.addLayout(self.verticalLayout_4)
        self.lw_objs = QtWidgets.QListWidget(self.centralwidget)
        self.lw_objs.setObjectName("lw_objs")
        self.horizontalLayout_3.addWidget(self.lw_objs)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_3.addWidget(self.label_3)
        self.tw_obj_message = QtWidgets.QTableWidget(self.centralwidget)
        self.tw_obj_message.setObjectName("tw_obj_message")
        self.tw_obj_message.setColumnCount(0)
        self.tw_obj_message.setRowCount(0)
        self.verticalLayout_3.addWidget(self.tw_obj_message)
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout_3.addWidget(self.line_2)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_3.addWidget(self.label_4)
        self.lw_labels = QtWidgets.QListWidget(self.centralwidget)
        self.lw_labels.setObjectName("lw_labels")
        self.verticalLayout_3.addWidget(self.lw_labels)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.btn_add_category = QtWidgets.QPushButton(self.centralwidget)
        self.btn_add_category.setObjectName("btn_add_category")
        self.horizontalLayout_5.addWidget(self.btn_add_category)
        self.btn_delete_category = QtWidgets.QPushButton(self.centralwidget)
        self.btn_delete_category.setObjectName("btn_delete_category")
        self.horizontalLayout_5.addWidget(self.btn_delete_category)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_3.addWidget(self.line)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.le_prompt = QtWidgets.QLineEdit(self.centralwidget)
        self.le_prompt.setObjectName("le_prompt")
        self.horizontalLayout_2.addWidget(self.le_prompt)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_4.addWidget(self.label_2)
        self.lb_default_category = QtWidgets.QLabel(self.centralwidget)
        self.lb_default_category.setObjectName("lb_default_category")
        self.horizontalLayout_4.addWidget(self.lb_default_category)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.btn_open_pic = QtWidgets.QPushButton(self.centralwidget)
        self.btn_open_pic.setObjectName("btn_open_pic")
        self.verticalLayout.addWidget(self.btn_open_pic)
        self.btn_save_pic = QtWidgets.QPushButton(self.centralwidget)
        self.btn_save_pic.setObjectName("btn_save_pic")
        self.verticalLayout.addWidget(self.btn_save_pic)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.btn_detect_box = QtWidgets.QPushButton(self.centralwidget)
        self.btn_detect_box.setObjectName("btn_detect_box")
        self.verticalLayout_2.addWidget(self.btn_detect_box)
        self.btn_detect_mask = QtWidgets.QPushButton(self.centralwidget)
        self.btn_detect_mask.setObjectName("btn_detect_mask")
        self.verticalLayout_2.addWidget(self.btn_detect_mask)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout_3.addWidget(self.progressBar)
        self.verticalLayout_3.setStretch(1, 1)
        self.verticalLayout_3.setStretch(4, 1)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)
        self.horizontalLayout_3.setStretch(0, 5)
        self.horizontalLayout_3.setStretch(1, 1)
        self.horizontalLayout_3.setStretch(2, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1086, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btn_add_box.setText(_translate("MainWindow", "add box"))
        self.btn_revise.setText(_translate("MainWindow", "revise box"))
        self.btn_delete_obj.setText(_translate("MainWindow", "delete box"))
        self.btn_ok.setText(_translate("MainWindow", "❤"))
        self.label_3.setText(_translate("MainWindow", "object annotations"))
        self.label_4.setText(_translate("MainWindow", "category labels"))
        self.btn_add_category.setText(_translate("MainWindow", "add category"))
        self.btn_delete_category.setText(_translate("MainWindow", "delete category"))
        self.label.setText(_translate("MainWindow", "prompt"))
        self.label_2.setText(_translate("MainWindow", "default category: "))
        self.lb_default_category.setText(_translate("MainWindow", "object"))
        self.btn_open_pic.setText(_translate("MainWindow", "open"))
        self.btn_save_pic.setText(_translate("MainWindow", "save"))
        self.btn_detect_box.setText(_translate("MainWindow", "detect box"))
        self.btn_detect_mask.setText(_translate("MainWindow", "detect mask"))
from ui.canvas_ui import DrawableView
