import sys
import time
import yaml
from tqdm import tqdm
import sce2_lens
import local_coms
from scipy.interpolate import interp1d
import numpy as np


z = local_coms.LOCAL_COMS_MASTER()

print("Loading data file... ", end = '')
keypoints = {}
lens_name = None
with open("results\\keypoints.yaml") as f:
    keypoints = yaml.load(f, Loader=yaml.FullLoader)
    f.close()
print("Ok")


print("Loading config file... ", end = '')
config = {}
cfg_file = "../03_lens_tester_gui/config.yaml"
with open(cfg_file) as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    f.close()
print("Ok")


reply, status, t = z.msg_text("show")

# detect lens
print("Using port:", config["port"])
lens = sce2_lens.SCE2(config["port"])
print("Detecting lens:", lens.lens_name)



interpolate_count = config["lens"][lens.lens_name]["motor"]["interpolate_count"]
curve_focus_inf = config["lens"][lens.lens_name]["motor"]["curves"]["focus_inf"]
curve_zoom_correction = config["lens"][lens.lens_name]["motor"]["curves"]["zoom_correction"]

f1 = interp1d(curve_focus_inf["x"], curve_focus_inf["y"], kind='cubic')
x1new = np.linspace(min(curve_focus_inf["x"]), max(curve_focus_inf["x"]), num=interpolate_count, endpoint=True)

f2 = interp1d(curve_zoom_correction["x"], curve_zoom_correction["y"], kind='cubic')
x2new = np.linspace(min(curve_zoom_correction["x"]), max(curve_zoom_correction["x"]), num=interpolate_count, endpoint=True)

i_min = min(curve_zoom_correction["x"])
i_max = max(curve_zoom_correction["x"])

normalized100 = interp1d((0, 100), (i_max, i_min))

lens.move_buffered("test")


zoom_slider_memory = 0
print()
while 1:
    pos_to = input("Enter zoom position 0..100 >")
    pos_to = float(pos_to)
    if pos_to<0 or pos_to>100:
        print("Wrong zoom range")
    else:           
        diff = np.abs(zoom_slider_memory-pos_to)
        resolution = 0.1

        motion_pan = []
        if lens.lens_name == "L084":
            for i in np.linspace(normalized100(zoom_slider_memory), normalized100(pos_to), int(diff/resolution), endpoint=True):
                cmd = "G90 G1"
                cmd += " X"+str(i)
                cmd += " Y"+str(f1(i))
                cmd += " Z"+str(f2(i))
                cmd += " F2000"
                motion_pan.append(cmd)

        if lens.lens_name == "L117":
            for i in np.linspace(normalized100(zoom_slider_memory), normalized100(pos_to), int(diff/resolution), endpoint=True):
                cmd = "G90 G1"
                cmd += " X"+str(i)
                cmd += " Y"+str(f2(i))
                cmd += " Z"+str(f1(i))
                cmd += " F1500"
                motion_pan.append(cmd)

        if lens.lens_name == "L086":
            for i in np.linspace(normalized100(zoom_slider_memory), normalized100(pos_to), int(diff/resolution), endpoint=True):
                cmd = "G90 G1"
                cmd += " X"+str(i)
                cmd += " Y"+str(f2(i))
                cmd += " Z"+str(f1(i))
                cmd += " F2000"
                motion_pan.append(cmd)

        zoom_slider_memory = pos_to # backup last value


        for i in tqdm(motion_pan, leave=False):
            lens.send_command(i, echo=False)
            #lens.wait_for_idle(echo=False)

                       