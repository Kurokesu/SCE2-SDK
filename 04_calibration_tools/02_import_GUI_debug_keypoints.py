import sys
import time
import yaml
from tqdm import tqdm


keypoints = {}
keypoints["kp"] = {}

print("Loading data... ", end = '')
config = {}
cfg_file = "../03_lens_tester_gui/config.yaml"
with open(cfg_file) as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    f.close()
print("OK")

lens = config["last_lens"]
#keypoints["lens"] = lens
focus_curve = "focus_inf"
correction_curve = "zoom_correction"

print("Importing", lens, "lens keypoints")

# TODO: let's assume they have the same x points
#curve1 = config["lens"][lens]["motor"]["curves"][focus_curve]
#curve2 = config["lens"][lens]["motor"]["curves"][correction_curve]
imported_keypoints = config["lens"][lens]["debug_keypoints"]

for i in range(len(imported_keypoints)):
    keypoints["kp"][i] = {}
   
    # TODO: make sure it's safe output with no references &
    keypoints["kp"][i]["x"] = imported_keypoints[i][0]
    keypoints["kp"][i]["y"] = imported_keypoints[i][1]
    keypoints["kp"][i]["z"] = imported_keypoints[i][2]
    
    span = 0.5

    keypoints["kp"][i]["maxy"] = keypoints["kp"][i]["y"] + span
    keypoints["kp"][i]["miny"] = keypoints["kp"][i]["y"] - span
    
    keypoints["kp"][i]["maxz"] = keypoints["kp"][i]["z"] + span
    keypoints["kp"][i]["minz"] = keypoints["kp"][i]["z"] - span

   
print("Saving data file... ", end = '')    
kpt_file = "results\\keypoints.yaml"
with open(kpt_file, 'w') as f:
    yaml.dump(keypoints, f)
print("Done")
