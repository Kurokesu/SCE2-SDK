import yaml
import cv2
from tqdm import tqdm

results = None
print("Loading data file... ", end = '')
config_file = "results\\results.yaml"
with open(config_file) as f:
    results = yaml.load(f, Loader=yaml.FullLoader)
    f.close()
print("OK")  
print()  


for kp in tqdm(results["kp"], position=0, desc="Keypoint"):
    picture_list = results["kp"][kp]["pic"]
    for p in tqdm(range(len(picture_list)), position=1, leave=False, desc="Frame"):
        filename = "results\\"+str(picture_list[p]["name"])+".jpg"
        #print(picture_list[p])
        #print(filename)
        #roi = img[cfg["ROI"][r]["y0"]:cfg["ROI"][r]["y1"], cfg["ROI"][r]["x0"]:cfg["ROI"][r]["x1"]]
        img = cv2.imread(filename, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        fm = cv2.Laplacian(gray, cv2.CV_64F).var()
        picture_list[p]["sharpness"] = float(fm)

        # TODO: show roi and value
        #print(fm)

print("Saving data file... ", end = '')
with open(config_file, 'w') as f:
    yaml.dump(results, f)
print("Done")    
