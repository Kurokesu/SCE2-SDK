from PyQt5 import QtCore, QtGui, QtWidgets, uic, QtSvg
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt


class PresetPoint(QWidget):
    clicked_go = pyqtSignal(int, list)
    clicked_set = pyqtSignal(int)

    def __init__(self, name="", nr=0, ch_count=6):
        self.name = name
        self.nr = nr
        self.ch_count = ch_count
        self.values = [0]*ch_count

        QWidget.__init__(self, parent=None)
        self.lay = QVBoxLayout(self)

        self.preset_group = QtWidgets.QGroupBox()
        self.preset_group.setEnabled(False)
        self.preset_group.setGeometry(QtCore.QRect(30, 20, 131, 141))
        self.preset_group.setObjectName("preset_group")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.preset_group)
        self.gridLayout_6.setObjectName("gridLayout_6")
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

        self.preset_group.setTitle(self.name)
        self.btn_go.setText("Go")
        self.label_19.setText("X:")
        self.label_x.setText("--")
        self.label_27.setText("Y:")
        self.label_y.setText("--")
        self.label_29.setText("Z:")
        self.label_z.setText("--")
        self.btn_set.setText("Set")
        self.label_30.setText("A:")
        self.label_a.setText("--")
        self.label_34.setText("B:")
        self.label_b.setText("--")
        self.label_33.setText("C:")
        self.label_c.setText("--")

        self.lay.addWidget(self.preset_group)
        
        self.btn_go.clicked.connect(self.btn_go_clicked)
        self.btn_set.clicked.connect(self.btn_set_clicked)

    def btn_go_clicked(self):
        self.clicked_go.emit(self.nr, self.values)

    def btn_set_clicked(self):
        self.clicked_set.emit(self.nr)

    def set_values(self, ch0=None, ch1=None, ch2=None, ch3=None, ch4=None, ch5=None):     
        if ch0 is not None:
            self.values[0] = ch0
            self.label_x.setText(str(round(ch0,3)))
        
        if ch1 is not None:
            self.values[1] = ch1
            self.label_y.setText(str(round(ch1,3)))
    
        if ch2 is not None:
            self.values[2] = ch2
            self.label_z.setText(str(round(ch2,3)))

        if ch3 is not None:
            self.values[3] = ch3
            self.label_a.setText(str(round(ch3,3)))

        if ch4 is not None:
            self.values[4] = ch4
            self.label_b.setText(str(round(ch4,3)))

        if ch5 is not None:
            self.values[5] = ch5
            self.label_c.setText(str(round(ch5,3)))


    def setEnabled(self, enabled):
        if enabled:
            self.preset_group.setEnabled(True)
        else:
            self.preset_group.setEnabled(False)


class Preset(QWidget):
    clicked_go = pyqtSignal(int, list)
    clicked_set = pyqtSignal(int)

    def __init__(self, parent=None, preset_cnt=2, ch_count=6):
        self.preset_cnt = preset_cnt
        self.parent = parent
        self.ch_count = ch_count
        self.preset_list = [None]*preset_cnt
        
        #QWidget.__init__(self, parent=self.parent)
        #self.lay = QHBoxLayout(self)
        #self.parent.setLayout(self.lay)


        QWidget.__init__(self, parent=None)
        self.lay = parent
        #self.parent.setLayout(self.lay)

        for i in range(self.preset_cnt):
            self.preset_list[i] = PresetPoint(name="Preset "+str(i), nr=i, ch_count=self.ch_count)
            self.lay.addWidget(self.preset_list[i])
            self.preset_list[i].clicked_set.connect(self.widget_set)
            self.preset_list[i].clicked_go.connect(self.widget_go)

        # optional add spacer
        #spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        #self.lay.addItem(spacerItem)
        
    def widget_go(self, nr, values):
        self.clicked_go.emit(nr, values)

    def widget_set(self, nr):
        self.clicked_set.emit(nr)

    def set_values(self, preset, ch0=None, ch1=None, ch2=None, ch3=None, ch4=None, ch5=None):
        self.preset_list[preset].set_values(ch0, ch1, ch2, ch3, ch4, ch5)

    def get_values(self, preset):
        return self.preset_list[preset].values
    
    def setEnabled(self, enabled):
        for i in range(self.preset_cnt):
            self.preset_list[i].setEnabled(enabled)


# fill from dict
# save to dict
# hide unused channels
# use list everywhere, define letters/names later
