import sys
import time
import yaml
from tqdm import tqdm
import sce2_lens
import local_coms

z = local_coms.LOCAL_COMS_MASTER()


keypoints = {}
lens_name = None
with open("results\\keypoints.yaml") as f:
    keypoints = yaml.load(f, Loader=yaml.FullLoader)
    f.close()


config = {}
cfg_file = "../03_lens_tester_gui/config.yaml"
with open(cfg_file) as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    f.close()


lens = sce2_lens.SCE2(config["port"])
ver = lens.send_command("$I", echo=False, expecting_lines=3)
print(ver)


#cam = uvc_camera.Camera(0)
#cam.start_task()

reply, status, t = z.msg_text("show")
#time.sleep(2)
#reply, status, t = z.msg_text("hide")
#sys.exit(1)


# detect lens
txt = ver[0].replace('[', '').replace(']', '')
txt_list = txt.split(':')    
id_strings = txt_list[2].split(',')
for i in id_strings:
    lens_detected = False
    if i[0:3] == "EFJ":
        lens_name = "L117"
        print("Homing L117")
        # TODO: check which lens it is. Home each lens according
        # Workaround for L117. Sometimes if Z is in -4..-2 Y axis can't home
        lens.send_command("G91 G0 Z2")
        lens.wait_for_idle(echo=False)
        lens.send_command("$HA")
        lens.send_command("$HX")
        lens.send_command("$HY")
        lens.send_command("$HZ")

#############################
# TODO: add other lens homing
#############################




results = {}
results["kp"] = {}

for kp in keypoints["kp"]:
    print()
    print("-------------------------")
    print("Key point:", kp)

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


    print("Moving fast original sharp position")
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
    lens.send_command(cmd)
    lens.wait_for_idle(echo=False)

    print("Moving to min Y fast")
    cmd =  "G90 G1"
    cmd += " Y"
    cmd += str(keypoints["kp"][kp]["miny"])
    cmd += " F"
    cmd += "1000"
    lens.send_command(cmd)
    lens.wait_for_idle(echo=False)

    print("Moving to max Y slow")
    cmd =  "G90 G1"
    cmd += " Y"
    cmd += str(keypoints["kp"][kp]["maxy"])
    cmd += " F"
    cmd += "1"
    z.msg_text("record")
    lens.send_command(cmd)
    positions = lens.wait_for_idle(echo=False)
    reply, status, t = z.msg_text("stop")
    print("Done")


    results["kp"][kp] = {}

    print()
    print("Saving positions")
    results["kp"][kp]["pos"] = []
    for p in positions:
        pos = {}
        pos["x"], pos["y"], pos["z"], pos["x_lim"], pos["y_lim"], pos["z_lim"], pos["timestamp"], pos["status"] = p  
        results["kp"][kp]["pos"].append(pos)

    print("Saving images")
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

print("Saving results")
with open("results\\results.yaml", 'w') as f:
    yaml.dump(results, f)


