import cv2
import numpy as np
import math

def crop_image(img_path):
    threshold_value = 180
    # Load the image
    img = cv2.imread(img_path)

    # Get the current image dimensions
    height, width = img.shape[:2]

    # Set the new image dimensions
    if width > height:
        new_width = 500
        new_height = int(height * (new_width/width))
    else:
        new_height = 500
        new_width = int(width * (new_height/height))

    # Resize the image
    img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Apply a Gaussian blur to smooth the image
    blur = cv2.GaussianBlur(gray, (5, 5), 2)
    while True:
        ret, thresh = cv2.threshold(blur, threshold_value, 255, cv2.THRESH_BINARY)
        # Find contours in the mask
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        max_contour = max(contours, key=cv2.contourArea)
        polygon = cv2.approxPolyDP(max_contour, 0.05 * cv2.arcLength(max_contour, True), True)
        cv2.waitKey(0)
        hull = cv2.convexHull(polygon)
        # Iterate over the points in the hull
        hull = np.array(hull)

        # Get the number of points in the hull
        n = hull.shape[0]

        # Calculate the angles between each set of three consecutive points in the hull
        angles = []
        for i in range(n):
            p1 = hull[i % n]
            p2 = hull[(i + 1) % n]
            p3 = hull[(i + 2) % n]
            v1 = np.squeeze(p1 - p2)
            v2 = np.squeeze(p3 - p2)
            angle = np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
            angles.append(angle)

        # Convert the angles from radians to degrees
        angles = np.degrees(angles)

        if any(map(lambda x: x <= 52, angles)):
            threshold_value -= 20
        else:
            break
        # cv2.drawContours(img, polygon, -1, (0, 255, 0), 3)  # for us to see the coontours delete later

    # Create a mask with the same size as the original image, filled with white
    mask = np.zeros_like(img)
    mask.fill(255)

    # Fill the polygon with black on the mask
    cv2.fillPoly(mask, [hull[:, 0, :]], 0)

    # Apply the mask to the original image

    result = cv2.bitwise_or(img, mask)

    # # Display the result
    # cv2.imshow('Result', result)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    cv2.imwrite('Cropped Image.jpeg', result)

