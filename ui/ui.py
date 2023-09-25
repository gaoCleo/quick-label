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
        MainWindow.resize(1102, 718)
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
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.btn_add_box = QtWidgets.QPushButton(self.centralwidget)
        self.btn_add_box.setObjectName("btn_add_box")
        self.horizontalLayout_7.addWidget(self.btn_add_box)
        self.btn_revise_box = QtWidgets.QPushButton(self.centralwidget)
        self.btn_revise_box.setObjectName("btn_revise_box")
        self.horizontalLayout_7.addWidget(self.btn_revise_box)
        self.verticalLayout_7.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.btn_add_mask = QtWidgets.QPushButton(self.centralwidget)
        self.btn_add_mask.setObjectName("btn_add_mask")
        self.horizontalLayout_8.addWidget(self.btn_add_mask)
        self.btn_revise_mask = QtWidgets.QPushButton(self.centralwidget)
        self.btn_revise_mask.setObjectName("btn_revise_mask")
        self.horizontalLayout_8.addWidget(self.btn_revise_mask)
        self.verticalLayout_7.addLayout(self.horizontalLayout_8)
        self.line_5 = QtWidgets.QFrame(self.centralwidget)
        self.line_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.verticalLayout_7.addWidget(self.line_5)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.btn_open_dir = QtWidgets.QPushButton(self.centralwidget)
        self.btn_open_dir.setObjectName("btn_open_dir")
        self.horizontalLayout_9.addWidget(self.btn_open_dir)
        self.btn_previous_img = QtWidgets.QPushButton(self.centralwidget)
        self.btn_previous_img.setObjectName("btn_previous_img")
        self.horizontalLayout_9.addWidget(self.btn_previous_img)
        self.btn_next_img = QtWidgets.QPushButton(self.centralwidget)
        self.btn_next_img.setObjectName("btn_next_img")
        self.horizontalLayout_9.addWidget(self.btn_next_img)
        self.verticalLayout_7.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_6.addLayout(self.verticalLayout_7)
        self.line_4 = QtWidgets.QFrame(self.centralwidget)
        self.line_4.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.horizontalLayout_6.addWidget(self.line_4)
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.btn_mode = QtWidgets.QPushButton(self.centralwidget)
        self.btn_mode.setObjectName("btn_mode")
        self.verticalLayout_8.addWidget(self.btn_mode)
        self.btn_ok = QtWidgets.QPushButton(self.centralwidget)
        self.btn_ok.setObjectName("btn_ok")
        self.verticalLayout_8.addWidget(self.btn_ok)
        self.btn_delete_obj = QtWidgets.QPushButton(self.centralwidget)
        self.btn_delete_obj.setObjectName("btn_delete_obj")
        self.verticalLayout_8.addWidget(self.btn_delete_obj)
        self.horizontalLayout_6.addLayout(self.verticalLayout_8)
        self.horizontalLayout_6.setStretch(0, 2)
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
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1102, 26))
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
        self.btn_revise_box.setText(_translate("MainWindow", "revise box"))
        self.btn_add_mask.setText(_translate("MainWindow", "add mask"))
        self.btn_revise_mask.setText(_translate("MainWindow", "revise mask"))
        self.btn_open_dir.setText(_translate("MainWindow", "open dir"))
        self.btn_previous_img.setText(_translate("MainWindow", "<--"))
        self.btn_next_img.setText(_translate("MainWindow", "-->"))
        self.btn_mode.setText(_translate("MainWindow", "…"))
        self.btn_ok.setText(_translate("MainWindow", "❤"))
        self.btn_delete_obj.setText(_translate("MainWindow", "✘"))
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
