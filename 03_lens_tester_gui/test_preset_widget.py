# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test_preset_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(291, 324)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.preset_group = QtWidgets.QGroupBox(self.centralwidget)
        self.preset_group.setEnabled(True)
        self.preset_group.setGeometry(QtCore.QRect(30, 20, 131, 141))
        self.preset_group.setObjectName("preset_group")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.preset_group)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.horizontalLayout_33 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_33.setObjectName("horizontalLayout_33")
        self.label_34 = QtWidgets.QLabel(self.preset_group)
        self.label_34.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_34.setObjectName("label_34")
        self.horizontalLayout_33.addWidget(self.label_34)
        self.label_b = QtWidgets.QLabel(self.preset_group)
        self.label_b.setMinimumSize(QtCore.QSize(40, 0))
        self.label_b.setObjectName("label_b")
        self.horizontalLayout_33.addWidget(self.label_b)
        self.gridLayout_6.addLayout(self.horizontalLayout_33, 3, 0, 1, 1)
        self.horizontalLayout_40 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_40.setObjectName("horizontalLayout_40")
        self.label_33 = QtWidgets.QLabel(self.preset_group)
        self.label_33.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_33.setObjectName("label_33")
        self.horizontalLayout_40.addWidget(self.label_33)
        self.label_c = QtWidgets.QLabel(self.preset_group)
        self.label_c.setMinimumSize(QtCore.QSize(40, 0))
        self.label_c.setObjectName("label_c")
        self.horizontalLayout_40.addWidget(self.label_c)
        self.gridLayout_6.addLayout(self.horizontalLayout_40, 3, 1, 1, 1)
        self.btn_go = QtWidgets.QPushButton(self.preset_group)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_go.sizePolicy().hasHeightForWidth())
        self.btn_go.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.btn_go.setFont(font)
        self.btn_go.setObjectName("btn_go")
        self.gridLayout_6.addWidget(self.btn_go, 0, 0, 1, 2)
        self.horizontalLayout_26 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_26.setObjectName("horizontalLayout_26")
        self.label_19 = QtWidgets.QLabel(self.preset_group)
        self.label_19.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_19.setObjectName("label_19")
        self.horizontalLayout_26.addWidget(self.label_19)
        self.label_x = QtWidgets.QLabel(self.preset_group)
        self.label_x.setMinimumSize(QtCore.QSize(40, 0))
        self.label_x.setObjectName("label_x")
        self.horizontalLayout_26.addWidget(self.label_x)
        self.gridLayout_6.addLayout(self.horizontalLayout_26, 1, 0, 1, 1)
        self.horizontalLayout_30 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_30.setObjectName("horizontalLayout_30")
        self.label_27 = QtWidgets.QLabel(self.preset_group)
        self.label_27.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_27.setObjectName("label_27")
        self.horizontalLayout_30.addWidget(self.label_27)
        self.label_y = QtWidgets.QLabel(self.preset_group)
        self.label_y.setMinimumSize(QtCore.QSize(40, 0))
        self.label_y.setObjectName("label_y")
        self.horizontalLayout_30.addWidget(self.label_y)
        self.gridLayout_6.addLayout(self.horizontalLayout_30, 1, 1, 1, 1)
        self.horizontalLayout_31 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_31.setObjectName("horizontalLayout_31")
        self.label_29 = QtWidgets.QLabel(self.preset_group)
        self.label_29.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_29.setObjectName("label_29")
        self.horizontalLayout_31.addWidget(self.label_29)
        self.label_z = QtWidgets.QLabel(self.preset_group)
        self.label_z.setMinimumSize(QtCore.QSize(40, 0))
        self.label_z.setObjectName("label_z")
        self.horizontalLayout_31.addWidget(self.label_z)
        self.gridLayout_6.addLayout(self.horizontalLayout_31, 2, 0, 1, 1)
        self.btn_set = QtWidgets.QPushButton(self.preset_group)
        self.btn_set.setObjectName("btn_set")
        self.gridLayout_6.addWidget(self.btn_set, 5, 0, 1, 2)
        self.horizontalLayout_38 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_38.setObjectName("horizontalLayout_38")
        self.label_30 = QtWidgets.QLabel(self.preset_group)
        self.label_30.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_30.setObjectName("label_30")
        self.horizontalLayout_38.addWidget(self.label_30)
        self.label_a = QtWidgets.QLabel(self.preset_group)
        self.label_a.setMinimumSize(QtCore.QSize(40, 0))
        self.label_a.setObjectName("label_a")
        self.horizontalLayout_38.addWidget(self.label_a)
        self.gridLayout_6.addLayout(self.horizontalLayout_38, 2, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 291, 21))
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
        self.preset_group.setTitle(_translate("MainWindow", "Preset 1"))
        self.label_34.setText(_translate("MainWindow", "B:"))
        self.label_b.setText(_translate("MainWindow", "--"))
        self.label_33.setText(_translate("MainWindow", "C:"))
        self.label_c.setText(_translate("MainWindow", "--"))
        self.btn_go.setText(_translate("MainWindow", "Go"))
        self.label_19.setText(_translate("MainWindow", "X:"))
        self.label_x.setText(_translate("MainWindow", "--"))
        self.label_27.setText(_translate("MainWindow", "Y:"))
        self.label_y.setText(_translate("MainWindow", "--"))
        self.label_29.setText(_translate("MainWindow", "Z:"))
        self.label_z.setText(_translate("MainWindow", "--"))
        self.btn_set.setText(_translate("MainWindow", "Set"))
        self.label_30.setText(_translate("MainWindow", "A:"))
        self.label_a.setText(_translate("MainWindow", "--"))
