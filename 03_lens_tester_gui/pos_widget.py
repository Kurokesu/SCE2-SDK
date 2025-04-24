from PyQt5 import QtCore, QtGui, QtWidgets, uic, QtSvg
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt


class PosAxis(QWidget):

    moved = pyqtSignal(int, int)
    value = None
    pi = None

    def __init__(self, name="", nr=0):
        self.name = name
        self.nr = nr

        QWidget.__init__(self, parent=None)
        self.lay = QVBoxLayout(self)
        
        self.group = QtWidgets.QGroupBox()
        self.group.setEnabled(False)
        self.group.setGeometry(QtCore.QRect(50, 50, 276, 79))
        self.group.setObjectName("group_x_axis")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.group)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.verticalLayout_15 = QtWidgets.QVBoxLayout()
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.label_x_pos = QtWidgets.QLabel(self.group)
        self.label_x_pos.setMinimumSize(QtCore.QSize(90, 0))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_x_pos.setFont(font)
        self.label_x_pos.setObjectName("label_x_pos")
        self.verticalLayout_15.addWidget(self.label_x_pos)
        self.label_x_pi = QtWidgets.QLabel(self.group)
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_x_pi.setFont(font)
        self.label_x_pi.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_x_pi.setObjectName("label_x_pi")
        self.verticalLayout_15.addWidget(self.label_x_pi)
        self.horizontalLayout_13.addLayout(self.verticalLayout_15)
        self.gridLayout_2.addLayout(self.horizontalLayout_13, 0, 3, 1, 1)
        self.btn_right = QtWidgets.QPushButton(self.group)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_right.sizePolicy().hasHeightForWidth())
        self.btn_right.setSizePolicy(sizePolicy)
        self.btn_right.setAutoRepeat(True)
        self.btn_right.setAutoRepeatInterval(50)
        self.btn_right.setObjectName("btn_x_right")
        self.gridLayout_2.addWidget(self.btn_right, 0, 1, 1, 1)
        self.btn_left = QtWidgets.QPushButton(self.group)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_left.sizePolicy().hasHeightForWidth())
        self.btn_left.setSizePolicy(sizePolicy)
        self.btn_left.setAutoRepeat(True)
        self.btn_left.setAutoRepeatInterval(50)
        self.btn_left.setObjectName("btn_left")
        self.gridLayout_2.addWidget(self.btn_left, 0, 0, 1, 1)

        self.group.setTitle(self.name)
        self.label_x_pos.setText("---")
        self.label_x_pi.setText("---")
        self.btn_right.setText(">")
        self.btn_left.setText("<")
        self.lay.addWidget(self.group)
        
        self.btn_right.clicked.connect(self.move_right)
        self.btn_left.clicked.connect(self.move_left)

    def set_name(self, name):
        self.name = name
        self.group.setTitle(self.name)

    def move_right(self):
        self.moved.emit(self.nr, 0)

    def move_left(self):
        self.moved.emit(self.nr, 1)

    def set_value(self, pos, pi):
        self.value = pos
        self.pi = pi
        self.label_x_pos.setText(str(round(self.value,3)))
        
        if self.pi:
            self.label_x_pi.setText("HIGH")
        else:
            self.label_x_pi.setText("LOW")

    def setEnabled(self, enabled):
        if enabled:
            self.group.setEnabled(True)
        else:
            self.group.setEnabled(False)
        

class Pos(QWidget):
    #                         ch,  dir 0=left, 1=right 
    moved = pyqtSignal(int, int)   
    axis_names = ["X", "Y", "Z", "A", "B", "C"]

    def __init__(self, parent=None, ch_count=4):
        self.ch_count = ch_count
        self.pos_list = [None]*ch_count
        
        QWidget.__init__(self, parent=None)
        self.lay = parent

        for i in range(self.ch_count):
            self.pos_list[i] = PosAxis(name=self.axis_names[i]+" axis", nr=i)
            self.lay.addWidget(self.pos_list[i])
            self.pos_list[i].moved.connect(self.clicked_move)

        #self.pos_list[1].set_name("test")
        #self.pos_list[1].set_value(32.2, True)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.lay.addItem(spacerItem)

    def clicked_move(self, nr, direction):
        self.moved.emit(nr, direction)
        #print("aaa", nr, direction)

    def setEnabled(self, enabled):
        for i in range(self.ch_count):
            self.pos_list[i].setEnabled(enabled)

    def set_name(self, ch, name):
        self.pos_list[ch].set_name(name)

    def set_value(self, ch, pos, pi):
        self.pos_list[ch].set_value(pos, pi)
    

