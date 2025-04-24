import json


def boot_routine(file):
    config = {}

    with open(file) as f:
        config = json.load(f)
        f.close()

    config["clean_exit"] = False
    config["boot_count"] += 1

    with open(file, 'w') as f:
        json.dump(config, f, indent=2)

    return config


def exit_routine(file, config):
    config["clean_exit"] = True
    with open(file, 'w') as f:
        json.dump(config, f, indent=2)
