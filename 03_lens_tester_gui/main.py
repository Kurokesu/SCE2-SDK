import logs
import version
import json
import ezdxf
import sys
import os
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets, uic, QtSvg
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import numpy as np
import queue
import utils
import motion
import gui
import preset_widget
import pos_widget
from scipy.interpolate import interp1d
import keypoints
import time

import logging
LOGGER = logging.getLogger(__name__)
LOGGER.info('start')

SETTINGS_FILE = 'config.json'
LENSES_DIR = 'lenses'


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


def split_preset_values(str_values, value_count=4):
    # TODO: change data format
    #val_cnt = 6
    values = [0]*value_count

    v = str_values.split(" ")
    for i in range(value_count):
        try:
            values[i] = float(v[i])
        except:
            values[i] = None

    return values


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
        self.lens_config = None
        self.zoom_slider_memory = 0
        self.focus_slider_memory = 50
        self.dbg_keypoints = None
        self.last_updated_pos = 0
        self.last_direction = {"X": 0, "Y": 0, "Z": 0, "A": 0}  # Track last movement direction for each axis

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
        self.group_focal_length.setEnabled(False)
        #self.group_x_axis.setEnabled(False)
        #self.group_y_axis.setEnabled(False)
        #self.group_z_axis.setEnabled(False)
        #self.group_a_axis.setEnabled(False)
        self.presetGroup.setEnabled(False)
        self.focus_slider1.setEnabled(True) # should be enabled in edittor, but there is a bug. workaround
        #self.group_p2.setEnabled(False)
        #self.group_p3.setEnabled(False)
        #self.group_p4.setEnabled(False)
        #self.group_p5.setEnabled(False)


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

        self.btn_x_seek.clicked.connect(self.btn_x_seek_clicked)
        self.btn_y_seek.clicked.connect(self.btn_y_seek_clicked)
        self.btn_z_seek.clicked.connect(self.btn_z_seek_clicked)
        self.btn_a_seek.clicked.connect(self.btn_a_seek_clicked)
        self.btn_all_seek.clicked.connect(self.btn_all_seek_clicked)
        
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

        self.presetGroup.hide()
        self.group_x_axis.hide()
        #layout.removeWidget(self.widget_name)
        #self.widget_name.deleteLater()
        #self.widget_name = None


        #self.presets = preset_widget.Preset(self.presetGroup, 5)
        self.presets = preset_widget.Preset(self.horizontalLayout, 5)
        self.presets.clicked_set.connect(self.preset_set)
        self.presets.clicked_go.connect(self.preset_go)
        
        self.pos = pos_widget.Pos(self.verticalLayout, 4)
        self.pos.moved.connect(self.pos_move)


        self.plot = self.win.addPlot()
        self.plot.showGrid(True, True, 0.2)
        self.plot.setMenuEnabled(enableMenu=False)
        self.plot.hideButtons()
        self.plot.setMouseEnabled(x=False, y=False)
        self.plot.addLegend()
        

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

    def compensate_backlash(self, axis, target_pos, current_pos):
        """Compensate for backlash in axis movement.
        
        Args:
            axis (str): Axis name (X, Y, Z, A)
            target_pos (float): Target position
            current_pos (float): Current position
            
        Returns:
            float: Compensated target position
        """
        if not self.lens_config or "backlash" not in self.lens_config:
            return target_pos
            
        backlash = self.lens_config.get("backlash", {}).get(axis.lower(), 0)
        if backlash == 0:
            return target_pos
            
        # Determine movement direction
        direction = 1 if target_pos > current_pos else -1
        
        # If direction changed, apply backlash compensation
        if self.last_direction[axis] != 0 and self.last_direction[axis] != direction:
            if direction > 0:
                target_pos += backlash
            else:
                target_pos -= backlash
                
        self.last_direction[axis] = direction
        return target_pos

    def send_gcode_with_backlash(self, cmd):
        """Send G-code command with backlash compensation.
        
        Args:
            cmd (str): G-code command to send
        """
        if not self.lens_config or "backlash" not in self.lens_config:
            self.hw.send(cmd+"\n")
            return
            
        # Parse the command to get axis movements
        parts = cmd.split()
        if len(parts) < 2:
            self.hw.send(cmd+"\n")
            return
            
        # Get current positions
        current_x = self.status.pos_x
        current_y = self.status.pos_y
        current_z = self.status.pos_z
        current_a = self.status.pos_a
        
        # Parse target positions
        target_x = current_x
        target_y = current_y
        target_z = current_z
        target_a = current_a
        
        for part in parts[1:]:
            if part.startswith('X'):
                target_x = float(part[1:])
            elif part.startswith('Y'):
                target_y = float(part[1:])
            elif part.startswith('Z'):
                target_z = float(part[1:])
            elif part.startswith('A'):
                target_a = float(part[1:])
                
        # Apply backlash compensation
        target_x = self.compensate_backlash("X", target_x, current_x)
        target_y = self.compensate_backlash("Y", target_y, current_y)
        target_z = self.compensate_backlash("Z", target_z, current_z)
        target_a = self.compensate_backlash("A", target_a, current_a)
        
        # Reconstruct command with compensated positions
        new_cmd = parts[0]  # G-code command (e.g., G90 G1)
        if target_x != current_x:
            new_cmd += f" X{target_x:.3f}"
        if target_y != current_y:
            new_cmd += f" Y{target_y:.3f}"
        if target_z != current_z:
            new_cmd += f" Z{target_z:.3f}"
        if target_a != current_a:
            new_cmd += f" A{target_a:.3f}"
            
        # Add any remaining parts (like F for feedrate)
        for part in parts[1:]:
            if not any(part.startswith(axis) for axis in ['X', 'Y', 'Z', 'A']):
                new_cmd += f" {part}"
                
        self.hw.send(new_cmd+"\n")

    def pos_move(self, ch, dir):
        cmd = "G91 "
        cmd += self.pos.axis_names[ch]
        if dir == 1:
            cmd += "-"
        elif dir == 0:
            pass
        else:
            print("Direction should be 0 or 1!")
        cmd += str(self.combo_step.currentText())
        cmd += " F"
        cmd += str(self.combo_speed.currentText())
        self.send_gcode_with_backlash(cmd)


    def preset_go(self, nr, values):
        #print("Widget GO", nr, values)
        cmd =  "G90 G1"
        if self.lens_config["motor"]["function"]["axis_x"]:
            cmd += " X"
            cmd += str(values[0])
        if self.lens_config["motor"]["function"]["axis_y"]:
            cmd += " Y"
            cmd += str(values[1])
        if self.lens_config["motor"]["function"]["axis_z"]:
            cmd += " Z"
            cmd += str(values[2])
        if self.lens_config["motor"]["function"]["axis_a"]:
            cmd += " A"
            cmd += str(values[3])
        cmd += " F"
        cmd += self.combo_speed.currentText()
        self.send_gcode_with_backlash(cmd)


    def preset_set(self, nr):
        #print("set", nr)
        self.presets.set_values(nr, ch0=self.status.pos_x, ch1=self.status.pos_y, ch2=self.status.pos_z, ch3=self.status.pos_a)
        
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
            self.send_gcode_with_backlash(cmd)

    
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
        interpolate_count = self.lens_config["motor"]["interpolate_count"]
        curve_focus_inf = self.lens_config["motor"]["curves"]["focus_inf"]
        curve_focus_near = self.lens_config["motor"]["curves"]["focus_near"]

        f1 = interp1d(curve_focus_inf["x"], curve_focus_inf["y"], kind='cubic')
        f3 = interp1d(curve_focus_near["x"], curve_focus_near["y"], kind='cubic')

        #x_pos = float(self.label_x_pos.text())
        x_pos = self.pos.pos_list[0].value

        new_focus_pos = f3(x_pos) * (1 - value/100) + f1(x_pos) * (value/100)
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
        available_inf = False
        available_near = False
        available_correction = False

        interpolate_count = self.lens_config["motor"]["interpolate_count"]
        
        curve_focus_inf = self.lens_config["motor"]["curves"]["focus_inf"]
        
        # Check if zoom_correction curve exists
        if "zoom_correction" in self.lens_config["motor"]["curves"]:
            curve_zoom_correction = self.lens_config["motor"]["curves"]["zoom_correction"]
            f2 = interp1d(curve_zoom_correction["x"], curve_zoom_correction["y"], kind='cubic')
            x2new = np.linspace(min(curve_zoom_correction["x"]), max(curve_zoom_correction["x"]), num=interpolate_count, endpoint=True)
            i_min = min(curve_zoom_correction["x"])
            i_max = max(curve_zoom_correction["x"])
        else:
            # If no zoom correction curve, use focus_inf curve for zoom
            curve_zoom_correction = curve_focus_inf
            f2 = interp1d(curve_focus_inf["x"], curve_focus_inf["y"], kind='cubic')
            x2new = np.linspace(min(curve_focus_inf["x"]), max(curve_focus_inf["x"]), num=interpolate_count, endpoint=True)
            i_min = min(curve_focus_inf["x"])
            i_max = max(curve_focus_inf["x"])

        f1 = interp1d(curve_focus_inf["x"], curve_focus_inf["y"], kind='cubic')
        x1new = np.linspace(min(curve_focus_inf["x"]), max(curve_focus_inf["x"]), num=interpolate_count, endpoint=True)

        normalized100 = interp1d((0, 100), (i_max, i_min))
        pos_from = self.zoom_slider_memory
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
                self.send_gcode_with_backlash(cmd)

        if self.lens_name == "L117":
            for i in np.linspace(normalized100(pos_from), normalized100(pos_to), int(diff/resolution), endpoint=True):
                cmd = "G90 G1"
                cmd += " X"+str(i)
                cmd += " Y"+str(f2(i))
                cmd += " Z"+str(f1(i))
                cmd += " F2000"
                self.send_gcode_with_backlash(cmd)

        if self.lens_name == "L086":
            for i in np.linspace(normalized100(pos_from), normalized100(pos_to), int(diff/resolution), endpoint=True):
                cmd = "G90 G1"
                cmd += " X"+str(i)
                cmd += " Y"+str(f2(i))
                cmd += " Z"+str(f1(i))
                cmd += " F2000"
                self.send_gcode_with_backlash(cmd)
                
        if self.lens_name == "L085":
            for i in np.linspace(normalized100(pos_from), normalized100(pos_to), int(diff/resolution), endpoint=True):
                cmd = "G90 G1"
                cmd += " X"+str(i)
                cmd += " Y"+str(f2(i))
                cmd += " F2000"
                self.send_gcode_with_backlash(cmd)

        if self.lens_name == "L085D":
            for i in np.linspace(normalized100(pos_from), normalized100(pos_to), int(diff/resolution), endpoint=True):
                cmd = "G90 G1"
                cmd += " X"+str(i)
                cmd += " Y"+str(f2(i))
                cmd += " F2000"
                self.send_gcode_with_backlash(cmd)

        if self.lens_name == "L120":
            for i in np.linspace(normalized100(pos_from), normalized100(pos_to), int(diff/resolution), endpoint=True):
                cmd = "G90 G1"
                cmd += " X"+str(i)
                cmd += " Y"+str(f2(i))
                cmd += " F2000"
                self.send_gcode_with_backlash(cmd)


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
            # TODO: check if HIGH, move only then
            cmd = "G91 G0 Z2 F1000"
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
            # TODO: check if HIGH, move only then
            cmd = "G91 G0 X-12 Y-6 F1000"
            self.hw.send(cmd+"\n")

            cmd = "$HZ"
            self.hw.send(cmd+"\n")
            cmd = "$HX"
            self.hw.send(cmd+"\n")
            cmd = "$HY"
            self.hw.send(cmd+"\n")

        if self.lens_name == "L085":
            cmd = "$HX"
            self.hw.send(cmd+"\n")
            cmd = "$HY"
            self.hw.send(cmd+"\n")

        if self.lens_name == "L085D":
            cmd = "M120 P1"             # Enable LED
            self.hw.send(cmd+"\n")
            
            cmd = "$HX"
            self.hw.send(cmd+"\n")
            cmd = "$HY"
            self.hw.send(cmd+"\n")
            
            cmd = "M120 P0"             # Disable LED
            self.hw.send(cmd+"\n")


        if self.lens_name == "L120":
            cmd = "$HX"
            self.hw.send(cmd+"\n")
            cmd = "$HY"
            self.hw.send(cmd+"\n")

        if self.lens_name == "L144":
            cmd = "$HX"
            self.hw.send(cmd+"\n")
            cmd = "$HY"


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


    def btn_f1_on_clicked(self):
        cmd = self.lens_config["filter1"]["state_on"]

        if type(cmd) == str:
            self.hw.send(cmd+"\n")

        if type(cmd) == list:
            for c in cmd:
                self.hw.send(c+"\n")

    def btn_f1_off_clicked(self):
        cmd = self.lens_config["filter1"]["state_off"]

        if type(cmd) == str:
            self.hw.send(cmd+"\n")

        if type(cmd) == list:
            for c in cmd:
                self.hw.send(c+"\n")

    def btn_f2_on_clicked(self):
        cmd = self.lens_config["filter2"]["state_on"]

        if type(cmd) == str:
            self.hw.send(cmd+"\n")

        if type(cmd) == list:
            for c in cmd:
                self.hw.send(c+"\n")

    def btn_f2_off_clicked(self):
        cmd = self.lens_config["filter2"]["state_off"]

        if type(cmd) == str:
            self.hw.send(cmd+"\n")

        if type(cmd) == list:
            for c in cmd:
                self.hw.send(c+"\n")

    def btn_pi_led_on_clicked(self):
        cmd = self.lens_config["limit_sensor"]["led_on"]
        self.hw.send(cmd+"\n")

    def btn_pi_led_off_clicked(self):
        cmd = self.lens_config["limit_sensor"]["led_off"]
        self.hw.send(cmd+"\n")

    def btn_iris_on_clicked(self):
        cmd = self.lens_config["iris"]["open"]
        self.hw.send(cmd+"\n")
       
    def btn_iris_off_clicked(self):
        cmd = self.lens_config["iris"]["close"]
        self.hw.send(cmd+"\n")

    def btn_mdi_send_clicked(self):
        self.hw.send(self.line_mdi.text()+"\n")

    def btn_connect_clicked(self):
        self.config["port"] = self.combo_ports.currentText()
        self.hw.connect(self.config["port"], self.config["com_baud"], self.config["com_timeout"])

    def btn_disconnect_clicked(self):
        self.hw.disconnect()
        self.plot.clear()
        self.presets.setEnabled(False)
        self.pos.setEnabled(False)

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
        if self.hw_connected and self.lens_config is not None:
            self.group_step_size.setEnabled(True)
            self.group_lens.setEnabled(True)
            self.group_speed.setEnabled(True)
            self.group_mdi.setEnabled(True)
            self.group_filter1.setEnabled(True)
            self.group_filter2.setEnabled(True)
            self.group_pi.setEnabled(True)
            self.group_iris.setEnabled(True)
            self.group_homing.setEnabled(True)
            self.group_keypoints_2.setEnabled(True)
            self.group_guided_zoom1.setEnabled(True)
            self.group_guided_focus1.setEnabled(True)
            self.group_focal_length.setEnabled(True)
            self.presetGroup.setEnabled(True)
        else:
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
            self.group_focal_length.setEnabled(False)
            self.presetGroup.setEnabled(False)


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

        try:
            # Parse version string like [VER:1.1g-SCE2.20221001:L084,JWF-00000]
            # First split by ":" then by ","
            version_parts = text.strip().replace('[', '').replace(']', '').split(':')
            
            if len(version_parts) >= 3:
                id_strings = version_parts[2].split(',')
                
                for i in id_strings:
                    # Check for lens ID (Lxxx) and split by comma
                    if i.startswith('L'):
                        lens_id = i.split(',')[0]  # Get the part before comma
                        lens_file = os.path.join(LENSES_DIR, f'{lens_id}.json')
                        if os.path.exists(lens_file):
                            self.lens_name = lens_id
                            self.label_lens_name.setText(self.lens_name)
                            self.config["last_lens"] = self.lens_name
                            #print(self.lens_name)

                            # Load lens configuration from JSON file
                            with open(lens_file, 'r') as f:
                                self.lens_config = json.load(f)
                            
                            # Initialize lens settings
                            cmd = self.lens_config["limit_sensor"]["led_on"]
                            self.hw.send(cmd+"\n")
                            cmd = self.lens_config["iris"]["open"]
                            self.hw.send(cmd+"\n")

                            # Setup step size
                            self.group_step_size.setEnabled(True)
                            self.combo_step.clear()                
                            default_step = None
                            step_list = self.lens_config["motor"]["step_list"].split(" ")
                            for i in step_list:
                                if "*" in i:
                                    default_step = i.replace("*", "")
                                self.combo_step.addItem(i.replace("*", ""))
                            if default_step:
                                self.combo_step.setCurrentText(default_step)

                            # Setup speed
                            self.group_speed.setEnabled(True)
                            self.group_lens.setEnabled(True)
                            self.combo_speed.clear()                
                            default_speed = None
                            speed_list = self.lens_config["motor"]["speed_list"].split(" ")
                            for i in speed_list:
                                if "*" in i:
                                    default_speed = i.replace("*", "")
                                self.combo_speed.addItem(i.replace("*", ""))
                            if default_speed:
                                self.combo_speed.setCurrentText(default_speed)

                            # Enable groups
                            self.group_mdi.setEnabled(True)
                            if "filter1" in self.lens_config:
                                self.group_filter1.setEnabled(True)
                                self.group_filter1.setTitle("Filter: "+self.lens_config["filter1"]["name"])
                            if "filter2" in self.lens_config:
                                self.group_filter2.setEnabled(True)
                                self.group_filter2.setTitle("Filter: "+self.lens_config["filter2"]["name"])
                            self.group_pi.setEnabled(True)
                            if "iris" in self.lens_config:
                                self.group_iris.setEnabled(True)
                            self.presetGroup.setEnabled(True)                
                            self.group_homing.setEnabled(True)
                            self.group_guided_zoom1.setEnabled(True)
                            self.group_guided_focus1.setEnabled(True)
                            self.group_keypoints_2.setEnabled(True)
                            self.group_focal_length.setEnabled(True)

                            # Setup presets
                            preset = split_preset_values(self.lens_config["preset"]["p1"], value_count=4)
                            self.presets.set_values(0, ch0=preset[0], ch1=preset[1], ch2=preset[2], ch3=preset[3])
                            preset = split_preset_values(self.lens_config["preset"]["p2"], value_count=4)
                            self.presets.set_values(1, ch0=preset[0], ch1=preset[1], ch2=preset[2], ch3=preset[3])
                            preset = split_preset_values(self.lens_config["preset"]["p3"], value_count=4)
                            self.presets.set_values(2, ch0=preset[0], ch1=preset[1], ch2=preset[2], ch3=preset[3])
                            preset = split_preset_values(self.lens_config["preset"]["p4"], value_count=4)
                            self.presets.set_values(3, ch0=preset[0], ch1=preset[1], ch2=preset[2], ch3=preset[3])
                            preset = split_preset_values(self.lens_config["preset"]["p5"], value_count=4)
                            self.presets.set_values(4, ch0=preset[0], ch1=preset[1], ch2=preset[2], ch3=preset[3])

                            self.presets.setEnabled(True)
                            self.pos.setEnabled(True)

                            # Setup axis names
                            if self.lens_config["motor"]["function"]["axis_x"]:
                                self.pos.set_name(0, "X axis / " + self.lens_config["motor"]["function"]["axis_x"])
                            if self.lens_config["motor"]["function"]["axis_y"]:
                                self.pos.set_name(1, "Y axis / " + self.lens_config["motor"]["function"]["axis_y"])
                            if self.lens_config["motor"]["function"]["axis_z"]:
                                self.pos.set_name(2, "Z axis / " + self.lens_config["motor"]["function"]["axis_z"])
                            if self.lens_config["motor"]["function"]["axis_a"]:
                                self.pos.set_name(3, "A axis / " + self.lens_config["motor"]["function"]["axis_a"])

                            # Setup debug keypoints
                            self.dbg_keypoints = keypoints.Keypoints(self.lens_config["debug_keypoints"])
                            items = []
                            for i in range(len(self.dbg_keypoints.points)):
                                items.append(str(i))
                            self.comboBox_keypoints.addItems(items)

                            # Setup plot
                            self.plot.clear()               
                            interpolate_count = 100 # TBD: move to config
                            for curve in self.lens_config["motor"]["curves"]:
                                try:
                                    if self.lens_config["motor"]["curves"][curve]["show"]:
                                        lens_curve = self.lens_config["motor"]["curves"][curve]
                                        pull_off = lens_curve["pulloff"]
                                        data_x = lens_curve["x"]
                                        data_y = lens_curve["y"]
                                        data_x = [i-pull_off for i in data_x]
                                        data_y = [i-pull_off for i in data_y]

                                        # Interpolated curve
                                        f2 = interp1d(data_x, data_y, kind='cubic')
                                        xnew = np.linspace(min(data_x), max(data_x), num=interpolate_count, endpoint=True)
                                        pen2 = pg.mkPen(color=lens_curve["color"], style=QtCore.Qt.SolidLine)
                                        im_i = self.plot.plot(pen=pen2, name=lens_curve["name"])
                                        im_i.setData(x=xnew, y=f2(xnew))
                                except Exception as e:
                                    LOGGER.error(str(e))

                            # Setup scatter plots
                            self.scatter_focus_zoom = self.plot.plot(pen=None, symbol='x', symbolPen="gray", symbolSize=15)
                            self.scatter_compensate = self.plot.plot(pen=None, symbol='x', symbolPen="blue", symbolSize=15)
                            break  # Exit the loop once we find a valid lens
                        else:
                            LOGGER.warning(f"Lens configuration file not found: {lens_file}")
                            self.lens_config = None
                            self.lens_name = None
        except Exception as e:
            LOGGER.error(f"Error loading lens configuration: {str(e)}")
            self.lens_config = None
            self.lens_name = None

    def add_log_response(self, text):
        self.label_response.setText(text.strip())

    def check_motor_pos(self):
        now = time.time()
        if str(self.label_motion_status.text()) == "Run":
            if(now - self.last_updated_pos) > 0.3:
                #print("update pos")
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

        self.pos.set_value(0, s.pos_x, s.limit_x)
        #try:
        # TODO: handle more delicate
        '''
        if "focal_range" in self.config["lens"][self.lens_name]["motor"]["curves"]:
            # do not calculate full interpolation here, move to init section
            interpolate_count = self.config["lens"][self.lens_name]["motor"]["interpolate_count"]
            curve_focal_range = self.config["lens"][self.lens_name]["motor"]["curves"]["focal_range"]
            f1 = interp1d(curve_focal_range["x"], curve_focal_range["y"], kind='cubic')
            focal_len = round(float(f1(s.pos_x)), 2)
            self.label_focal_length.setText(str(focal_len))
        '''
        #except Exception as e:
        #    print("Err", e)

        self.pos.set_value(1, s.pos_y, s.limit_y)
        self.pos.set_value(2, s.pos_z, s.limit_z)
        self.pos.set_value(3, s.pos_a, s.limit_a)

        self.btn_x_seek.setEnabled(True)
        self.btn_y_seek.setEnabled(True)
        self.btn_z_seek.setEnabled(True)
        self.btn_a_seek.setEnabled(True)

        self.label_buffer_count.setText(str(s.block_buffer_avail))
        self.label_motion_status.setText(str(s.status))
        self.s_global = s

        self.last_updated_pos = time.time()


    def closeEvent(self, event):
        global config
        global running

        if self.s_status.text() == "Connected" and self.lens_config is not None:
            # Save preset values to the lens configuration
            p = self.presets.get_values(0)
            p = str(p[0])+" "+str(p[1])+" "+str(p[2])+" "+str(p[3])
            self.lens_config["preset"]["p1"] = p

            p = self.presets.get_values(1)
            p = str(p[0])+" "+str(p[1])+" "+str(p[2])+" "+str(p[3])
            self.lens_config["preset"]["p2"] = p

            p = self.presets.get_values(2)
            p = str(p[0])+" "+str(p[1])+" "+str(p[2])+" "+str(p[3])
            self.lens_config["preset"]["p3"] = p

            p = self.presets.get_values(3)
            p = str(p[0])+" "+str(p[1])+" "+str(p[2])+" "+str(p[3])
            self.lens_config["preset"]["p4"] = p

            p = self.presets.get_values(4)
            p = str(p[0])+" "+str(p[1])+" "+str(p[2])+" "+str(p[3])
            self.lens_config["preset"]["p5"] = p

            # Save the updated lens configuration
            lens_file = os.path.join(LENSES_DIR, f'{self.lens_name}.json')
            with open(lens_file, 'w') as f:
                json.dump(self.lens_config, f, indent=2)

        utils.exit_routine(SETTINGS_FILE, self.config)
        running = False
        app.quit()


app = QtWidgets.QApplication(sys.argv)
app.setStyle('Fusion')
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()
