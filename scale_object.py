def scale(lower_corner, upper_corner):
    delta1 = str(max(float(lower_corner[0]) - float(upper_corner[0]),
                     float(upper_corner[0]) - float(lower_corner[0])))
    delta2 = str(max(float(lower_corner[1]) - float(upper_corner[1]),
                     float(upper_corner[1]) - float(lower_corner[1])))
    return delta1, delta2


def main():
    lower_corner = input().split()
    upper_corner = input().split()
    print(scale(lower_corner, upper_corner))


if __name__ == '__main__':
    main()
