import yaml


class Keypoints():
    points = []
    
    def __init__(self, points):
        self.points = points

    def add_point(self, point):
        x = point[0]
        nr = -1

        for p in self.points:
            if p[0] == x:                
                #raise ValueError("Duplicate x axis not allowed")
                return -1

        self.points.append(point)
        self.sort()

        for p in range(len(self.points)):
            if self.points[p][0] == x:
                nr = p

        return nr

    def set_point(self, nr, point):
        self.delete_point(nr)
        nr = self.add_point(point)
        return nr

    def delete_point(self, nr):
        del self.points[nr]
        return nr-1
        
    def sort(self):
        self.points.sort(key=lambda x: x[0])



if __name__ == '__main__':
    config = {}
    with open("config.yaml") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        f.close()

    k = Keypoints(config["lens"]["L117"]["debug_keypoints"])
    #k = Keypoints([])

    k.add_point([2, 1, 1, 1])
    k.add_point([1.1, 2, 2, 2])
    k.set_point(0, [2.2, 2, 2, 2])

    print(k.points)
