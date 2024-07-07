import cv2 as cv2
import numpy as np
import random


def find_target_and_correct_perspective(image_array):
    if len(image_array.shape) == 3 and image_array.shape[2] == 3:  
        image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)  
      
    # Threshold the image  
    _, img = cv2.threshold(image_array, 50, 255, cv2.THRESH_BINARY)  
      
    # Find contours in the image  
    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  
      
    if len(contours) < 2:  
        raise ValueError("Not enough contours found in the image.")  
      
    # Sort contours by area in descending order  
    contours = sorted(contours, key=cv2.contourArea, reverse=True)  
      
    # Select the second largest contour  
    second_largest_contour = contours[1]  
      
    # Debug: Draw only the second largest contour  
    debug_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)  # Convert to BGR for colored contours  
    cv2.drawContours(debug_img, [second_largest_contour], -1, (0, 255, 0), 2)  
      
    cv2.imwrite("normalized_target_debug.jpg", debug_img)  
      
    # Fit an ellipse to the second largest contour  
    if len(second_largest_contour) < 5:  
        raise ValueError("Not enough points to fit an ellipse.")  
    ellipse = cv2.fitEllipse(second_largest_contour)  
      
    # Calculate the scaling factors  
    (center, axes, angle) = ellipse  
    major_axis_length = max(axes)  
    minor_axis_length = min(axes)  
    scale_x = major_axis_length / minor_axis_length  
    scale_y = 1.0  # No scaling in the y direction  
      
    # Calculate the transformation matrix to make the ellipse a circle  
    M = cv2.getRotationMatrix2D(center, angle, scale_x)  
      
    # Apply the transformation to the image  
    img_transformed = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))  
      
    # Save the transformed image  
    cv2.imwrite("normalized_target.jpg", img_transformed)
    return M, img.shape[1], img.shape[0]  

def get_target_and_correct_perspective(image_array, rotation_matrix, shapeX, shapeY):
    img_transformed = cv2.warpAffine(image_array, rotation_matrix, shapeX, shapeY)
    return img_transformed

def calculate_target_zones(image_array):
    # Find the black center of the target
    circles = cv2.HoughCircles(image_array, cv2.HOUGH_GRADIENT, 1, 20, param1=700, param2=100, minRadius=50, maxRadius=0)
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
    cv2.circle(image_array,(targetCenterX,targetCenterY),max_circle[2],(0,255,0),2)

    # Get the diameter of the circle
    diameter = max_circle[2] * 2
    distanceBetween = int(diameter / 8); 
    # Draw the center of the circle
    cv2.circle(image_array,(max_circle[0],max_circle[1]),2,(0,0,255),3)
    nextRad = 2
    # new array of circles
    circles = []

    # Draw the 8 points on the circle
    for i in range(8):
        nextRad = nextRad + distanceBetween
        circles.append(nextRad)

    return circles, targetCenterX, targetCenterY

def find_hit_coordinates(prev_image_array, new_image_array):
    diff = cv2.absdiff(prev_image_array, new_image_array)

    # Find contours in the difference image
    contours, _ = cv2.findContours(diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    areas = [cv2.contourArea(contour) for contour in contours]
    max_index = np.argmax(areas)
    contour_img = np.zeros_like(diff)

    # Draw only the largest contour
    cv2.drawContours(contour_img, contours, max_index, (255), thickness=cv2.FILLED)
    # Find the coordinates of the largest difference
    coords = cv2.findNonZero(contour_img)

    # find the average value of the coordinates on both axis
    x = 0
    y = 0
    for coord in coords:
        x = x + coord[0][0]
        y = y + coord[0][1]
    x = x / len(coords)
    y = y / len(coords)
    return x, y

def score_hit(x, y, zones):
        # Calculate the smallest circle that contains any parts of the coords
    # Find the minimum and maximum x and y coordinates
    # min_x = np.min(coords[:,0,0])
    # min_y = np.min(coords[:,0,1])


    # iterate the circles and find the smallest circle that contains the coordinates
    min_circle = None
    points = 0
    for circle in zones:
    # Calculate the distance from the point to the center of the circle
        distance = (x ** 2 + y ** 2) ** 0.5

        # Check if the distance is less than the radius
        if distance < circle + 10:
            min_circle = circle
            #print the index of the circle
            points = (10 - zones.index(circle))
            print("Circle index: ", zones.index(circle), " Points: ", points)
            break

    return points

def draw_hit_and_score(image_array, x, y, score):
    cv2.circle(image_array,(int(x),int(y)),20,(255,0,0),3)
    cv2.putText(image_array, score, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 2, cv2.LINE_AA)
    return image_array

