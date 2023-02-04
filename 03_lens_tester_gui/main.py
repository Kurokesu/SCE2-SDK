import logs
import version
import yaml
import ezdxf
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
from scipy.interpolate import interp1d
import keypoints
import time

import logging
LOGGER = logging.getLogger(__name__)
LOGGER.info('start')

SETTINGS_FILE = 'config.yaml'


def approximate_spline(data_x, data_y, point_count):
    doc = ezdxf.new(dxfversion='R2010')

    control_points = []
    for i in range(len(data_x)):
        control_points.append((data_x[i], data_y[i], 0))

    msp = doc.modelspace()
    spline = msp.add_open_spline(control_points)

    bspline = spline.construction_tool()
    xy_pts = [p.xy for p in bspline.approximate(segments=point_count)]
    msp.add_polyline2d(xy_pts)

    x_values = []
    y_values = []
    for i in xy_pts:
        x_values.append(i[0])
        y_values.append(i[1])

    return((x_values, y_values))
   


class Status():
    status = str

    limit_x = bool
    limit_y = bool
    limit_z = bool
    limit_a = bool
    limit_available = bool

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
        self.zoom_slider_memory = 0
        self.focus_slider_memory = 50
        self.dbg_keypoints = None
        self.last_updated_pos = 0

        s_global = Status()

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


        # set all groups disabled
        self.group_step_size.setEnabled(False)
        self.group_lens.setEnabled(False)
        self.group_speed.setEnabled(False)
        self.group_mdi.setEnabled(False)
        self.group_filter1.setEnabled(False)
        self.group_filter2.setEnabled(False)
        self.group_pi.setEnabled(False)
        self.group_iris.setEnabled(False)
        self.group_homing.setEnabled(False)
        self.group_keypoints_2.setEnabled(False)
        self.group_guided_zoom1.setEnabled(False)
        self.group_guided_focus1.setEnabled(False)
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
        self.hw.log_rx.connect(self.add_log_response)
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
        self.btn_all_seek.clicked.connect(self.btn_all_seek_clicked)

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
        
        #self.btn_new_keypoint.clicked.connect(self.btn_new_keypoint_clicked)
        #self.btn_keypoint_mark_focused.clicked.connect(self.btn_keypoint_mark_focused_clicked)
        #self.btn_save_keypoint_miny.clicked.connect(self.btn_save_keypoint_miny_clicked)
        #self.btn_save_keypoint_maxy.clicked.connect(self.btn_save_keypoint_maxy_clicked)
        #self.btn_save_keypoint_minz.clicked.connect(self.btn_save_keypoint_minz_clicked)
        #self.btn_save_keypoint_maxz.clicked.connect(self.btn_save_keypoint_maxz_clicked)
        #self.btn_new_keypoint_file.clicked.connect(self.btn_new_keypoint_file_clicked)
        #self.btn_reset.clicked.connect(self.btn_reset_clicked)

        self.zoom_slider1.valueChanged.connect(self.zoom_slider1_changed)
        self.focus_slider1.valueChanged.connect(self.focus_slider1_changed)
        
        self.push_kpt_new.clicked.connect(self.push_kpt_new_clicked)
        self.push_kpt_delete.clicked.connect(self.push_kpt_delete_clicked)
        self.push_kpt_go.clicked.connect(self.push_kpt_go_clicked)
        self.push_kpt_set.clicked.connect(self.push_kpt_set_clicked)
        self.comboBox_keypoints.currentTextChanged.connect(self.comboBox_keypoints_changed)


        self.timer=QTimer()
        self.timer.timeout.connect(self.check_motor_pos)
        #self.timer.start(1000)


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

        '''


    def comboBox_keypoints_changed(self, value):
        if len(value)>0:
            p = self.dbg_keypoints.points[int(value)]
            self.label_dk_x.setText(str(p[0]))
            self.label_dk_y.setText(str(p[1]))
            self.label_dk_z.setText(str(p[2]))
            self.label_dk_a.setText(str(p[3]))        
        
    def push_kpt_new_clicked(self):
        nr = self.dbg_keypoints.add_point([self.status.pos_x, self.status.pos_y, self.status.pos_z, self.status.pos_a])
        #print(nr)
        
        if nr == -1:
            QMessageBox.critical(self, "Add point failed", 'Duplicate X point not allowed!')        

        self.comboBox_keypoints.clear()
        items = []
        for i in range(len(self.dbg_keypoints.points)):
            items.append(str(i))
        self.comboBox_keypoints.addItems(items)

        if nr > -1:
            self.comboBox_keypoints.setCurrentIndex(nr)
        
    def push_kpt_delete_clicked(self):
        id = self.comboBox_keypoints.currentText()
        if len(id)>0:           
            id = int(id)
            nr = self.dbg_keypoints.delete_point(id)

            self.comboBox_keypoints.clear()
            items = []
            for i in range(len(self.dbg_keypoints.points)):
                items.append(str(i))
            self.comboBox_keypoints.addItems(items)

            if nr > -1:
                self.comboBox_keypoints.setCurrentIndex(nr)
        
    def push_kpt_set_clicked(self):
        id = self.comboBox_keypoints.currentText()
        if len(id) > 0:
            id = int(id)
            nr = self.dbg_keypoints.set_point(id, [self.status.pos_x, self.status.pos_y, self.status.pos_z, self.status.pos_a])

            if nr > -1:
                self.comboBox_keypoints.setCurrentIndex(nr)

            p = self.dbg_keypoints.points[nr]
            self.label_dk_x.setText(str(p[0]))
            self.label_dk_y.setText(str(p[1]))
            self.label_dk_z.setText(str(p[2]))
            self.label_dk_a.setText(str(p[3]))        



    def push_kpt_go_clicked(self):
        id = self.comboBox_keypoints.currentText()
        if len(id) > 0:
            id = int(id)
            p = self.dbg_keypoints.points[id]

            cmd =  "G90 G1"
            cmd += " X"
            cmd += str(p[0])
            cmd += " Y"
            cmd += str(p[1])
            cmd += " Z"
            cmd += str(p[2])
            cmd += " A"
            cmd += str(p[3])
            cmd += " F"
            cmd += self.combo_speed.currentText()
            self.hw.send(cmd+"\n")

    
    def btn_reset_clicked(self):
        # this works
        #self.hw.send_buffered('\x18')
        #self.hw.send_buffered('?')

        # ---------

        #self.hw.send_buffered(bytes.fromhex('18'))
  
        #M120 P1
        #cmd = "M254"
        #self.hw.send_buffered(cmd+"\n")

        #cmd = "M120 P1"
        #self.hw.send_buffered(cmd+"\n")
        pass



    def focus_slider1_changed(self, value):
        interpolate_count = self.config["lens"][self.lens_name]["motor"]["interpolate_count"]
        curve_focus_inf = self.config["lens"][self.lens_name]["motor"]["curves"]["focus_inf"]
        curve_focus_near = self.config["lens"][self.lens_name]["motor"]["curves"]["focus_near"]

        f1 = interp1d(curve_focus_inf["x"], curve_focus_inf["y"], kind='cubic')
        f3 = interp1d(curve_focus_near["x"], curve_focus_near["y"], kind='cubic')

        x_pos = float(self.label_x_pos.text())
        new_focus_pos = f1(x_pos)+(f3(x_pos)-f1(x_pos))*value/100
        if self.lens_name == "L084":
            cmd = "G90 G1"
            cmd += " Y"+str(new_focus_pos)
            cmd += " F2000"
            self.hw.send_buffered(cmd+"\n")

        if self.lens_name == "L117":
            cmd = "G90 G1"
            cmd += " Z"+str(new_focus_pos)
            cmd += " F2000"
            self.hw.send_buffered(cmd+"\n")
        
        if self.lens_name == "L086":
            cmd = "G90 G1"
            cmd += " Z"+str(new_focus_pos)
            cmd += " F2000"
            self.hw.send_buffered(cmd+"\n")


    def zoom_slider1_changed(self, value):
        interpolate_count = self.config["lens"][self.lens_name]["motor"]["interpolate_count"]
        curve_focus_inf = self.config["lens"][self.lens_name]["motor"]["curves"]["focus_inf"]
        curve_zoom_correction = self.config["lens"][self.lens_name]["motor"]["curves"]["zoom_correction"]

        f1 = interp1d(curve_focus_inf["x"], curve_focus_inf["y"], kind='cubic')
        x1new = np.linspace(min(curve_focus_inf["x"]), max(curve_focus_inf["x"]), num=interpolate_count, endpoint=True)

        f2 = interp1d(curve_zoom_correction["x"], curve_zoom_correction["y"], kind='cubic')
        x2new = np.linspace(min(curve_zoom_correction["x"]), max(curve_zoom_correction["x"]), num=interpolate_count, endpoint=True)

        i_min = min(curve_zoom_correction["x"])
        i_max = max(curve_zoom_correction["x"])

        normalized100 = interp1d((0, 100), (i_max, i_min))
        pos_from = self.zoom_slider_memory
        #pos_to = self.sender().value()
        pos_to = value
        diff = np.abs(pos_from-pos_to)
        resolution = 0.5
        self.zoom_slider_memory = pos_to # backup last value


        if self.lens_name == "L084":
            for i in np.linspace(normalized100(pos_from), normalized100(pos_to), int(diff/resolution), endpoint=True):
                cmd = "G90 G1"
                cmd += " X"+str(i)
                cmd += " Y"+str(f1(i))
                cmd += " Z"+str(f2(i))
                cmd += " F2000"
                self.hw.send_buffered(cmd+"\n")

        if self.lens_name == "L117":
            for i in np.linspace(normalized100(pos_from), normalized100(pos_to), int(diff/resolution), endpoint=True):
                cmd = "G90 G1"
                cmd += " X"+str(i)
                cmd += " Y"+str(f2(i))
                cmd += " Z"+str(f1(i))
                cmd += " F2000"
                self.hw.send_buffered(cmd+"\n")

        if self.lens_name == "L086":
            for i in np.linspace(normalized100(pos_from), normalized100(pos_to), int(diff/resolution), endpoint=True):
                cmd = "G90 G1"
                cmd += " X"+str(i)
                cmd += " Y"+str(f2(i))
                cmd += " Z"+str(f1(i))
                cmd += " F2000"
                self.hw.send_buffered(cmd+"\n")
                

    '''        
    def btn_new_keypoint_file_clicked(self):
        self.kpt = keypoints.Keypoints(self.lens_name)
        self.kpt.save()

        self.btn_new_keypoint_file.setEnabled(False)
        self.btn_new_keypoint.setEnabled(True)
        # TODO: make all gray and disabled again

        #self.btn_save_keypoint_minx.setEnabled(True)
        #self.btn_save_keypoint_miny.setEnabled(True)
        #self.btn_save_keypoint_minz.setEnabled(True)
        #self.btn_save_keypoint_mina.setEnabled(True)
        #self.btn_save_keypoint_maxx.setEnabled(True)
        #self.btn_save_keypoint_maxy.setEnabled(True)
        #self.btn_save_keypoint_maxz.setEnabled(True)
        #self.btn_save_keypoint_maxa.setEnabled(True)
    '''

    '''
    def btn_new_keypoint_clicked(self):
        self.kpt.new_kp()
        self.kpt.save()

        self.btn_keypoint_mark_focused.setStyleSheet("")
        self.btn_save_keypoint_miny.setStyleSheet("")
        self.btn_save_keypoint_maxy.setStyleSheet("")
        self.btn_save_keypoint_minz.setStyleSheet("")
        self.btn_save_keypoint_maxz.setStyleSheet("")
        
        self.btn_new_keypoint.setEnabled(False)
        self.btn_keypoint_mark_focused.setEnabled(True)
        #self.btn_x_left.setEnabled(False)
        #self.btn_x_right.setEnabled(False)

        #self.label_keypoint_count.setText(str(self.kpt.count))

        #self.btn_save_keypoint_minx.setEnabled(True)
        #self.btn_save_keypoint_maxx.setEnabled(True)

        self.btn_save_keypoint_miny.setEnabled(True)
        self.btn_save_keypoint_maxy.setEnabled(True)

        self.btn_save_keypoint_minz.setEnabled(True)
        self.btn_save_keypoint_maxz.setEnabled(True)
        
        #self.btn_save_keypoint_mina.setEnabled(True)
        #self.btn_save_keypoint_maxa.setEnabled(True)

        #self.btn_save_keypoint_minx.setStyleSheet("background-color: " + COLOR_GREEN)
        #print(self.btn_keypoint_mark_focused.styleSheet())
    '''

    '''
    def btn_keypoint_mark_focused_clicked(self):
        self.btn_keypoint_mark_focused.setStyleSheet("background-color: " + COLOR_GREEN)
        self.kpt.set_kp_val("x", self.s_global.pos_x)    
        self.kpt.set_kp_val("y", self.s_global.pos_y)    
        self.kpt.set_kp_val("z", self.s_global.pos_z)    
        self.kpt.save()

        if self.kpt.validate_point():
            self.btn_new_keypoint.setEnabled(True)
    
    def btn_save_keypoint_miny_clicked(self):
        self.btn_save_keypoint_miny.setStyleSheet("background-color: " + COLOR_GREEN)
        self.kpt.set_kp_val("miny", self.s_global.pos_y)
        self.kpt.save()

        if self.kpt.validate_point():
            self.btn_new_keypoint.setEnabled(True)

    def btn_save_keypoint_maxy_clicked(self):
        self.btn_save_keypoint_maxy.setStyleSheet("background-color: " + COLOR_GREEN)
        self.kpt.set_kp_val("maxy", self.s_global.pos_y)
        self.kpt.save()

        if self.kpt.validate_point():
            self.btn_new_keypoint.setEnabled(True)

    def btn_save_keypoint_minz_clicked(self):
        self.btn_save_keypoint_minz.setStyleSheet("background-color: " + COLOR_GREEN)
        self.kpt.set_kp_val("minz", self.s_global.pos_z)
        self.kpt.save()

        if self.kpt.validate_point():
            self.btn_new_keypoint.setEnabled(True)

    def btn_save_keypoint_maxz_clicked(self):
        self.btn_save_keypoint_maxz.setStyleSheet("background-color: " + COLOR_GREEN)
        self.kpt.set_kp_val("maxz", self.s_global.pos_z)
        self.kpt.save()

        if self.kpt.validate_point():
            self.btn_new_keypoint.setEnabled(True)
    '''

  
    def push_pr1_go_clicked(self):
        preset = self.config["lens"][self.lens_name]["preset"]["p1"].split(" ")  
        cmd =  "G90 G1"
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
        cmd =  "G90 G1"
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
        cmd =  "G90 G1"
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
        cmd =  "G90 G1"
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
        cmd =  "G90 G1"
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


    def btn_all_seek_clicked(self):
        # If command is issued when lens is in telephoto position it stalls
        #cmd = "$H"
        #self.hw.send(cmd+"\n")


        if self.lens_name == "L084":
            cmd = "$HX"
            self.hw.send(cmd+"\n")
            cmd = "$HY"
            self.hw.send(cmd+"\n")
            cmd = "$HZ"
            self.hw.send(cmd+"\n")
            cmd = "$HA"
            self.hw.send(cmd+"\n")

        if self.lens_name == "L117":
            # Workaround. Sometimes if Z is in -4..-2 Y axis can't home
            cmd = "G91 G0 Z2"
            self.hw.send(cmd+"\n")

            cmd = "$HA"
            self.hw.send(cmd+"\n")
            cmd = "$HX"
            self.hw.send(cmd+"\n")                              
            cmd = "$HY"
            self.hw.send(cmd+"\n")
            cmd = "$HZ"
            self.hw.send(cmd+"\n")

        if self.lens_name == "L086":
            cmd = "$HX"
            self.hw.send(cmd+"\n")
            cmd = "$HY"
            self.hw.send(cmd+"\n")
            cmd = "$HZ"
            self.hw.send(cmd+"\n")


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
            self.timer.start(100)
            
            
        if text == "Disconnected":
            self.hw_connected = False
            self.timer.stop()

        self.update_enabled_elements()


    def update_enabled_elements(self):
        if not self.hw.commands.empty():
            self.push_run.setEnabled(False)

        if self.hw_connected:
            self.combo_ports.setEnabled(False)
            self.btn_connect.setEnabled(False)
            self.btn_com_refresh.setEnabled(False)
            self.btn_disconnect.setEnabled(True)
            

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
                lens_detected = True

            if i[0:3] == "6ZG":
                self.lens_name = "L086"
                lens_detected = True

            if i[0:3] == "JWF":
                self.lens_name = "L084"
                lens_detected = True

            if i[0:3] == "EFJ":
                self.lens_name = "L117"
                lens_detected = True


            if lens_detected:
                self.label_lens_name.setText(self.lens_name)

                self.config["last_lens"] = self.lens_name
                #self.btn_new_keypoint_file.setEnabled(True)

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
                self.group_lens.setEnabled(True)

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
                self.group_homing.setEnabled(True)
                self.group_guided_zoom1.setEnabled(True)
                self.group_guided_focus1.setEnabled(True)
                self.group_keypoints_2.setEnabled(True)

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


                # RRRRRRRRRRRRRRRRRR
                self.dbg_keypoints = keypoints.Keypoints(self.config["lens"][self.lens_name]["debug_keypoints"])

                items = []
                for i in range(len(self.dbg_keypoints.points)):
                    items.append(str(i))
                self.comboBox_keypoints.addItems(items)


               

                # ------------------

                self.plot = self.win.addPlot()
                self.plot.showGrid(True, True, 0.2)
                self.plot.setMenuEnabled(enableMenu=False)
                self.plot.hideButtons()
                self.plot.setMouseEnabled(x=False, y=False)
                self.plot.addLegend()
                                                
                # TODO: clean after fresh load
                
                interpolate_count = 100 # TBD: move to config

                for curve in self.config["lens"][self.lens_name]["motor"]["curves"]:
                    try:
                        lens_yaml = self.config["lens"][self.lens_name]["motor"]["curves"][curve]
                        pull_off = lens_yaml["pulloff"]
                        data_x = lens_yaml["x"]
                        data_y = lens_yaml["y"]
                        data_x = [i-pull_off for i in data_x]
                        data_y = [i-pull_off for i in data_y]

                        # Dots                        
                        pen1 = pg.mkPen(color=lens_yaml["color"])
                        im_p = self.plot.plot(pen=None, symbol='o', symbolSize = 3, symbolPen=pen1)
                        im_p.setData(data_x, data_y)
                                            
                        # Wrong interpolation curve
                        #(data_x, data_y) = approximate_spline(data_x, data_y, interpolate_count)
                        #self.plot_focus_inf.setData(x=data_x, y=data_y)

                        # Interpolated curve
                        f2 = interp1d(data_x, data_y, kind='cubic')
                        xnew = np.linspace(min(data_x), max(data_x), num=interpolate_count, endpoint=True)
                        pen2 = pg.mkPen(color=lens_yaml["color"], style=QtCore.Qt.SolidLine)
                        im_i = self.plot.plot(pen=pen2, name=lens_yaml["name"])
                        im_i.setData(x=xnew, y=f2(xnew))

                    except Exception as e:
                        LOGGER.error(str(e))
                    

                #ax.set_xlabel('Zoom motor (mm)')

                # scater data
                self.scatter_focus_zoom = self.plot.plot(pen=None, symbol='x', symbolPen="gray", symbolSize = 15)
                self.scatter_compensate = self.plot.plot(pen=None, symbol='x', symbolPen="blue", symbolSize = 15)
                #x_data = [0]
                #y_data = [0]
                #self.scatter_focus_zoom.setData([0], y_data)
                #self.scatter_compensate.setData(x_data, y_data)

                #self.plot.addLegend()
                 
                #plt = pg.plot()
 
                
    def add_log_response(self, text):
        self.label_response.setText(text.strip())

    def check_motor_pos(self):
        now = time.time()
        if str(self.label_motion_status.text()) == "Run":
            if(now - self.last_updated_pos) > 0.3:
                print("update pos")
                self.hw.send_buffered('?')           
            #self.last_updated_pos = now


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
            s.limit_available = False

            if p[0:2] == "Pn":
                s.limit_available = True
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
            self.scatter_focus_zoom.setData([s.pos_x], [s.pos_z])
            self.scatter_compensate.setData([s.pos_x], [s.pos_y])

        self.label_x_pos.setText(str(round(s.pos_x,3)))
        self.label_y_pos.setText(str(round(s.pos_y,3)))
        self.label_z_pos.setText(str(round(s.pos_z,3)))
        self.label_a_pos.setText(str(round(s.pos_a,3)))

        self.btn_x_seek.setEnabled(True)
        self.btn_y_seek.setEnabled(True)
        self.btn_z_seek.setEnabled(True)
        self.btn_a_seek.setEnabled(True)

        if s.limit_available:
            if s.limit_x:
                self.label_x_pi.setText('LOW')
                #self.label_x_pi.setStyleSheet("color: " + COLOR_RED)
                #self.btn_x_seek.setEnabled(False)
            else:
                self.label_x_pi.setText('HIGH')
                #self.label_x_pi.setStyleSheet("")
                #self.btn_x_seek.setEnabled(True)

            if s.limit_y:
                self.label_y_pi.setText('LOW')
                #self.label_y_pi.setStyleSheet("color: " + COLOR_RED)
                #self.btn_y_seek.setEnabled(False)
            else:
                self.label_y_pi.setText('HIGH')
                #self.label_y_pi.setStyleSheet("")
                #self.btn_y_seek.setEnabled(True)

            if s.limit_z:
                self.label_z_pi.setText('LOW')
                #self.label_z_pi.setStyleSheet("color: " + COLOR_RED)
                #self.btn_z_seek.setEnabled(False)
            else:
                self.label_z_pi.setText('HIGH')
                #self.label_z_pi.setStyleSheet("")
                #self.btn_z_seek.setEnabled(True)

            if s.limit_a:
                self.label_a_pi.setText('LOW')
                #self.label_a_pi.setStyleSheet("color: " + COLOR_RED)
                #self.btn_a_seek.setEnabled(False)
            else:
                self.label_a_pi.setText('HIGH')
                #self.label_a_pi.setStyleSheet("")
                #self.btn_a_seek.setEnabled(True)


        self.label_buffer_count.setText(str(s.block_buffer_avail))
        self.label_motion_status.setText(str(s.status))
        self.s_global = s

        self.last_updated_pos = time.time()

        '''
        if str(s.status) == "Run":
            now = time.time()
            print(now - self.last_updated_pos)
            if (now - self.last_updated_pos) > 0.5:
                #time.sleep(0.5)
                # TODO: add watchdog
                print(s.status)
                self.hw.send_buffered('?')
           
            self.last_updated_pos = now
        '''

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
