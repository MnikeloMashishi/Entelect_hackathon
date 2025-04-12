import math
import re
import json

# drone flight calculations
class Point3D:
    def __init__(self, x, y, z): self.x, self.y, self.z = x, y, z
    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)

# used for final output
class Point2D:
    def __init__(self, x, y): self.x, self.y = x, y
    def to_tuple(self): return (self.x, self.y)

# food storage location
class FoodStorage(Point3D):
    def __init__(self, x, y, z, diet): super().__init__(x, y, z); self.diet = diet

# animale enclosure
class Enclosure(Point3D):
    def __init__(self, x, y, z, importance, diet):
        super().__init__(x, y, z)
        self.importance = importance
        self.diet = diet
        self.fed = False #if eclosure has been visited

# this is the whole zoo
class Zoo:
    def __init__(self):
        self.dimensions = None
        self.depot = None
        self.battery_capacity = 0
        self.food_storages = []
        self.enclosures = []

    # get zoo details from file
    def load_from_file(self, filepath):
        with open(filepath) as f:
            lines = [line.strip() for line in f.readlines()]
        self.dimensions = parse_point3d(lines[0])
        self.depot = parse_point3d(lines[1])
        self.battery_capacity = int(lines[2])
        self.food_storages = parse_storages(lines[3])
        self.enclosures = parse_enclosures(lines[4])

# get coordinates (x, y, z)
def parse_point3d(text):
    nums = list(map(int, re.findall(r'\d+', text)))
    return Point3D(*nums)

# food storage
def parse_storages(text):
    matches = re.findall(r'\((\d+),(\d+),(\d+),([cho])\)', text)
    return [FoodStorage(int(x), int(y), int(z), diet) for x, y, z, diet in matches]

# enclosures
def parse_enclosures(text):
    matches = re.findall(r'\((\d+),(\d+),(\d+),([\d.]+),([cho])\)', text)
    return [Enclosure(int(x), int(y), int(z), float(imp), diet) for x, y, z, imp, diet in matches]

# prep the drone
def plan_drone_run(zoo, diet):
    path = [Point2D(zoo.depot.x, zoo.depot.y)]
    storage = min((fs for fs in zoo.food_storages if fs.diet == diet),
                  key=lambda s: s.distance_to(Point3D(zoo.depot.x, zoo.depot.y, 50)))
    path.append(Point2D(storage.x, storage.y))

    current = Point3D(storage.x, storage.y, 50)
    targets = [e for e in zoo.enclosures if not e.fed and e.diet == diet]

    # go to enclosures
    while targets:
        next_enclosure = min(targets, key=lambda e: e.distance_to(current))
        path.append(Point2D(next_enclosure.x, next_enclosure.y))
        next_enclosure.fed = True
        current = next_enclosure
        targets.remove(next_enclosure)

    # back to depot
    path.append(Point2D(zoo.depot.x, zoo.depot.y))
    return path

def calculate_score(zoo, path, diet):
    total_dist = 0
    current = Point3D(path[0].x, path[0].y, 10)
    importance = 0

    for p in path[1:]:
        next_point = Point3D(p.x, p.y, 50)
        total_dist += current.distance_to(next_point)
        current = next_point
        fed = next((e for e in zoo.enclosures if e.x == p.x and e.y == p.y and e.diet == diet and e.fed), None)
        if fed:
            importance += fed.importance

    return importance * 1000 - total_dist

# try each diet and pick the best run
def main():
    zoo = Zoo()
    zoo.load_from_file("1.txt")

    best_score = float('-inf')
    best_path = []

    # Try each diet
    for diet in ['c', 'h', 'o']:
        for e in zoo.enclosures:
            e.fed = False
        path = plan_drone_run(zoo, diet)
        score = calculate_score(zoo, path, diet)
        print(f"Diet {diet.upper()}: Score = {score:.2f}")
        if score > best_score:
            best_score = score
            best_path = path

    output = [[pt.to_tuple() for pt in best_path]]
    with open("level1_output.txt", "w") as f:
        json.dump(output, f)

    print("\nBest Run Path Output:\n", output)

if __name__ == "__main__":
    main()