import sys
import json
import os
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.interpolate import interp1d

LENSES_DIR = 'lenses'

class CurveEditor(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lens Curve Editor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Create file selection area
        file_layout = QtWidgets.QHBoxLayout()
        self.file_combo = QtWidgets.QComboBox()
        self.file_combo.setMinimumWidth(300)
        file_layout.addWidget(QLabel("Select Lens File:"))
        file_layout.addWidget(self.file_combo)
        file_layout.addStretch()
        layout.addLayout(file_layout)
        
        # Create curve selection area
        curve_layout = QtWidgets.QHBoxLayout()
        self.curve_combo = QtWidgets.QComboBox()
        self.curve_combo.setMinimumWidth(300)
        curve_layout.addWidget(QLabel("Select Curve:"))
        curve_layout.addWidget(self.curve_combo)
        
        # Add Fine tune curve button
        self.btn_fine_tune = QPushButton("Fine tune curve")
        self.btn_fine_tune.setEnabled(False)
        curve_layout.addWidget(self.btn_fine_tune)
        
        # Add Overwrite curve button
        self.btn_overwrite = QPushButton("Overwrite curve")
        self.btn_overwrite.setEnabled(False)
        curve_layout.addWidget(self.btn_overwrite)
        
        curve_layout.addStretch()
        layout.addLayout(curve_layout)
        
        # Create plot area
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(True, True, 0.2)
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.hideButtons()
        self.plot_widget.addLegend()
        layout.addWidget(self.plot_widget)
        
        # Connect signals
        self.file_combo.currentTextChanged.connect(self.load_lens_file)
        self.curve_combo.currentTextChanged.connect(self.update_plot)
        self.curve_combo.currentTextChanged.connect(self.update_fine_tune_button_state)
        self.btn_fine_tune.clicked.connect(self.fine_tune_curve)
        self.btn_overwrite.clicked.connect(self.overwrite_curve)
        
        # Initialize variables
        self.current_lens_data = None
        self.adjusted_curve = None  # Store the adjusted curve data
        
        # Populate file list and trigger first file selection
        self.refresh_files()
        if self.file_combo.count() > 0:
            self.load_lens_file(self.file_combo.currentText())
            self.update_plot()  # Show all curves initially
        
    def refresh_files(self):
        self.file_combo.clear()
        if os.path.exists(LENSES_DIR):
            for file in os.listdir(LENSES_DIR):
                if file.endswith('.json'):
                    self.file_combo.addItem(file)
    
    def load_lens_file(self, filename):
        if not filename:
            return
            
        filepath = os.path.join(LENSES_DIR, filename)
        try:
            with open(filepath, 'r') as f:
                self.current_lens_data = json.load(f)
                
            # Update curve combo box
            self.curve_combo.clear()
            if 'motor' in self.current_lens_data and 'curves' in self.current_lens_data['motor']:
                for curve_name in self.current_lens_data['motor']['curves'].keys():
                    self.curve_combo.addItem(curve_name)
                # Clear the plot when loading a new file
                self.plot_widget.clear()
                self.update_plot()  # Show all curves after loading new file
                
            # Update fine tune button state
            self.update_fine_tune_button_state()
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")
    
    def update_plot(self):
        if not self.current_lens_data:
            return
            
        self.plot_widget.clear()
        selected_curve = self.curve_combo.currentText()
        
        # Plot all curves
        for curve_name, curve_data in self.current_lens_data['motor']['curves'].items():
            x = curve_data['x']
            y = curve_data['y']
            color = curve_data.get('color', '#000000')
            
            # Make selected curve thicker
            width = 3 if curve_name == selected_curve else 1
            pen = pg.mkPen(color=color, width=width)
            self.plot_widget.plot(x, y, name=curve_name, pen=pen)
        
        # Plot preset points if they exist
        if 'debug_keypoints' in self.current_lens_data:
            keypoints = self.current_lens_data['debug_keypoints']
            x_points = []
            y_points = []
            for point in keypoints:
                if len(point) >= 2:
                    x_points.append(point[0])
                    y_points.append(point[1])
            
            if x_points and y_points:
                # Get pixel scale for 30px diagonal lines
                view_box = self.plot_widget.getViewBox()
                screen_coords = view_box.viewPixelSize()
                px_size_x = screen_coords[0]  # size of one pixel in x-axis units
                px_size_y = screen_coords[1]  # size of one pixel in y-axis units
                
                # Calculate 15px offset (half of 30px) in data coordinates
                offset_x = px_size_x * 8
                offset_y = px_size_y * 8
                
                # Plot each point as an X with diagonal lines
                for x, y in zip(x_points, y_points):
                    # Draw diagonal line from top-left to bottom-right
                    self.plot_widget.plot(
                        [x - offset_x, x + offset_x],
                        [y - offset_y, y + offset_y],
                        pen=pg.mkPen('r', width=1)
                    )
                    # Draw diagonal line from top-right to bottom-left
                    self.plot_widget.plot(
                        [x - offset_x, x + offset_x],
                        [y + offset_y, y - offset_y],
                        pen=pg.mkPen('r', width=1)
                    )
        
        # Set plot limits based on all curves and points
        all_x = []
        all_y = []
        for curve_data in self.current_lens_data['motor']['curves'].values():
            all_x.extend(curve_data['x'])
            all_y.extend(curve_data['y'])
            
        # Include preset points in range calculation if they exist
        if 'debug_keypoints' in self.current_lens_data:
            for point in self.current_lens_data['debug_keypoints']:
                if len(point) >= 2:
                    all_x.append(point[0])
                    all_y.append(point[1])
        
        if all_x and all_y:
            self.plot_widget.setXRange(min(all_x), max(all_x))
            self.plot_widget.setYRange(min(all_y), max(all_y))

    def update_fine_tune_button_state(self):
        can_fine_tune = (
            self.current_lens_data is not None and
            'debug_keypoints' in self.current_lens_data and
            len(self.current_lens_data.get('debug_keypoints', [])) > 0 and
            bool(self.curve_combo.currentText())
        )
        self.btn_fine_tune.setEnabled(can_fine_tune)
        self.btn_overwrite.setEnabled(False)  # Reset overwrite button state
        self.adjusted_curve = None  # Clear any stored adjusted curve

    def fine_tune_curve(self):
        if not self.current_lens_data or not self.curve_combo.currentText():
            return
            
        selected_curve = self.curve_combo.currentText()
        curve_data = self.current_lens_data['motor']['curves'][selected_curve]
        keypoints = self.current_lens_data['debug_keypoints']
        
        # Extract x, y coordinates from curve and keypoints
        curve_x = np.array(curve_data['x'])
        curve_y = np.array(curve_data['y'])
        keypoint_x = np.array([p[0] for p in keypoints])
        keypoint_y = np.array([p[1] for p in keypoints])
        
        # Ensure curve is properly ordered (ascending x)
        if curve_x[0] > curve_x[-1]:
            sort_idx = np.argsort(curve_x)
            curve_x = curve_x[sort_idx]
            curve_y = curve_y[sort_idx]
        
        # Sort keypoints by x coordinate and remove duplicates
        unique_indices = np.unique(keypoint_x, return_index=True)[1]
        keypoint_x = keypoint_x[unique_indices]
        keypoint_y = keypoint_y[unique_indices]
        
        sort_idx = np.argsort(keypoint_x)
        keypoint_x = keypoint_x[sort_idx]
        keypoint_y = keypoint_y[sort_idx]
        
        # Ensure keypoints are within curve x range
        x_min = min(curve_x[0], curve_x[-1])
        x_max = max(curve_x[0], curve_x[-1])
        margin = 0.001
        mask = (keypoint_x >= x_min - margin) & (keypoint_x <= x_max + margin)
        keypoint_x = keypoint_x[mask]
        keypoint_y = keypoint_y[mask]
        
        if len(keypoint_x) < 2:
            QtWidgets.QMessageBox.warning(self, "Warning", 
                f"Not enough valid keypoints for adjustment. Found {len(keypoint_x)}, need at least 2.")
            return
            
        try:
            # Create interpolator for original curve
            original_interp = interp1d(curve_x, curve_y, kind='linear', fill_value='extrapolate')
            
            # Calculate y values and slopes on original curve at keypoint x positions
            dx = 0.01  # Small delta for numerical derivative
            original_y_at_keypoints = original_interp(keypoint_x)
            original_slopes = []
            for x in keypoint_x:
                slope = (original_interp(x + dx) - original_interp(x - dx)) / (2 * dx)
                original_slopes.append(slope)
            original_slopes = np.array(original_slopes)
            
            # Calculate the difference between keypoints and original curve
            y_differences = keypoint_y - original_y_at_keypoints
            
            # Add virtual keypoints at endpoints
            virtual_dx = (x_max - x_min) * 0.01  # 1% of range for closer control
            extended_x = np.concatenate([
                [curve_x[0] - virtual_dx],
                keypoint_x,
                [curve_x[-1] + virtual_dx]
            ])
            
            # Calculate virtual y-differences at endpoints
            left_diff = y_differences[0]
            right_diff = y_differences[-1]
            extended_diffs = np.concatenate([[left_diff], y_differences, [right_diff]])
            
            # Calculate slopes for the differences at keypoints (maintain original curve slope)
            extended_slopes = np.concatenate([[0], np.zeros_like(original_slopes), [0]])
            
            # Create cubic spline interpolator for the differences with controlled derivatives
            diff_spline = CubicSpline(
                extended_x,
                extended_diffs,
                bc_type='natural',
                axis=0
            )
            
            # Calculate adjustment for each point on the curve
            adjustments = diff_spline(curve_x)
            
            # Apply adjustments to get final curve
            adjusted_y = curve_y + adjustments
            
            # Store the adjusted curve data
            self.adjusted_curve = {
                'x': curve_x.tolist(),
                'y': adjusted_y.tolist()
            }
            
            # Enable the overwrite button now that we have an adjusted curve
            self.btn_overwrite.setEnabled(True)
            
            # Plot the adjusted curve
            pen = pg.mkPen(color='#FF00FF', width=2)  # Magenta color for adjusted curve
            self.plot_widget.plot(curve_x, adjusted_y, name=f"{selected_curve}_adjusted", pen=pen)
            
            # Plot anchor points for visualization
            scatter = pg.ScatterPlotItem(
                x=keypoint_x,
                y=keypoint_y,
                symbol='o',
                size=8,
                pen=pg.mkPen('m', width=1),
                brush=pg.mkBrush('m')
            )
            self.plot_widget.addItem(scatter)
            
        except ValueError as e:
            QtWidgets.QMessageBox.critical(self, "Error", 
                f"Failed to create adjustment spline: {str(e)}\nKeypoints: {list(zip(keypoint_x, keypoint_y))}")
            return

    def overwrite_curve(self):
        if not self.adjusted_curve or not self.current_lens_data:
            return
            
        try:
            selected_curve = self.curve_combo.currentText()
            current_file = self.file_combo.currentText()
            filepath = os.path.join(LENSES_DIR, current_file)
            
            # Update the curve data in memory
            curve_data = self.current_lens_data['motor']['curves'][selected_curve]
            curve_data['x'] = self.adjusted_curve['x']
            curve_data['y'] = self.adjusted_curve['y']
            
            # Save the updated JSON file
            with open(filepath, 'w') as f:
                json.dump(self.current_lens_data, f, indent=2)
            
            # Reload the file to refresh everything
            self.load_lens_file(current_file)
            
            # Show success message
            QtWidgets.QMessageBox.information(self, "Success", "Curve has been updated successfully!")
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save changes: {str(e)}")
            return

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = CurveEditor()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
