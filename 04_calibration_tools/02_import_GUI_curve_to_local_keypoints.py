import sys
import time
import yaml
from tqdm import tqdm


keypoints = {}
keypoints["kp"] = {}

config = {}
cfg_file = "../03_lens_tester_gui/config.yaml"
with open(cfg_file) as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    f.close()


lens = config["last_lens"]
focus_curve = "focus_inf"
correction_curve = "zoom_correction"

print("Importing", lens, "lens keypoints")

# TODO: let's assume they have the same x points
curve1 = config["lens"][lens]["motor"]["curves"][focus_curve]
curve2 = config["lens"][lens]["motor"]["curves"][correction_curve]


for i in range(len(curve1["x"])):
    #print(i)
    keypoints["kp"][i] = {}

    # TODO: make sure it's safe output with no references &
    keypoints["kp"][i]["x"] = curve1["x"][i]
    keypoints["kp"][i]["y"] = curve2["y"][i] # !! z/y
    keypoints["kp"][i]["z"] = curve1["y"][i] # !! z/y
    
    span = 0.5

    keypoints["kp"][i]["maxy"] = keypoints["kp"][i]["y"] + span
    keypoints["kp"][i]["miny"] = keypoints["kp"][i]["y"] - span
    
    keypoints["kp"][i]["maxz"] = keypoints["kp"][i]["z"] + span
    keypoints["kp"][i]["minz"] = keypoints["kp"][i]["z"] - span
   
    
kpt_file = "results\\keypoints.yaml"
with open(kpt_file, 'w') as f:
    yaml.dump(keypoints, f)

print("Done")
