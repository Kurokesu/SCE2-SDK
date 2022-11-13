import sys
import time
import yaml
from tqdm import tqdm
import sce2_lens
import local_coms

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


results = {}
results["kp"] = {}
results["lens"] = lens.lens_name

for kp in tqdm(keypoints["kp"], desc="Capturing frames"):
    #print()
    #print("-------------------------")
    #print("Key point:", kp)

    '''
    print("Homing")
    # TODO: check which lens it is. Home each lens according
    # Workaround for L117. Sometimes if Z is in -4..-2 Y axis can't home
    lens.send_command("G91 G0 Z2")
    lens.wait_for_idle(echo=False)
    lens.send_command("$HA")
    lens.send_command("$HX")
    lens.send_command("$HY")
    lens.send_command("$HZ")
    '''


    #print("Moving fast original sharp position")
    cmd =  "G90 G1"
    cmd += " X"
    cmd += str(keypoints["kp"][kp]["x"])
    cmd += " Y"
    cmd += str(keypoints["kp"][kp]["y"])
    cmd += " Z"
    cmd += str(keypoints["kp"][kp]["z"])
    cmd += " A"
    cmd += "0"
    cmd += " F"
    cmd += "1000"
    lens.send_command(cmd, echo=False)
    lens.wait_for_idle(echo=False)

    #print("Moving to min Y fast")
    cmd =  "G90 G1"
    cmd += " Y"
    cmd += str(keypoints["kp"][kp]["miny"])
    cmd += " F"
    cmd += "1000"
    lens.send_command(cmd, echo=False)
    lens.wait_for_idle(echo=False)

    #print("Moving to max Y slow")
    cmd =  "G90 G1"
    cmd += " Y"
    cmd += str(keypoints["kp"][kp]["maxy"])
    cmd += " F"
    cmd += "1"
    z.msg_text("record")
    lens.send_command(cmd, echo=False)
    positions = lens.wait_for_idle(echo=False)
    reply, status, t = z.msg_text("stop")
    #print("Done")


    results["kp"][kp] = {}

    #print()
    #print("Saving positions")
    results["kp"][kp]["pos"] = []
    for p in positions:
        pos = {}
        pos["x"], pos["y"], pos["z"], pos["x_lim"], pos["y_lim"], pos["z_lim"], pos["timestamp"], pos["status"] = p  
        results["kp"][kp]["pos"].append(pos)

    #print("Saving images")
    results["kp"][kp]["pic"] = []

    file_names = reply.split(",")[1:]
    for f in file_names:
        filename = "results\\"+str(f)+".jpg"
        f_ = {}
        f_["name"] = int(f)
        results["kp"][kp]["pic"].append(f_)


    '''

    while True:
        if not cam.frames.empty():
            (f, pic) = cam.frames.get()
            filename = "results\\"+str(f)+".jpg"

            cam.save(filename, pic)
            f_ = {}
            f_["name"] = f
            results["kp"][kp]["pic"].append(f_)
        else:
            break
    '''


reply, status, t = z.msg_text("hide")

print("Saving data file... ", end = '')
with open("results\\results.yaml", 'w') as f:
    yaml.dump(results, f)
print("Ok")
