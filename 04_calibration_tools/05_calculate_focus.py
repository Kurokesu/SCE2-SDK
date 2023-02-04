import yaml
import cv2
from tqdm import tqdm


show_preview = True
use_roi = True


roi_tele = {}
roi_tele["x0"] = 650
roi_tele["y0"] = 370
roi_tele["x1"] = 1450
roi_tele["y1"] = 950

roi_wide = {}
roi_wide["x0"] = 890
roi_wide["y0"] = 430
roi_wide["x1"] = 1020
roi_wide["y1"] = 532



def find_y_point(xa, xb, ya, yb, xc):
    m = (ya - yb) / (xa - xb)
    yc = (xc - xb) * m + yb
    return yc

def find_x_point(xa, xb, ya, yb, yc):
    m = (xa - xb) / (ya - yb)
    xc = (yc - yb) * m + xb
    return xc


keypoints = None
print("Loading keypoint file... ", end = '')
kp_file = "results\\keypoints.yaml"
with open(kp_file) as f:
    keypoints = yaml.load(f, Loader=yaml.FullLoader)
    f.close()
print("OK")  

results = None
print("Loading data file... ", end = '')
config_file = "results\\results.yaml"
with open(config_file) as f:
    results = yaml.load(f, Loader=yaml.FullLoader)
    f.close()
print("OK")  
print()  


# find min/max of the lens x axis
'''
motor_x_pos_min = 9999999
motor_x_pos_max = -9999999
for kp in tqdm(results["kp"], position=0, desc="Keypoint"):
    picture_list = results["kp"][kp]["pic"]
    for p in tqdm(range(len(picture_list)), position=1, leave=False, desc="Frame"):
        motor_x_pos = results["kp"][kp]["pos"][p]["x"]
        if motor_x_pos >= motor_x_pos_max:
            motor_x_pos_max = motor_x_pos
        if motor_x_pos < motor_x_pos_min:
            motor_x_pos_min = motor_x_pos
'''

motor_x_pos_min = keypoints["kp"][0]["x"]
motor_x_pos_max = keypoints["kp"][len(keypoints["kp"])-1]["x"]


for kp in tqdm(results["kp"], position=0, desc="Keypoint"):
    picture_list = results["kp"][kp]["pic"]

    for p in tqdm(range(len(picture_list)), position=1, leave=False, desc="Frame"):
        kp_ = keypoints["kp"][kp]
        motor_x_pos = kp_["x"]
        filename = "results\\"+str(picture_list[p]["name"])+".jpg"

        img = cv2.imread(filename, cv2.IMREAD_COLOR)
        img_annoted = img.copy()
        roi = img

        if use_roi:
            x0_i = find_y_point(motor_x_pos_max, motor_x_pos_min, roi_wide["x0"], roi_tele["x0"], motor_x_pos)
            y0_i = find_y_point(motor_x_pos_max, motor_x_pos_min, roi_wide["y0"], roi_tele["y0"], motor_x_pos)
            x1_i = find_y_point(motor_x_pos_max, motor_x_pos_min, roi_wide["x1"], roi_tele["x1"], motor_x_pos)
            y1_i = find_y_point(motor_x_pos_max, motor_x_pos_min, roi_wide["y1"], roi_tele["y1"], motor_x_pos)
            x0_i = int(x0_i)
            y0_i = int(y0_i)
            x1_i = int(x1_i)
            y1_i = int(y1_i)

            img_annoted = cv2.rectangle(img_annoted, (x0_i, y0_i), (x1_i, y1_i), (0,255,0), 2)
            roi = img[y0_i:y1_i, x0_i:x1_i]

        if show_preview:
            cv2.imshow("image", img_annoted)
            cv2.waitKey(1)


        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        fm = cv2.Laplacian(gray, cv2.CV_64F).var()
        picture_list[p]["sharpness"] = float(fm)

        # TODO: show roi and value
        #print(fm)

print("Saving data file... ", end = '')
with open(config_file, 'w') as f:
    yaml.dump(results, f)
print("Done")    
