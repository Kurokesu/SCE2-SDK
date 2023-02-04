Branch for testing focus auto calibration tools. Highly experimental.


* Set keypoints for near distance (~20 points should be plenty) in the GUI program, exit gui program then
* Run automated calibration enhancement procedure from 04_calibration_tools folder, don't forget to import data back to gui program 07_import_infinity_curve_to_config.py
* Refine each keypoint focus for infinity distance. Do not change x position. Just change focus!
* Run automated calirbration procedure, don't forget to run 08_import_closeup_curve_to_config.py 
* GUI program now has focus with the limits for each zoom point. Focus can be safely cahnged from 0% to 100%
* Guided focus has to be adjusted after each motion command manually. By default it uses infinity motion curve. Easy to update for automatic adjustment but will be easier to debug as is.
