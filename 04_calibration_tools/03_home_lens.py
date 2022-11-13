import sys
import time
import yaml
from tqdm import tqdm
import sce2_lens
import local_coms

print("Loading config file... ", end = '')
config = {}
cfg_file = "../03_lens_tester_gui/config.yaml"
with open(cfg_file) as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    f.close()
print("Ok")


print("Using port:", config["port"])
lens = sce2_lens.SCE2(config["port"])
print("Detecting lens:", lens.lens_name)

lens.home_lens(echo=True)
