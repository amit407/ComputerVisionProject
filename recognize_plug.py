import math
import cv2
import numpy as np
import crop_plug


def is_circle(circle, thresh):
    # Calculate the perimeter and enclosed area of the polygon
    perimeter = cv2.arcLength(circle, True)
    area = cv2.contourArea(circle)

    # Calculate the perimeter of a circle that has the same enclosed area
    circle_perimeter = 2 * np.pi * np.sqrt(area / np.pi)

    # Calculate the difference between the perimeters
    perimeter_diff = abs(perimeter - circle_perimeter)

    # Set a threshold for the perimeter difference
    threshold = thresh * perimeter

    # Return True if the difference is below the threshold, False otherwise
    return perimeter_diff < threshold


def has_big_angle(triangle_points):
    a = math.sqrt(
        (triangle_points[1][0] - triangle_points[0][0]) ** 2 + (triangle_points[1][1] - triangle_points[0][1]) ** 2)
    b = math.sqrt(
        (triangle_points[2][0] - triangle_points[1][0]) ** 2 + (triangle_points[2][1] - triangle_points[1][1]) ** 2)
    c = math.sqrt(
        (triangle_points[0][0] - triangle_points[2][0]) ** 2 + (triangle_points[0][1] - triangle_points[2][1]) ** 2)

    # Calculate the angles using the law of cosines
    cosA = (b ** 2 + c ** 2 - a ** 2) / (2 * b * c)
    cosB = (a ** 2 + c ** 2 - b ** 2) / (2 * a * c)
    cosC = (a ** 2 + b ** 2 - c ** 2) / (2 * a * b)

    angleA = (math.acos(cosA) * 180 / math.pi) > 100
    angleB = math.acos(cosB) * 180 / math.pi > 100
    angleC = math.acos(cosC) * 180 / math.pi > 100
    return angleA or angleB or angleC


def is_Three_linear(p1, p2, p3):
    # Calculate the slopes between the first two points and the second two points
    if abs(p2[0] - p1[0]) < 1 and abs(p2[0] - p3[0]) < 1:
        return True
    slope1 = (p2[1] - p1[1]) / (p2[0] - p1[0])
    slope2 = (p3[1] - p2[1]) / (p3[0] - p2[0])

    # Check if the slopes are approximately equal (with a tolerance of 0.1)
    return abs(slope1 - slope2) < 0.1


def has_one_bigger_hole(r1, r2, r3):
    if abs(r1 - r2) < 0.85:
        return abs(r3 - r2) >= 1.2 and abs(r3-r1) >= 1.2
    if abs(r1 - r3) < 0.85:
        return abs(r2 - r1) >= 1.2 and abs(r2-r3) >= 1.2
    if abs(r2 - r3) < 0.85:
        return abs(r1 - r2) >= 1.2 and abs(r1-r3) >= 1.2


def up_or_down(y1, y2, y3):
    y1_y2 = abs(y1 - y2)
    y1_y3 = abs(y1 - y3)
    y2_y3 = abs(y2 - y3)
    min_dist = min(y1_y2, y1_y3, y2_y3)
    if y1_y2 == min_dist:
        top_or_bottom = y3
        one_of_the_two = y1
    elif y1_y3 == min_dist:
        top_or_bottom = y2
        one_of_the_two = y1
    elif y2_y3 == min_dist:
        top_or_bottom = y1
        one_of_the_two = y2
    if top_or_bottom < one_of_the_two:
        return 'Up'
    else:
        return 'Down'


def recognize_plug(img_path):
    MIN_THRESH = 125

    img = cv2.imread(img_path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    gray_blur = cv2.GaussianBlur(gray, (9, 9), 10)

    # Threshold the image to create a binary mask until 3 or fewer contours
    while True:
        ret, mask = cv2.threshold(gray_blur, MIN_THRESH, 255, cv2.THRESH_BINARY_INV)
        # cv2.imshow("Detected holes", mask)
        # cv2.waitKey(0)
        # Find contours in the binary mask
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) <= 3:
            break
        MIN_THRESH -= 5
    holes = []
    holes_from_origin_image = []
    SECOND_MIN_THRESH = 150
    for shape in contours:
        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = float('-inf'), float('-inf')
        polygon = cv2.approxPolyDP(shape, 0.05 * cv2.arcLength(shape, True), True)
        for point in polygon:
            x, y = point[0]
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)

        # Crop the image to the bounding box of the contours
        cropped_img = img[min_y:max_y, min_x:max_x]
        crop_margin = 10

        # Adjust the boundaries of the crop
        cropped_img = img[(min_y - crop_margin):(max_y + crop_margin), (min_x - crop_margin):(max_x + crop_margin)]
        gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        # Apply Gaussian blur to reduce noise
        gray_blur = cv2.GaussianBlur(gray, (5, 5), 1)
        while True:
            ret, mask = cv2.threshold(gray_blur, SECOND_MIN_THRESH, 255, cv2.THRESH_BINARY_INV)

            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            # Find contours in the binary mask
            tmpContours, hierarchy = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(tmpContours) <= 1:
                tmpContours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if len(tmpContours) <= 1:
                    break
                else:
                    SECOND_MIN_THRESH -= 5
                    continue
                # cv2.imshow("Detected holes", opening)
                # cv2.waitKey(0)
                break
            SECOND_MIN_THRESH -= 5
        holes_from_origin_image.append((cropped_img, max_y))
        holes.append(tmpContours[0])

    circles = []
    rectangles = []
    radii = []
    for hole in holes:
        # first find circles
        polygon = cv2.approxPolyDP(hole, 0.001 * cv2.arcLength(hole, True), True)
        # cv2.drawContours(img, contours, -1, (0, 0, 255), 3)
        if len(polygon) >= 8:
            (x, y), radius = cv2.minEnclosingCircle(polygon)
            if is_circle(polygon, 0.098):
                radii.append(radius)
                circles.append("+")
                continue
        # find rectangles
        polygon = cv2.approxPolyDP(hole, 0.05 * cv2.arcLength(hole, True), True)

        if 2 <= len(polygon) <= 5:
            # cv2.drawContours(img, polygon, -1, (0, 255, 0), 3)  # for us to see the coontours delete later
            rectangles.append("-")
            continue
    if len(rectangles) == 2 and len(circles) == 0:
        return "A"
    elif len(rectangles) == 2 and len(circles) == 1:
        return "B"
    elif len(circles) == 2 and len(rectangles) == 0:
        return "C"
    elif len(circles) == 3:
        points = []
        for contour in contours:
            # first find circles
            polygon = cv2.approxPolyDP(contour, 0.001 * cv2.arcLength(contour, True), True)
            (x, y), radius = cv2.minEnclosingCircle(polygon)
            points.append((x, y))

        if is_Three_linear(points[0], points[1], points[2]):
            return "L"
        elif has_one_bigger_hole(radii[0], radii[1], radii[2]):
            return "D"
        else:
            if up_or_down(points[0][1], points[1][1], points[2][1]) == 'Down':
                if has_big_angle(points):
                    return "N"
                else:
                    return "H"
            else:
                return "O"

    elif len(rectangles) == 3:
        y_points = []
        for contour in contours:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            y_points.append(y)
        G_or_I = up_or_down(y_points[0], y_points[1], y_points[2])
        if G_or_I == 'Up':
            return "G"
        else:
            return "I"

    cv2.destroyAllWindows()



