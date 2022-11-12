import os

def deltree(target):
    for d in os.listdir(target):
        try:
            deltree(target + '/' + d)
        except OSError:
            os.remove(target + '/' + d)

    os.rmdir(target)

print("Removing results folder")
try:
    deltree("results")
except:
    pass

print("Creating fresh results folder")
try:
    os.mkdir("results")
except:
    pass


