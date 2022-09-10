import logs
import version
#import json
import yaml
import sys
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets, uic, QtSvg
from PyQt5.QtCore import *
#from PyQt5.QtCore import Qt, QTimer, QThread
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import numpy as np
import queue
import utils
import motion
import gui

import logging
LOGGER = logging.getLogger(__name__)
LOGGER.info('start')

COLOR_GREEN = '#33cc33'
COLOR_YELLOW = '#E5B500'
COLOR_RED = '#C0150E'
SETTINGS_FILE = 'config.yaml'


class Status():
    status = str

    limit_x = bool
    limit_y = bool
    limit_z = bool
    limit_a = bool

    pos_x = float
    pos_y = float
    pos_z = float
    pos_a = float

    block_buffer_avail = int
    rx_buffer_avail = int
    


if sys.platform == 'win32':
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)


class VLine(QFrame):
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine|self.Sunken)

class MyWindowClass(QtWidgets.QMainWindow, gui.Ui_MainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.current_motion_profile = None
        self.current_motion_filename = None
        self.hw_connected = False
        self.source_filename = ""        
        self.status = Status()
        self.lens_name = None

        # load settings from json
        self.config = {}
        self.config = utils.boot_routine(SETTINGS_FILE)
        LOGGER.info(self.config)

        # must be set before setupUi        
        pg.setConfigOption('background', (255, 255, 255))
        pg.setConfigOption('foreground', (60, 60, 60))
        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('leftButtonPan', True)

        self.setupUi(self)
        self.original_window_name = self.windowTitle()
        self.setWindowTitle(self.original_window_name + " (" + version.__version__ + ")")



        # wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww

        '''
        #self.plot = self.win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.plot = self.win.addPlot()
        self.plot.showGrid(True, True, 0.2)
        self.plot.setMenuEnabled(enableMenu=False)
        self.plot.hideButtons()
        self.plot.setMouseEnabled(x=False, y=False)
        self.plot_focus_inf = self.plot.plot(pen='blue')
        self.plot_focus_near = self.plot.plot(pen='teal')
        self.plot_focus_ir = self.plot.plot(pen='red')
        self.plot_correction = self.plot.plot(pen='green')
        
        # self.curve = plot.plot(pen=pg.mkPen('r', width=2)) # slow
        #self.phigh = self.plot.plot(pen=(50, 200, 50, 100))
        #self.plow = self.plot.plot(pen=(50, 200, 50, 100))
        #pfill = pg.FillBetweenItem(self.phigh, self.plow, brush=(100, 255, 100, 100))
        #self.plot.addItem(pfill)
        
        # TODO: move to config file, plot once loaded
        # TODO: clean after fresh load
        # TODO: add legend
        pull_off = 0.5
        zoom_inf = [-23.2, -22, -20.81, -19.62, -18.43, -17.23, -16.04, -14.85, -13.65, -12.46, -11.26, -10.08, -8.882, -7.686, -6.49, -5.305, -4.109, -2.913, -1.717, -0.5319, 0.664, 1.86, 3.056, 4.241, 5.437, 6.633, 7.828, 9.014, 10.21, 11.41, 12.6, 13.79, 14.98, 16.18, 17.37, 18.56, 19.76, 20.95, 22.15, 23.33, 24.53, 25.72, 26.92, 28.1, 29.3, 30.5, 31.69, 32.88, 34.07, 35.27]
        focus_inf = [6.41, 1.39, -0.626, -1.86, -2.6, -3.08, -3.32, -3.31, -3.14, -2.79, -2.27, -1.65, -0.859, -0.0256, 0.857, 1.73, 2.6, 3.45, 4.21, 4.92, 5.6, 6.18, 6.69, 7.16, 7.53, 7.85, 8.08, 8.23, 8.33, 8.38, 8.37, 8.31, 8.19, 8.05, 7.88, 7.69, 7.52, 7.3, 7.08, 6.86, 6.63, 6.42, 6.19, 5.96, 5.7, 5.45, 5.18, 4.85, 4.48, 4.08]
        zoom_inf = [x-pull_off for x in zoom_inf]
        focus_inf = [x-pull_off for x in focus_inf]
        self.plot_focus_inf.setData(x=zoom_inf, y=focus_inf)

        zoom_correction = [-23.18, -21.98, -20.8, -19.6, -18.41, -17.22, -16.02, -14.83, -13.63, -12.45, -11.25, -10.06, -8.871, -7.675, -6.479, -5.294, -4.098, -2.902, -1.717, -0.5213, 0.6746, 1.87, 3.056, 4.252, 5.447, 6.633, 7.828, 9.024, 10.21, 11.41, 12.6, 13.8, 14.98, 16.18, 17.37, 18.56, 19.76, 20.95, 22.14, 23.33, 24.53, 25.71, 26.91, 28.1, 29.3, 30.49, 31.68, 32.88, 34.06, 35.26]
        correction = [-1.71, -0.84, -0.216, 0.323, 0.724, 1.14, 1.54, 1.89, 2.26, 2.62, 3.02, 3.42, 3.82, 4.19, 4.54, 4.91, 5.16, 5.37, 5.51, 5.58, 5.59, 5.53, 5.42, 5.26, 5.02, 4.73, 4.38, 4.03, 3.65, 3.21, 2.76, 2.31, 1.81, 1.33, 0.83, 0.333, -0.153, -0.639, -1.09, -1.54, -1.97, -2.39, -2.81, -3.22, -3.64, -4.08, -4.5, -5, -5.5, -6.01]
        zoom_correction = [x-pull_off for x in zoom_correction]
        correction = [x-pull_off for x in correction]
        self.plot_correction.setData(x=zoom_correction, y=correction)

        zoom_near = [-23.19, -21.99, -20.81, -19.61, -18.42, -17.23, -16.04, -14.84, -13.64, -12.46, -11.26, -10.07, -8.882, -7.686, -6.49, -5.305, -4.109, -2.913, -1.728, -0.5319, 0.664, 1.86, 3.045, 4.241, 5.437, 6.622, 7.818, 9.014, 10.2, 11.39, 12.59, 13.79, 14.97, 16.17, 17.36, 18.55, 19.74, 20.94, 22.13, 23.32, 24.52, 25.7, 26.9, 28.09, 29.29, 30.48, 31.67, 32.87, 34.05, 35.25]
        focus_near = [-0.744, -3.51, -4.99, -5.89, -6.22, -6.23, -5.96, -5.56, -4.92, -4.23, -3.42, -2.53, -1.59, -0.629, 0.332, 1.25, 2.19, 3.09, 3.92, 4.67, 5.38, 6, 6.54, 7.03, 7.44, 7.77, 7.99, 8.18, 8.28, 8.33, 8.32, 8.27, 8.15, 8.01, 7.84, 7.67, 7.48, 7.27, 7.06, 6.84, 6.62, 6.4, 6.18, 5.95, 5.7, 5.43, 5.17, 4.86, 4.47, 4.06]
        zoom_near = [x-pull_off for x in zoom_near]
        focus_near = [x-pull_off for x in focus_near]
        self.plot_focus_near.setData(x=zoom_near, y=focus_near)

        zoom_ir = [-11.99, -11.03, -10.07, -9.104, -8.141, -7.167, -6.204, -5.241, -4.278, -3.315, -2.352, -1.389, -0.426, 0.537, 1.5, 2.474, 3.437, 4.4, 5.363, 6.326, 7.289, 8.252, 9.215, 10.18, 11.14, 12.11, 13.08, 14.04, 15, 15.97, 16.93, 17.89, 18.86, 19.82, 20.78, 21.76, 22.72, 23.68, 24.64, 25.61, 26.57, 27.53, 28.5, 29.46, 30.42, 31.4, 32.36, 33.32, 34.29, 35.25]
        focus_ir = [-6.3, -5.26, -4.29, -3.32, -2.36, -1.42, -0.489, 0.442, 1.29, 2.12, 2.9, 3.62, 4.28, 4.92, 5.48, 5.98, 6.44, 6.84, 7.2, 7.51, 7.73, 7.93, 8.06, 8.16, 8.22, 8.22, 8.19, 8.13, 8.06, 7.99, 7.86, 7.71, 7.58, 7.42, 7.26, 7.11, 6.94, 6.76, 6.58, 6.39, 6.21, 6.03, 5.85, 5.65, 5.42, 5.2, 4.97, 4.71, 4.38, 4.04]
        zoom_ir = [x-pull_off for x in zoom_ir]
        focus_ir = [x-pull_off for x in focus_ir]
        self.plot_focus_ir.setData(x=zoom_ir, y=focus_ir)


        # scater data
        self.scatter_focus_zoom = self.plot.plot(pen=None, symbol='x', symbolPen="blue")
        self.scatter_compensate = self.plot.plot(pen=None, symbol='x', symbolPen="green")
        #x_data = [0]
        #y_data = [0]
        #self.scatter_focus_zoom.setData([0], y_data)
        #self.scatter_compensate.setData(x_data, y_data)

        '''










        # set all groups disabled
        self.group_step_size.setEnabled(False)
        self.group_speed.setEnabled(False)
        self.group_mdi.setEnabled(False)
        self.group_filter1.setEnabled(False)
        self.group_filter2.setEnabled(False)
        self.group_pi.setEnabled(False)
        self.group_iris.setEnabled(False)
        self.group_x_axis.setEnabled(False)
        self.group_y_axis.setEnabled(False)
        self.group_z_axis.setEnabled(False)
        self.group_a_axis.setEnabled(False)
        self.group_p1.setEnabled(False)
        self.group_p2.setEnabled(False)
        self.group_p3.setEnabled(False)
        self.group_p4.setEnabled(False)
        self.group_p5.setEnabled(False)


        # Com port
        self.btn_connect.clicked.connect(self.btn_connect_clicked)
        self.btn_disconnect.clicked.connect(self.btn_disconnect_clicked)
        self.btn_com_refresh.clicked.connect(self.btn_com_refresh_clicked)        
        self.btn_mdi_send.clicked.connect(self.btn_mdi_send_clicked)


        # prepare serial communications
        self.hw = motion.SerialComm()
        self.thread_serial = QtCore.QThread()
        self.hw.strStatus.connect(self.serStatus)
        #self.hw.serReceive.connect(self.controller_read)
        #self.hw.current_line_feedback.connect(self.current_line_feedback)
        self.hw.strVersion.connect(self.serVersion)
        self.hw.strError.connect(self.strError)
        self.hw.serFeedback.connect(self.serFeedback)
        self.hw.moveToThread(self.thread_serial)
        self.thread_serial.started.connect(self.hw.serial_worker)
        self.thread_serial.start()
        self.btn_com_refresh_clicked()

        # functions
        self.btn_f1_on.clicked.connect(self.btn_f1_on_clicked)
        self.btn_f1_off.clicked.connect(self.btn_f1_off_clicked)
        self.btn_f2_on.clicked.connect(self.btn_f2_on_clicked)
        self.btn_f2_off.clicked.connect(self.btn_f2_off_clicked)      
        self.btn_pi_led_on.clicked.connect(self.btn_pi_led_on_clicked)
        self.btn_pi_led_off.clicked.connect(self.btn_pi_led_off_clicked)
        self.btn_iris_on.clicked.connect(self.btn_iris_on_clicked)
        self.btn_iris_off.clicked.connect(self.btn_iris_off_clicked)

        self.btn_x_left.clicked.connect(self.btn_x_left_clicked)
        self.btn_x_right.clicked.connect(self.btn_x_right_clicked)
        self.btn_y_left.clicked.connect(self.btn_y_left_clicked)
        self.btn_y_right.clicked.connect(self.btn_y_right_clicked)
        self.btn_z_left.clicked.connect(self.btn_z_left_clicked)
        self.btn_z_right.clicked.connect(self.btn_z_right_clicked)
        self.btn_a_left.clicked.connect(self.btn_a_left_clicked)
        self.btn_a_right.clicked.connect(self.btn_a_right_clicked)
        
        self.btn_x_seek.clicked.connect(self.btn_x_seek_clicked)
        self.btn_y_seek.clicked.connect(self.btn_y_seek_clicked)
        self.btn_z_seek.clicked.connect(self.btn_z_seek_clicked)
        self.btn_a_seek.clicked.connect(self.btn_a_seek_clicked)

        self.push_pr1_set.clicked.connect(self.push_pr1_set_clicked)
        self.push_pr2_set.clicked.connect(self.push_pr2_set_clicked)
        self.push_pr3_set.clicked.connect(self.push_pr3_set_clicked)
        self.push_pr4_set.clicked.connect(self.push_pr4_set_clicked)
        self.push_pr5_set.clicked.connect(self.push_pr5_set_clicked)

        self.push_pr1_go.clicked.connect(self.push_pr1_go_clicked)
        self.push_pr2_go.clicked.connect(self.push_pr2_go_clicked)
        self.push_pr3_go.clicked.connect(self.push_pr3_go_clicked)
        self.push_pr4_go.clicked.connect(self.push_pr4_go_clicked)
        self.push_pr5_go.clicked.connect(self.push_pr5_go_clicked)



        '''
        # Status Bar
        self.s_status = QtWidgets.QLabel("--")
        self.s_status.setToolTip("Motor status")
        self.s_position = QtWidgets.QLabel("--")
        self.s_position.setToolTip("Active motor position")
        self.s_controller_fw = QtWidgets.QLabel("--")
        self.s_controller_fw.setToolTip("Controller firmware")
        self.s_script = QtWidgets.QLabel("--")
        self.s_script.setToolTip("Loaded script name")

        self.statusBar.addPermanentWidget(self.s_status)
        self.statusBar.addPermanentWidget(VLine())
        self.statusBar.addPermanentWidget(self.s_position)
        self.statusBar.addPermanentWidget(VLine())
        self.statusBar.addPermanentWidget(self.s_controller_fw)

        # Menu buttons
        self.action_about.triggered.connect(self.action_about_clicked)
        self.action_settings.triggered.connect(self.action_settings_clicked)
        self.action_manual_control.triggered.connect(self.action_manual_control_clicked)
        self.action_monitor.triggered.connect(self.action_monitor_clicked)
        self.action_edit_motion_script.triggered.connect(self.action_edit_motion_script_clicked)
        self.action_save_script.triggered.connect(self.action_save_script_clicked)
        self.action_save_as_script.triggered.connect(self.action_save_as_script_clicked)
        self.action_load_script.triggered.connect(self.action_load_script_clicked)

        # all other buttons
        self.push_run.clicked.connect(self.push_run_clicked)

        # more UI tweaking
        self.btn_connect.setStyleSheet("background-color: " + COLOR_GREEN)
        children = self.findChildren(QtWidgets.QPushButton)
        for c in children:
            c.setEnabled(False)
        self.btn_connect.setEnabled(True)
        self.btn_com_refresh.setEnabled(True)


        # initialize gcode generator and manual control windows
        self.gcode_generator = gcode_generator.CodeGenerator()
        self.manual_control = manual_control.ManualControl(self.hw)
        self.monitor = monitor.CommunicationsMonitor()
        self.hw.log_tx.connect(self.monitor.add_log_cmd)
        self.hw.log_rx.connect(self.monitor.add_log_response)

        '''



    def push_pr1_go_clicked(self):
        preset = self.config["lens"][self.lens_name]["preset"]["p1"].split(" ")  
        cmd =  "G90"
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_x"]:
            cmd += " X"
            cmd += preset[0]
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_y"]:
            cmd += " Y"
            cmd += preset[1]
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_z"]:
            cmd += " Z"
            cmd += preset[2]
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_a"]:
            cmd += " A"
            cmd += preset[3]
        cmd += " F"
        cmd += self.combo_speed.currentText()
        self.hw.send(cmd+"\n")

    def push_pr2_go_clicked(self):
        preset = self.config["lens"][self.lens_name]["preset"]["p2"].split(" ")  
        cmd =  "G90"
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_x"]:
            cmd += " X"
            cmd += preset[0]
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_y"]:
            cmd += " Y"
            cmd += preset[1]
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_z"]:
            cmd += " Z"
            cmd += preset[2]
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_a"]:
            cmd += " A"
            cmd += preset[3]
        cmd += " F"
        cmd += self.combo_speed.currentText()
        self.hw.send(cmd+"\n")

    def push_pr3_go_clicked(self):
        preset = self.config["lens"][self.lens_name]["preset"]["p3"].split(" ")  
        cmd =  "G90"
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_x"]:
            cmd += " X"
            cmd += preset[0]
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_y"]:
            cmd += " Y"
            cmd += preset[1]
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_z"]:
            cmd += " Z"
            cmd += preset[2]
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_a"]:
            cmd += " A"
            cmd += preset[3]
        cmd += " F"
        cmd += self.combo_speed.currentText()
        self.hw.send(cmd+"\n")

    def push_pr4_go_clicked(self):
        preset = self.config["lens"][self.lens_name]["preset"]["p4"].split(" ")  
        cmd =  "G90"
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_x"]:
            cmd += " X"
            cmd += preset[0]
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_y"]:
            cmd += " Y"
            cmd += preset[1]
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_z"]:
            cmd += " Z"
            cmd += preset[2]
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_a"]:
            cmd += " A"
            cmd += preset[3]
        cmd += " F"
        cmd += self.combo_speed.currentText()
        self.hw.send(cmd+"\n")

    def push_pr5_go_clicked(self):
        preset = self.config["lens"][self.lens_name]["preset"]["p5"].split(" ")  
        cmd =  "G90"
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_x"]:
            cmd += " X"
            cmd += preset[0]
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_y"]:
            cmd += " Y"
            cmd += preset[1]
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_z"]:
            cmd += " Z"
            cmd += preset[2]
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_a"]:
            cmd += " A"
            cmd += preset[3]
        cmd += " F"
        cmd += self.combo_speed.currentText()
        self.hw.send(cmd+"\n")



    def push_pr1_set_clicked(self):
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_x"]:
            val_x = str(self.status.pos_x)
        else:
            val_x = "--"

        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_y"]:
            val_y = str(self.status.pos_y)
        else:
            val_y = "--"

        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_z"]:
            val_z = str(self.status.pos_z)
        else:
            val_z = "--"

        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_a"]:
            val_a = str(self.status.pos_a)
        else:
            val_a = "--"

        self.config["lens"][self.lens_name]["preset"]["p1"] = val_x+" "+val_y+" "+val_z+" "+val_a

        self.label_pr1_x.setText(val_x)
        self.label_pr1_y.setText(val_y)
        self.label_pr1_z.setText(val_z)
        self.label_pr1_a.setText(val_a)
        

    def push_pr2_set_clicked(self):
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_x"]:
            val_x = str(self.status.pos_x)
        else:
            val_x = "--"

        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_y"]:
            val_y = str(self.status.pos_y)
        else:
            val_y = "--"

        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_z"]:
            val_z = str(self.status.pos_z)
        else:
            val_z = "--"

        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_a"]:
            val_a = str(self.status.pos_a)
        else:
            val_a = "--"

        self.config["lens"][self.lens_name]["preset"]["p2"] = val_x+" "+val_y+" "+val_z+" "+val_a

        self.label_pr2_x.setText(val_x)
        self.label_pr2_y.setText(val_y)
        self.label_pr2_z.setText(val_z)
        self.label_pr2_a.setText(val_a)
        

    def push_pr3_set_clicked(self):
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_x"]:
            val_x = str(self.status.pos_x)
        else:
            val_x = "--"

        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_y"]:
            val_y = str(self.status.pos_y)
        else:
            val_y = "--"

        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_z"]:
            val_z = str(self.status.pos_z)
        else:
            val_z = "--"

        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_a"]:
            val_a = str(self.status.pos_a)
        else:
            val_a = "--"

        self.config["lens"][self.lens_name]["preset"]["p3"] = val_x+" "+val_y+" "+val_z+" "+val_a

        self.label_pr3_x.setText(val_x)
        self.label_pr3_y.setText(val_y)
        self.label_pr3_z.setText(val_z)
        self.label_pr3_a.setText(val_a)
        

    def push_pr4_set_clicked(self):
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_x"]:
            val_x = str(self.status.pos_x)
        else:
            val_x = "--"

        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_y"]:
            val_y = str(self.status.pos_y)
        else:
            val_y = "--"

        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_z"]:
            val_z = str(self.status.pos_z)
        else:
            val_z = "--"

        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_a"]:
            val_a = str(self.status.pos_a)
        else:
            val_a = "--"

        self.config["lens"][self.lens_name]["preset"]["p4"] = val_x+" "+val_y+" "+val_z+" "+val_a

        self.label_pr4_x.setText(val_x)
        self.label_pr4_y.setText(val_y)
        self.label_pr4_z.setText(val_z)
        self.label_pr4_a.setText(val_a)
        

    def push_pr5_set_clicked(self):
        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_x"]:
            val_x = str(self.status.pos_x)
        else:
            val_x = "--"

        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_y"]:
            val_y = str(self.status.pos_y)
        else:
            val_y = "--"

        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_z"]:
            val_z = str(self.status.pos_z)
        else:
            val_z = "--"

        if self.config["lens"][self.lens_name]["motor"]["function"]["axis_a"]:
            val_a = str(self.status.pos_a)
        else:
            val_a = "--"

        self.config["lens"][self.lens_name]["preset"]["p5"] = val_x+" "+val_y+" "+val_z+" "+val_a

        self.label_pr5_x.setText(val_x)
        self.label_pr5_y.setText(val_y)
        self.label_pr5_z.setText(val_z)
        self.label_pr5_a.setText(val_a)






    def btn_x_seek_clicked(self):
        cmd = "$HX"
        self.hw.send(cmd+"\n")

    def btn_y_seek_clicked(self):
        cmd = "$HY"
        self.hw.send(cmd+"\n")

    def btn_z_seek_clicked(self):
        cmd = "$HZ"
        self.hw.send(cmd+"\n")

    def btn_a_seek_clicked(self):
        cmd = "$HA"
        self.hw.send(cmd+"\n")



    def btn_x_left_clicked(self):
        cmd = "G91 X-"
        cmd += str(self.combo_step.currentText())
        cmd += " F"
        cmd += str(self.combo_speed.currentText())
        self.hw.send(cmd+"\n")

    def btn_x_right_clicked(self):
        cmd = "G91 X"
        cmd += str(self.combo_step.currentText())
        cmd += " F"
        cmd += str(self.combo_speed.currentText())
        self.hw.send(cmd+"\n")

    def btn_y_left_clicked(self):
        cmd = "G91 Y-"
        cmd += str(self.combo_step.currentText())
        cmd += " F"
        cmd += str(self.combo_speed.currentText())
        self.hw.send(cmd+"\n")

    def btn_y_right_clicked(self):
        cmd = "G91 Y"
        cmd += str(self.combo_step.currentText())
        cmd += " F"
        cmd += str(self.combo_speed.currentText())
        self.hw.send(cmd+"\n")

    def btn_z_left_clicked(self):
        cmd = "G91 Z-"
        cmd += str(self.combo_step.currentText())
        cmd += " F"
        cmd += str(self.combo_speed.currentText())
        self.hw.send(cmd+"\n")

    def btn_z_right_clicked(self):
        cmd = "G91 Z"
        cmd += str(self.combo_step.currentText())
        cmd += " F"
        cmd += str(self.combo_speed.currentText())
        self.hw.send(cmd+"\n")

    def btn_a_left_clicked(self):
        cmd = "G91 A-"
        cmd += str(self.combo_step.currentText())
        cmd += " F"
        cmd += str(self.combo_speed.currentText())
        self.hw.send(cmd+"\n")

    def btn_a_right_clicked(self):
        cmd = "G91 A"
        cmd += str(self.combo_step.currentText())
        cmd += " F"
        cmd += str(self.combo_speed.currentText())
        self.hw.send(cmd+"\n")



    def btn_f1_on_clicked(self):
        cmd = self.config["lens"][self.lens_name]["filter1"]["state_on"]

        if type(cmd) == str:
            self.hw.send(cmd+"\n")

        if type(cmd) == list:
            for c in cmd:
                self.hw.send(c+"\n")

    def btn_f1_off_clicked(self):
        cmd = self.config["lens"][self.lens_name]["filter1"]["state_off"]

        if type(cmd) == str:
            self.hw.send(cmd+"\n")

        if type(cmd) == list:
            for c in cmd:
                self.hw.send(c+"\n")

    def btn_f2_on_clicked(self):
        cmd = self.config["lens"][self.lens_name]["filter2"]["state_on"]

        if type(cmd) == str:
            self.hw.send(cmd+"\n")

        if type(cmd) == list:
            for c in cmd:
                self.hw.send(c+"\n")

    def btn_f2_off_clicked(self):
        cmd = self.config["lens"][self.lens_name]["filter2"]["state_off"]

        if type(cmd) == str:
            self.hw.send(cmd+"\n")

        if type(cmd) == list:
            for c in cmd:
                self.hw.send(c+"\n")


    def btn_pi_led_on_clicked(self):
        cmd = self.config["lens"][self.lens_name]["limit_sensor"]["led_on"]
        self.hw.send(cmd+"\n")

    def btn_pi_led_off_clicked(self):
        cmd = self.config["lens"][self.lens_name]["limit_sensor"]["led_off"]
        self.hw.send(cmd+"\n")

    def btn_iris_on_clicked(self):
        cmd = self.config["lens"][self.lens_name]["iris"]["open"]
        self.hw.send(cmd+"\n")
       

    def btn_iris_off_clicked(self):
        cmd = self.config["lens"][self.lens_name]["iris"]["close"]
        self.hw.send(cmd+"\n")

        



    def btn_mdi_send_clicked(self):
        self.hw.send(self.line_mdi.text()+"\n")

    def btn_connect_clicked(self):
        self.config["port"] = self.combo_ports.currentText()
        self.hw.connect(self.config["port"], self.config["com_baud"], self.config["com_timeout"])

    def btn_disconnect_clicked(self):
        self.hw.disconnect()

    def btn_com_refresh_clicked(self):
        self.combo_ports.clear()
        com_ports = sorted(self.hw.get_compot_list())
        for port, desc in com_ports:
            self.combo_ports.addItem(port.strip())
        self.combo_ports.setCurrentIndex(self.combo_ports.findText(self.config["port"]))

    def serStatus(self, text):
        self.s_status.setText(text)
        self.combo_ports.setEnabled(False)
        self.btn_connect.setEnabled(False)
        self.btn_disconnect.setEnabled(False)
        
        if text == "Connected":
            self.hw_connected = True
            self.hw.action_recipe.put("status1")
            self.hw.action_recipe.put("version")
            self.hw.action_recipe.put("get_param_list")
            
        if text == "Disconnected":
            self.hw_connected = False

        self.update_enabled_elements()


    def update_enabled_elements(self):
        if not self.hw.commands.empty():
            self.push_run.setEnabled(False)

        if self.hw_connected:
            self.combo_ports.setEnabled(False)
            self.btn_connect.setEnabled(False)
            self.btn_com_refresh.setEnabled(False)
            self.btn_disconnect.setEnabled(True)
            #self.btn_connect.setStyleSheet("")

        else:
            self.combo_ports.setEnabled(True)
            self.btn_connect.setEnabled(True)
            self.btn_com_refresh.setEnabled(True)
            self.btn_disconnect.setEnabled(False)
            #self.btn_connect.setStyleSheet("background-color: " + COLOR_GREEN)


    def strError(self, text):
        LOGGER.error(text)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(text)
        msg.setWindowTitle("Error")
        msg.exec_()


    def serVersion(self, text):
        self.s_controller_fw.setText(text)

        # Expecting: [VER:1.1f-SCE2.20211130:L086,6ZG-BEG19]
        txt = text.replace('[', '').replace(']', '')

        txt_list = txt.split(':')    
        id_strings = txt_list[2].split(',')

        for i in id_strings:

            lens_detected = False
            if i[0:3] == "LS8":
                self.lens_name = "L085"
                self.label_lens_name.setText(self.lens_name)
                lens_detected = True

            if i[0:3] == "6ZG":
                self.lens_name = "L086"
                self.label_lens_name.setText(self.lens_name)
                lens_detected = True

            if i[0:3] == "JWF":
                self.lens_name = "L084"
                self.label_lens_name.setText(self.lens_name)
                lens_detected = True




            if lens_detected:
                cmd = self.config["lens"][self.lens_name]["limit_sensor"]["led_on"]
                self.hw.send(cmd+"\n")
                cmd = self.config["lens"][self.lens_name]["iris"]["open"]
                self.hw.send(cmd+"\n")

                self.group_step_size.setEnabled(True)
                self.combo_step.clear()                
                default_step = None
                step_list = self.config["lens"][self.lens_name]["motor"]["step_list"].split(" ")
                for i in step_list:
                    if "*" in i:
                        default_step = i.replace("*", "")
                    self.combo_step.addItem(i.replace("*", ""))
                if default_step:
                    self.combo_step.setCurrentText(default_step)


                self.group_speed.setEnabled(True)
                self.combo_speed.clear()                
                default_speed = None
                speed_list = self.config["lens"][self.lens_name]["motor"]["speed_list"].split(" ")
                for i in speed_list:
                    if "*" in i:
                        default_speed = i.replace("*", "")
                    self.combo_speed.addItem(i.replace("*", ""))
                if default_speed:
                    self.combo_speed.setCurrentText(default_speed)


                self.group_mdi.setEnabled(True)


                if "filter1"  in self.config["lens"][self.lens_name]:
                    self.group_filter1.setEnabled(True)
                    self.group_filter1.setTitle("Filter: "+self.config["lens"][self.lens_name]["filter1"]["name"])

                if "filter2"  in self.config["lens"][self.lens_name]:
                    self.group_filter2.setEnabled(True)
                    self.group_filter2.setTitle("Filter: "+self.config["lens"][self.lens_name]["filter2"]["name"])


                self.group_pi.setEnabled(True)


                if "iris"  in self.config["lens"][self.lens_name]:
                    self.group_iris.setEnabled(True)


                self.group_p1.setEnabled(True)
                self.group_p2.setEnabled(True)
                self.group_p3.setEnabled(True)
                self.group_p4.setEnabled(True)
                self.group_p5.setEnabled(True)

                preset = self.config["lens"][self.lens_name]["preset"]["p1"].split(" ")
                self.label_pr1_x.setText(preset[0])
                self.label_pr1_y.setText(preset[1])
                self.label_pr1_z.setText(preset[2])
                self.label_pr1_a.setText(preset[3])

                preset = self.config["lens"][self.lens_name]["preset"]["p2"].split(" ")
                self.label_pr2_x.setText(preset[0])
                self.label_pr2_y.setText(preset[1])
                self.label_pr2_z.setText(preset[2])
                self.label_pr2_a.setText(preset[3])

                preset = self.config["lens"][self.lens_name]["preset"]["p3"].split(" ")
                self.label_pr3_x.setText(preset[0])
                self.label_pr3_y.setText(preset[1])
                self.label_pr3_z.setText(preset[2])
                self.label_pr3_a.setText(preset[3])

                preset = self.config["lens"][self.lens_name]["preset"]["p4"].split(" ")
                self.label_pr4_x.setText(preset[0])
                self.label_pr4_y.setText(preset[1])
                self.label_pr4_z.setText(preset[2])
                self.label_pr4_a.setText(preset[3])

                preset = self.config["lens"][self.lens_name]["preset"]["p5"].split(" ")
                self.label_pr5_x.setText(preset[0])
                self.label_pr5_y.setText(preset[1])
                self.label_pr5_z.setText(preset[2])
                self.label_pr5_a.setText(preset[3])



                if self.config["lens"][self.lens_name]["motor"]["function"]["axis_x"]:
                    self.group_x_axis.setEnabled(True)
                    self.group_x_axis.setTitle("X axis / " + self.config["lens"][self.lens_name]["motor"]["function"]["axis_x"])

                if self.config["lens"][self.lens_name]["motor"]["function"]["axis_y"]:
                    self.group_y_axis.setEnabled(True)
                    self.group_y_axis.setTitle("Y axis / " + self.config["lens"][self.lens_name]["motor"]["function"]["axis_y"])

                if self.config["lens"][self.lens_name]["motor"]["function"]["axis_z"]:
                    self.group_z_axis.setEnabled(True)
                    self.group_z_axis.setTitle("Z axis / " + self.config["lens"][self.lens_name]["motor"]["function"]["axis_z"])

                if self.config["lens"][self.lens_name]["motor"]["function"]["axis_a"]:
                    self.group_a_axis.setEnabled(True)
                    self.group_a_axis.setTitle("A axis / " + self.config["lens"][self.lens_name]["motor"]["function"]["axis_a"])




                # ------------------

                #self.plot = self.win.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
                self.plot = self.win.addPlot()
                self.plot.showGrid(True, True, 0.2)
                self.plot.setMenuEnabled(enableMenu=False)
                self.plot.hideButtons()
                self.plot.setMouseEnabled(x=False, y=False)
                self.plot_focus_inf = self.plot.plot(pen='blue')
                self.plot_focus_near = self.plot.plot(pen='teal')
                self.plot_focus_ir = self.plot.plot(pen='red')
                self.plot_correction = self.plot.plot(pen='green')
                
                # self.curve = plot.plot(pen=pg.mkPen('r', width=2)) # slow
                #self.phigh = self.plot.plot(pen=(50, 200, 50, 100))
                #self.plow = self.plot.plot(pen=(50, 200, 50, 100))
                #pfill = pg.FillBetweenItem(self.phigh, self.plow, brush=(100, 255, 100, 100))
                #self.plot.addItem(pfill)
                
                # TODO: move to config file, plot once loaded
                # TODO: clean after fresh load
                # TODO: add legend
                pull_off = 0.5
                zoom_inf = [-23.2, -22, -20.81, -19.62, -18.43, -17.23, -16.04, -14.85, -13.65, -12.46, -11.26, -10.08, -8.882, -7.686, -6.49, -5.305, -4.109, -2.913, -1.717, -0.5319, 0.664, 1.86, 3.056, 4.241, 5.437, 6.633, 7.828, 9.014, 10.21, 11.41, 12.6, 13.79, 14.98, 16.18, 17.37, 18.56, 19.76, 20.95, 22.15, 23.33, 24.53, 25.72, 26.92, 28.1, 29.3, 30.5, 31.69, 32.88, 34.07, 35.27]
                focus_inf = [6.41, 1.39, -0.626, -1.86, -2.6, -3.08, -3.32, -3.31, -3.14, -2.79, -2.27, -1.65, -0.859, -0.0256, 0.857, 1.73, 2.6, 3.45, 4.21, 4.92, 5.6, 6.18, 6.69, 7.16, 7.53, 7.85, 8.08, 8.23, 8.33, 8.38, 8.37, 8.31, 8.19, 8.05, 7.88, 7.69, 7.52, 7.3, 7.08, 6.86, 6.63, 6.42, 6.19, 5.96, 5.7, 5.45, 5.18, 4.85, 4.48, 4.08]
                zoom_inf = [x-pull_off for x in zoom_inf]
                focus_inf = [x-pull_off for x in focus_inf]
                self.plot_focus_inf.setData(x=zoom_inf, y=focus_inf)

                zoom_correction = [-23.18, -21.98, -20.8, -19.6, -18.41, -17.22, -16.02, -14.83, -13.63, -12.45, -11.25, -10.06, -8.871, -7.675, -6.479, -5.294, -4.098, -2.902, -1.717, -0.5213, 0.6746, 1.87, 3.056, 4.252, 5.447, 6.633, 7.828, 9.024, 10.21, 11.41, 12.6, 13.8, 14.98, 16.18, 17.37, 18.56, 19.76, 20.95, 22.14, 23.33, 24.53, 25.71, 26.91, 28.1, 29.3, 30.49, 31.68, 32.88, 34.06, 35.26]
                correction = [-1.71, -0.84, -0.216, 0.323, 0.724, 1.14, 1.54, 1.89, 2.26, 2.62, 3.02, 3.42, 3.82, 4.19, 4.54, 4.91, 5.16, 5.37, 5.51, 5.58, 5.59, 5.53, 5.42, 5.26, 5.02, 4.73, 4.38, 4.03, 3.65, 3.21, 2.76, 2.31, 1.81, 1.33, 0.83, 0.333, -0.153, -0.639, -1.09, -1.54, -1.97, -2.39, -2.81, -3.22, -3.64, -4.08, -4.5, -5, -5.5, -6.01]
                zoom_correction = [x-pull_off for x in zoom_correction]
                correction = [x-pull_off for x in correction]
                self.plot_correction.setData(x=zoom_correction, y=correction)

                zoom_near = [-23.19, -21.99, -20.81, -19.61, -18.42, -17.23, -16.04, -14.84, -13.64, -12.46, -11.26, -10.07, -8.882, -7.686, -6.49, -5.305, -4.109, -2.913, -1.728, -0.5319, 0.664, 1.86, 3.045, 4.241, 5.437, 6.622, 7.818, 9.014, 10.2, 11.39, 12.59, 13.79, 14.97, 16.17, 17.36, 18.55, 19.74, 20.94, 22.13, 23.32, 24.52, 25.7, 26.9, 28.09, 29.29, 30.48, 31.67, 32.87, 34.05, 35.25]
                focus_near = [-0.744, -3.51, -4.99, -5.89, -6.22, -6.23, -5.96, -5.56, -4.92, -4.23, -3.42, -2.53, -1.59, -0.629, 0.332, 1.25, 2.19, 3.09, 3.92, 4.67, 5.38, 6, 6.54, 7.03, 7.44, 7.77, 7.99, 8.18, 8.28, 8.33, 8.32, 8.27, 8.15, 8.01, 7.84, 7.67, 7.48, 7.27, 7.06, 6.84, 6.62, 6.4, 6.18, 5.95, 5.7, 5.43, 5.17, 4.86, 4.47, 4.06]
                zoom_near = [x-pull_off for x in zoom_near]
                focus_near = [x-pull_off for x in focus_near]
                self.plot_focus_near.setData(x=zoom_near, y=focus_near)

                zoom_ir = [-11.99, -11.03, -10.07, -9.104, -8.141, -7.167, -6.204, -5.241, -4.278, -3.315, -2.352, -1.389, -0.426, 0.537, 1.5, 2.474, 3.437, 4.4, 5.363, 6.326, 7.289, 8.252, 9.215, 10.18, 11.14, 12.11, 13.08, 14.04, 15, 15.97, 16.93, 17.89, 18.86, 19.82, 20.78, 21.76, 22.72, 23.68, 24.64, 25.61, 26.57, 27.53, 28.5, 29.46, 30.42, 31.4, 32.36, 33.32, 34.29, 35.25]
                focus_ir = [-6.3, -5.26, -4.29, -3.32, -2.36, -1.42, -0.489, 0.442, 1.29, 2.12, 2.9, 3.62, 4.28, 4.92, 5.48, 5.98, 6.44, 6.84, 7.2, 7.51, 7.73, 7.93, 8.06, 8.16, 8.22, 8.22, 8.19, 8.13, 8.06, 7.99, 7.86, 7.71, 7.58, 7.42, 7.26, 7.11, 6.94, 6.76, 6.58, 6.39, 6.21, 6.03, 5.85, 5.65, 5.42, 5.2, 4.97, 4.71, 4.38, 4.04]
                zoom_ir = [x-pull_off for x in zoom_ir]
                focus_ir = [x-pull_off for x in focus_ir]
                self.plot_focus_ir.setData(x=zoom_ir, y=focus_ir)


                # scater data
                self.scatter_focus_zoom = self.plot.plot(pen=None, symbol='x', symbolPen="blue")
                self.scatter_compensate = self.plot.plot(pen=None, symbol='x', symbolPen="green")
                #x_data = [0]
                #y_data = [0]
                #self.scatter_focus_zoom.setData([0], y_data)
                #self.scatter_compensate.setData(x_data, y_data)




                

    def serFeedback(self, text):
        txt = text.replace('<', '').replace('>', '')
        txt_list = txt.split("|")
        s = Status()
        s.status = txt_list[0] # allways first element

        for p in txt_list[1:]:
            if p[0:2] == "Bf":
                temp1 = p.split(":")[1]
                s.block_buffer_avail = int(temp1.split(",")[0])
                s.rx_buffer_avail = int(temp1.split(",")[1])

            s.limit_x = False
            s.limit_y = False
            s.limit_z = False
            s.limit_a = False

            if p[0:2] == "Pn":
                temp1 = p.split(":")[1]
                s.limit_x = "X" in temp1
                s.limit_y = "Y" in temp1
                s.limit_z = "Z" in temp1
                s.limit_a = "A" in temp1

            if p[0:4] == "MPos":
                temp1 = p.split(":")[1]
                s.pos_x = float(temp1.split(",")[0])
                s.pos_y = float(temp1.split(",")[1])
                s.pos_z = float(temp1.split(",")[2])
                s.pos_a = float(temp1.split(",")[3])

        self.status = s


        # setting data to the scatter plot
        if self.lens_name:
            self.scatter_focus_zoom.setData([s.pos_x], [s.pos_y])
            self.scatter_compensate.setData([s.pos_x], [s.pos_z])

        self.label_x_pos.setText(str(round(s.pos_x,3)))
        self.label_y_pos.setText(str(round(s.pos_y,3)))
        self.label_z_pos.setText(str(round(s.pos_z,3)))
        self.label_a_pos.setText(str(round(s.pos_a,3)))

        self.btn_x_seek.setEnabled(True)
        self.btn_y_seek.setEnabled(True)
        self.btn_z_seek.setEnabled(True)
        self.btn_a_seek.setEnabled(True)


        '''
        if s.limit_x:
            self.label_x_pi.setText('LOW')
            self.label_x_pi.setStyleSheet("color: " + COLOR_RED)
            self.btn_x_seek.setEnabled(False)
        else:
            self.label_x_pi.setText('HIGH')
            self.label_x_pi.setStyleSheet("")
            self.btn_x_seek.setEnabled(True)

        if s.limit_y:
            self.label_y_pi.setText('LOW')
            self.label_y_pi.setStyleSheet("color: " + COLOR_RED)
            self.btn_y_seek.setEnabled(False)
        else:
            self.label_y_pi.setText('HIGH')
            self.label_y_pi.setStyleSheet("")
            self.btn_y_seek.setEnabled(True)

        if s.limit_z:
            self.label_z_pi.setText('LOW')
            self.label_z_pi.setStyleSheet("color: " + COLOR_RED)
            self.btn_z_seek.setEnabled(False)
        else:
            self.label_z_pi.setText('HIGH')
            self.label_z_pi.setStyleSheet("")
            self.btn_z_seek.setEnabled(True)

        if s.limit_a:
            self.label_a_pi.setText('LOW')
            self.label_a_pi.setStyleSheet("color: " + COLOR_RED)
            self.btn_a_seek.setEnabled(False)
        else:
            self.label_a_pi.setText('HIGH')
            self.label_a_pi.setStyleSheet("")
            self.btn_a_seek.setEnabled(True)
        '''


        self.label_buffer_count.setText(str(s.block_buffer_avail))
        self.label_motion_status.setText(str(s.status))




        '''
        if len(text) < 5:
            return None

        if text[0] != "<":
            return None

        if not ((text[0] == "<") and (text[-1] == ">")):
            raise Exception("Bad format 1")

        text = text[1:-1]
        feedback_split = text.split("|")

        status["STATUS"] = feedback_split[0]

        if feedback_split[1].find("MPos") < 0:
            raise Exception("Bad format 2")

        positions = feedback_split[1].split(":")
        if len(positions) != 2:
            raise Exception("Bad format 3")

        positions = positions[1]
        positions = positions.split(",")
        if len(positions) != 4:
            raise Exception("Bad format 4")

        status["MPOS_X"] = float(positions[0])
        status["MPOS_Y"] = float(positions[1])
        status["MPOS_Z"] = float(positions[2])
        status["MPOS_A"] = float(positions[3])

        positions = feedback_split[2].split(":")
        if len(positions) != 2:
            raise Exception("Bad format 5")

        positions = positions[1]
        positions = positions.split(",")
        if len(positions) != 2:
            raise Exception("Bad format 6")

        status["BUFFERS"] = int(positions[0])

        active_axis = self.gcode_generator.dialog.ui.combo_active_axis.currentText()
        mpos_x = float(status["MPOS_"+active_axis])
        self.s_position.setText("{:.2f}°".format(mpos_x))

        commands_in_buffer = self.hw.commands.qsize()
        self.progress_program.setValue(self.progress_program.maximum() - int(commands_in_buffer))
        self.s_status.setText(status["STATUS"])
        self.update_enabled_elements()
        '''




    '''
    def push_run_clicked(self):
        line_count = 0
        for line in self.current_motion_profile["text"]["text_gcode"].splitlines():
            self.hw.send(line+"\n")
            line_count += 1

        self.progress_program.setMaximum(line_count)
        self.progress_program.setValue(line_count)

        self.update_enabled_elements()


    def controller_read(self, data):
        pass




    def action_about_clicked(self):
        dialog = QtWidgets.QDialog()
        dialog.ui = about_ui.Ui_About()
        dialog.ui.setupUi(dialog)
        dialog.exec_()

    def action_settings_clicked(self):
        dialog = QtWidgets.QDialog()
        dialog.ui = settings_ui.Ui_Settings()
        dialog.ui.setupUi(dialog)

        dialog.ui.check_remember_last_com_port.setChecked(self.config["remember_last_com_port"])

        ret = dialog.exec_()
        if ret:
            self.config["remember_last_com_port"] = dialog.ui.check_remember_last_com_port.isChecked()

    def action_edit_motion_script_clicked(self):
        ret = self.gcode_generator.show_modal()
        if ret:
            self.gcode_generator.push_generate_clicked()
            active_axis = self.gcode_generator.dialog.ui.combo_active_axis.currentText()
            self.manual_control.set_active_axis(active_axis)

            values = self.gcode_generator.collect_values()
            self.current_motion_profile = values
            self.action_save_script.setEnabled(True)

        self.update_enabled_elements()

    def action_manual_control_clicked(self):
        self.manual_control.show()

    def action_monitor_clicked(self):
        self.monitor.show()

    def current_line_feedback(self, text):
        if len(text)>2:
            if text[0] == ";":
                text_ = text[1:].strip()
                self.label_gcode_comment.setText(text_)

    def action_save_script_clicked(self):
        with open(self.source_filename, 'w') as outfile:
            json.dump(self.current_motion_profile, outfile)

    def action_save_as_script_clicked(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "Save motion script as...", "", "Motion script (*.profile)")
        if fileName:
            with open(fileName, 'w') as outfile:
                json.dump(self.current_motion_profile, outfile)


    def action_load_script_clicked(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open motion script...", "", "Motion script (*.profile)")
        if fileName:
            with open(fileName) as json_file:
                self.current_motion_profile = json.load(json_file)
                self.gcode_generator.populate_values(self.current_motion_profile)

                script_name = Path(fileName).stem
                self.s_script.setText(script_name)
                self.update_enabled_elements()
                self.action_save_script.setEnabled(True)
                self.action_save_as_script.setEnabled(True)
                self.source_filename = fileName


    '''

    def closeEvent(self, event):
        global config
        global running

        if self.s_status.text() == "Connected":
            p1 = self.label_pr1_x.text()+" "+self.label_pr1_y.text()+" "+self.label_pr1_z.text()+" "+self.label_pr1_a.text()
            self.config["lens"][self.lens_name]["preset"]["p1"] = p1

            p2 = self.label_pr2_x.text()+" "+self.label_pr2_y.text()+" "+self.label_pr2_z.text()+" "+self.label_pr2_a.text()
            self.config["lens"][self.lens_name]["preset"]["p2"] = p2

            p3 = self.label_pr3_x.text()+" "+self.label_pr3_y.text()+" "+self.label_pr3_z.text()+" "+self.label_pr3_a.text()
            self.config["lens"][self.lens_name]["preset"]["p3"] = p3

            p4 = self.label_pr4_x.text()+" "+self.label_pr4_y.text()+" "+self.label_pr4_z.text()+" "+self.label_pr4_a.text()
            self.config["lens"][self.lens_name]["preset"]["p4"] = p4

            p5 = self.label_pr5_x.text()+" "+self.label_pr5_y.text()+" "+self.label_pr5_z.text()+" "+self.label_pr5_a.text()
            self.config["lens"][self.lens_name]["preset"]["p5"] = p5

        utils.exit_routine(SETTINGS_FILE, self.config)
        running = False
        app.quit()


app = QtWidgets.QApplication(sys.argv)
app.setStyle('Fusion')
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()
