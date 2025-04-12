import math
import re
import json

class Point3D:
    def __init__(self, x, y, z): self.x, self.y, self.z = x, y, z
    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)

class Point2D:
    def __init__(self, x, y): self.x, self.y = x, y
    def to_tuple(self): return (self.x, self.y)

class FoodStorage(Point3D):
    def __init__(self, x, y, z, diet): super().__init__(x, y, z); self.diet = diet

class Enclosure(Point3D):
    def __init__(self, x, y, z, importance, diet):
        super().__init__(x, y, z)
        self.importance = importance
        self.diet = diet
        self.fed = False

class Zoo:
    def __init__(self):
        self.dimensions = None
        self.depot = None
        self.battery_capacity = 0
        self.food_storages = []
        self.enclosures = []

    def load_from_file(self, filepath):
        with open(filepath) as f:
            lines = [line.strip() for line in f.readlines()]
        self.dimensions = parse_point3d(lines[0])
        self.depot = parse_point3d(lines[1])
        self.battery_capacity = int(lines[2])
        self.food_storages = parse_storages(lines[3])
        self.enclosures = parse_enclosures(lines[4])

def parse_point3d(text):
    nums = list(map(int, re.findall(r'-?\d+', text)))
    return Point3D(*nums)

def parse_storages(text):
    matches = re.findall(r'\((\d+),(\d+),(\d+),([cho])\)', text)
    return [FoodStorage(int(x), int(y), int(z), diet) for x, y, z, diet in matches]

def parse_enclosures(text):
    matches = re.findall(r'\((\d+),(\d+),(\d+),([\d.]+),([cho])\)', text)
    return [Enclosure(int(x), int(y), int(z), float(imp), diet) for x, y, z, imp, diet in matches]



def plan_drone_run(zoo, diet):
    path = [Point2D(zoo.depot.x, zoo.depot.y)]

    storage = min((fs for fs in zoo.food_storages if fs.diet == diet),
                  key=lambda s: s.distance_to(zoo.depot))
    path.append(Point2D(storage.x, storage.y))

    current = Point3D(storage.x, storage.y, storage.z)
    remaining_battery = zoo.battery_capacity
    remaining_battery -= zoo.depot.distance_to(storage)  # initial cost

    targets = [e for e in zoo.enclosures if not e.fed and e.diet == diet]
    targets.sort(key=lambda e: e.importance / current.distance_to(e), reverse=True)

    for e in targets:
        dist_to_enclosure = current.distance_to(e)
        dist_to_depot = e.distance_to(zoo.depot)
        if remaining_battery - (dist_to_enclosure + dist_to_depot) < 0:
            continue  # can't make it back
        path.append(Point2D(e.x, e.y))
        e.fed = True
        remaining_battery -= dist_to_enclosure
        current = e

    # return to depot
    path.append(Point2D(zoo.depot.x, zoo.depot.y))
    return path

def calculate_score(zoo, path, diet):
    total_dist = 0
    current = Point3D(path[0].x, path[0].y, zoo.depot.z)
    importance = 0

    for p in path[1:]:
        next_point = Point3D(p.x, p.y, 50)
        total_dist += current.distance_to(next_point)
        current = next_point
        fed = next((e for e in zoo.enclosures if e.x == p.x and e.y == p.y and e.diet == diet and e.fed), None)
        if fed:
            importance += fed.importance

    return importance * 1000 - total_dist

def main():
    zoo = Zoo()
    zoo.load_from_file("2.txt")

    all_runs = []

    for diet in ['c', 'h', 'o']:
        for e in zoo.enclosures:
            e.fed = False

        path = plan_drone_run(zoo, diet)
        run = [pt.to_tuple() for pt in path]
        all_runs.append(run)

    with open("final_output.txt", "w") as f:
        json.dump([[list(p) for p in run] for run in all_runs], f)

    print("\nFinal Output Format:\n", all_runs)

if __name__ == "__main__":
    main()
