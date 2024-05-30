import cv2 as cv
import numpy as np
import random

# Load the image

def load_convert_image(image_path):
    img = cv.imread(image_path,1)
    # Resize the image
    scale_percent = 60 # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    img = cv.resize(img, dim, interpolation = cv.INTER_AREA)

    # Apply a blur to reduce noise
    img = cv.medianBlur(img,5)

    return img

def convertToBW(image):
    gray_image = cv.cvtColor(image.copy(), cv.COLOR_BGR2GRAY)
    ret, bw_img = cv.threshold(gray_image, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    return bw_img

def compare_and_markup(original, prev, next, circles, targetCenterX, targetCenterY):

    diff = cv.absdiff(prev, next)

    # Find contours in the difference image
    contours, _ = cv.findContours(diff, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    areas = [cv.contourArea(contour) for contour in contours]
    max_index = np.argmax(areas)
    contour_img = np.zeros_like(diff)

    # Draw only the largest contour
    cv.drawContours(contour_img, contours, max_index, (255), thickness=cv.FILLED)
    # Find the coordinates of the largest difference
    coords = cv.findNonZero(contour_img)

    # find the average value of the coordinates on both axis
    x = 0
    y = 0
    for coord in coords:
        x = x + coord[0][0]
        y = y + coord[0][1]
    x = x / len(coords)
    y = y / len(coords)

    # draw a circle on the original image at the average coordinates
    cv.circle(original,(int(x),int(y)),20,(255,0,0),3)

    # Calculate the smallest circle that contains any parts of the coords
    # Find the minimum and maximum x and y coordinates
    min_x = np.min(coords[:,0,0])
    min_y = np.min(coords[:,0,1])

    # iterate the circles and find the smallest circle that contains the coordinates
    min_circle = None
    points = 0
    for circle in circles:
    # Calculate the distance from the point to the center of the circle
        distance = ((targetCenterX - x) ** 2 + (targetCenterY - y) ** 2) ** 0.5

        # Check if the distance is less than the radius
        if distance < circle + 10:
            min_circle = circle
            #print the index of the circle
            points = (10 - circles.index(circle))
            print("Circle index: ", circles.index(circle), " Points: ", points)
            break

    return points, next

def find_circles(image):
    # Find the black center of the target
    circles = cv.HoughCircles(image, cv.HOUGH_GRADIENT, 1, 20, param1=700, param2=100, minRadius=50, maxRadius=0)
    circles = np.uint16(np.around(circles))

    max_radius = 0
    max_circle = None
    for i in circles[0,:]:
        if i[2] > max_radius:
            max_radius = i[2]
            max_circle = i

    # Draw the max circle on the image
    targetCenterX = max_circle[0]
    targetCenterY = max_circle[1]
    cv.circle(bw_img,(targetCenterX,targetCenterY),max_circle[2],(0,255,0),2)

    # Get the diameter of the circle
    diameter = max_circle[2] * 2
    distanceBetween = int(diameter / 8); 
    # Draw the center of the circle
    cv.circle(bw_img,(max_circle[0],max_circle[1]),2,(0,0,255),3)
    nextRad = 2
    # new array of circles
    circles = []

    # Draw the 8 points on the circle
    for i in range(8):
        nextRad = nextRad + distanceBetween
        cv.circle(targetImg,(max_circle[0], max_circle[1]), nextRad, (0, 0, 255), 3)
        circles.append(nextRad)

    return circles, targetCenterX, targetCenterY
