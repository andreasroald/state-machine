total_points = 20
points_left = total_points
points = {
    "strength": 0,
    "speed": 0,
    "health": 0,
    "defense": 0,
    "magic": 0
}

def assign_points(points_left, points_dict):
    while points_left > 0:
        for key in points.keys():
            print("Add points to {0} (you have {1} points left)".format(key, points_left))

            input_points = int(input())

            if points_left - input_points > 0:
                points[key] += input_points
                points_left -= input_points
            else:
                points[key] += points_left
                points_left = 0

            print("Your {0} is now {1}".format(key, points[key]))

            if points_left <= 0:
                return points_left, points_dict

while True:
    points_left, points = assign_points(points_left, points)
    print("These are your stats:")
    for key in points.keys():
        print("{0}: {1}".format(key, points[key]))
    print("Do you want to re-assign your stats? [y/n]")

    if input().lower() == "n":
        print("OK, your character has been saved!")
        break
    else:
        points_left = total_points
        for key in points.keys():
            points[key] = 0
