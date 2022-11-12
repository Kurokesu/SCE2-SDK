import yaml
import cv2
from tqdm import tqdm
import matplotlib.pyplot as plt

fig, ax = plt.subplots()

results = None
print("Loading data")
config_file = "results\\results.yaml"
with open(config_file) as f:
    results = yaml.load(f, Loader=yaml.FullLoader)
    f.close()


for kp in tqdm(results["kp"], position=0):
    x = []
    x1 = []
    x2 = []
    y = []

    picture_list = results["kp"][kp]["pic"]
    for i in range(len(picture_list)):
        #print(picture_list[p]["name"], picture_list[p]["sharpness"])
        #x.append(picture_list[i]["name"])

        '''
        # find best focus point
        picture_list = results["kp"][1]["pic"]
        best_pic = None
        highest_sharpness = 0
        for p in range(len(picture_list)):
            if picture_list[p]["sharpness"] > highest_sharpness:
                best_pic = p
                highest_sharpness = picture_list[p]["sharpness"]
                
        print(picture_list[best_pic]["name"], picture_list[best_pic]["sharpness"])
        '''

        ts_gap = 9999999999999999999999
        best_motor = None

        motor_list = results["kp"][kp]["pos"]
        for p in range(len(motor_list)):
            ts = motor_list[p]["timestamp"]
            ts_abs_gap = abs(ts - picture_list[i]["name"])
            if ts_abs_gap < ts_gap:
                ts_gap = ts_abs_gap
                best_motor = p

        x.append(motor_list[best_motor]["x"])
        x1.append(motor_list[best_motor]["x"]+picture_list[i]["sharpness"]/5)
        x2.append(motor_list[best_motor]["x"]-picture_list[i]["sharpness"]/5)
        
        y.append(motor_list[best_motor]["y"])

    ax.plot(x, y, '--', linewidth=0.5, label=str(kp), color='black')
    ax.plot(x1, y, linewidth=0.5, label=str(kp), color='b')
    ax.plot(x2, y, linewidth=0.5, label=str(kp), color='b')
    ax.fill_betweenx(y, x1, x2, alpha = 0.2, color='b')


plt.show()
