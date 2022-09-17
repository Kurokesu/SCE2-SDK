import yaml

config_file   = "config.yaml"
keypoint_file = "keypoints.txt"
curve_name    = "focus_inf"
save_correction_curve = True





keypoints_data = None
keypoint_x = []
keypoint_y = []
keypoint_z = []
keypoint_a = []


with open(keypoint_file, "r") as f:
    #config = yaml.load(f, Loader=yaml.FullLoader)
    keypoints_data = f.readlines()
    f.close()

for i in range(len(keypoints_data)):
    keypoints_data_line = keypoints_data[i].strip().split(", ")
    keypoint_x.append(float(keypoints_data_line[0]))
    keypoint_y.append(float(keypoints_data_line[1]))
    keypoint_z.append(float(keypoints_data_line[2]))
    keypoint_a.append(float(keypoints_data_line[3]))

config = None
with open(config_file) as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    f.close()


config["lens"]["L086"]["motor"]["curves"]["focus_inf"]["x"] = keypoint_x
config["lens"]["L086"]["motor"]["curves"]["focus_inf"]["y"] = keypoint_z

if save_correction_curve:
    config["lens"]["L086"]["motor"]["curves"]["zoom_correction"]["x"] = keypoint_x
    config["lens"]["L086"]["motor"]["curves"]["zoom_correction"]["y"] = keypoint_y


with open(config_file, 'w') as f:
    yaml.dump(config, f)
