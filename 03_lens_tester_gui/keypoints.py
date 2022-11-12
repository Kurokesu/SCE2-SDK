import yaml

'''
TODO
----
* [x] save on close
* [x] move to separate file
* [x] save data after each button press

* [ ] make gray keypoint tab
* [ ] remove old keypoint file
* [ ] remove old keypoint tab

* [ ] gui update button text once it is pressed min/max/...

'''

class Keypoints():
    data = {}
    active_kp = {}
    count = 0

    def __init__(self, lens):
        self.data["lens"] = lens
        self.data["kp"] = {}

    def new_kp(self):
        self.count += 1
        self.data["kp"][self.count] = {}
                
    def set_kp_val(self, name, value):
        self.data["kp"][self.count][name] = value
        self.save()

    def save(self):
        with open("keypoints.yaml", 'w') as f:
            yaml.dump(self.data, f)

    def validate_point(self):
        # TODO: quick and dirty way to test if all keys are present. works for now, update later
        valid = False
        param_list = ["x", "y", "z", "miny", "maxy", "minz", "maxz"]

        try:
            for i in param_list:
                test = self.data["kp"][self.count][i]
            valid = True
        except:
            pass

        return valid


    def __del__(self):
        # TODO: fix, throws NameError: name 'open' is not defined error
        #self.save()
        pass
