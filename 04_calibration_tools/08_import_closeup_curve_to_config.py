import yaml
import cv2
from tqdm import tqdm

print("Loading config file")
results = None
results_file = "results\\results.yaml"
with open(results_file) as f:
    results = yaml.load(f, Loader=yaml.FullLoader)
    f.close()

config = {}
cfg_file = "../03_lens_tester_gui/config.yaml"
with open(cfg_file) as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    f.close()


lens = config["last_lens"]

print("Importing", lens, "updated drive curve back to the config file")

x_data = []
y_data = []
z_data = []

for kp in results["kp"]:
    picture_list = results["kp"][kp]["pic"]
    best_pic = None
    highest_sharpness = 0
    for p in range(len(picture_list)):
        if picture_list[p]["sharpness"] > highest_sharpness:
            best_pic = p
            highest_sharpness = picture_list[p]["sharpness"]
            
    #print(picture_list[best_pic]["name"], picture_list[best_pic]["sharpness"])

    ts_gap = 9999999999999999999999
    best_motor = None

    motor_list = results["kp"][kp]["pos"]
    for p in range(len(motor_list)):
        ts = motor_list[p]["timestamp"]
        ts_abs_gap = abs(ts - picture_list[best_pic]["name"])
        if ts_abs_gap < ts_gap:
            ts_gap = ts_abs_gap
            best_motor = p

    #print(motor_list[best_motor]['x'], motor_list[best_motor]['y'], motor_list[best_motor]['z']) 
    
    x_data.append(motor_list[best_motor]['x'])
    y_data.append(motor_list[best_motor]['y'])
    z_data.append(motor_list[best_motor]['z'])


config["lens"][lens]["motor"]["curves"]["focus_near"]["x"] = x_data
config["lens"][lens]["motor"]["curves"]["focus_near"]["y"] = y_data

config["lens"][lens]["motor"]["curves"]["zoom_correction"]["x"] = x_data
config["lens"][lens]["motor"]["curves"]["zoom_correction"]["y"] = z_data

with open(cfg_file, 'w') as f:
    yaml.dump(config, f)

print("Done")
