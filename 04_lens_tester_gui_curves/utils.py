import yaml


def boot_routine(file):
    config = {}

    with open(file) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        f.close()

    config["clean_exit"] = False
    config["boot_count"] += 1

    with open(file, 'w') as f:
        yaml.dump(config, f)

    return config


def exit_routine(file, config):
    config["clean_exit"] = True
    with open(file, 'w') as f:
        yaml.dump(config, f)
