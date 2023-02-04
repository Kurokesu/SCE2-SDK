import yaml
import cv2
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots()

results = None
scale_sharpness = 1/5
print("Loading data file... ", end = '')
config_file = "results\\results.yaml"
with open(config_file) as f:
    results = yaml.load(f, Loader=yaml.FullLoader)
    f.close()
print("OK")


print("Loading keypoint file... ", end = '')
keypoints = {}
lens_name = None
with open("results\\keypoints.yaml") as f:
    keypoints = yaml.load(f, Loader=yaml.FullLoader)
    f.close()
print("Ok")


for kp in tqdm(results["kp"], position=0):
    x = []
    x1 = []
    x2 = []
    y = []

    best_x = []
    best_y = []

    picture_list = results["kp"][kp]["pic"]
    best_pic = None
    highest_sharpness = 0
    for p in range(len(picture_list)):
        try:
            if picture_list[p]["sharpness"] > highest_sharpness:
                best_pic = p
                highest_sharpness = picture_list[p]["sharpness"]
        except:
            pass

    ts_gap = 9999999999999999999999
    best_motor = None

    motor_list = results["kp"][kp]["pos"]
    for p in range(len(motor_list)):
        ts = motor_list[p]["timestamp"]
        ts_abs_gap = abs(ts - picture_list[best_pic]["name"])
        if ts_abs_gap < ts_gap:
            ts_gap = ts_abs_gap
            best_motor = p

    
    #ax.scatter(motor_list[best_motor]['x'], motor_list[best_motor]['y'], c ="red", alpha = 0.9, s = 20, marker ="x")
    ax.scatter(motor_list[best_motor]['x']+picture_list[best_pic]["sharpness"]*scale_sharpness, motor_list[best_motor]['y'], c ="red", alpha = 0.9, s = 20, marker ="x")
    ax.plot([motor_list[best_motor]['x'], motor_list[best_motor]['x']+picture_list[best_pic]["sharpness"]*scale_sharpness], [motor_list[best_motor]['y'], motor_list[best_motor]['y']], c ="red", alpha = 0.4, linewidth=0.8)  

    picture_list = results["kp"][kp]["pic"]
    for i in range(len(picture_list)):       
        ts_gap = 9999999999999999999999
        best_motor = None
        motor_list = results["kp"][kp]["pos"]
        peak_y = 0
        peak_x = 0
        for p in range(len(motor_list)):
            ts = motor_list[p]["timestamp"]
            ts_abs_gap = abs(ts - picture_list[i]["name"])
            if ts_abs_gap < ts_gap:
                ts_gap = ts_abs_gap
                best_motor = p

        #if results["lens"] == "L117":
        x.append(motor_list[best_motor]["x"])
        x1.append(motor_list[best_motor]["x"]+picture_list[i]["sharpness"]*scale_sharpness)
        #x2.append(motor_list[best_motor]["x"]-picture_list[i]["sharpness"]*scale_sharpness)
        y.append(motor_list[best_motor]["y"])

    #best_x.append(motor_list[best_motor]['y'])
    #ax.scatter(x, y, c ="black", alpha = 0.9, s = 25, marker ="x")

    ax.plot(x, y, linestyle='dashed', linewidth=0.5, label=str(kp), color='black')
    ax.plot(x1, y, linewidth=0.5, label=str(kp), color='b')
    #ax.plot(x2, y, linewidth=0.5, label=str(kp), color='b')
    ax.fill_betweenx(y, x1, x, alpha = 0.2, color='b')


for kp in range(len(keypoints["kp"])):
    x = keypoints["kp"][kp]["x"]
    y = keypoints["kp"][kp]["y"]
    ax.scatter(x, y, c ="black", alpha = 0.9, s = 25, marker ="x")
    

plt.show()
