import cv2 as cv2
import numpy as np
import random


def find_target(image_array):
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
    x, y, w, h = cv2.boundingRect(second_largest_contour)
    zoneWidth = int(w / 8)
    x = x - zoneWidth
    y = y - zoneWidth
    w = w + zoneWidth
    h = h + zoneWidth
    # Step 2: Draw the rectangle around the second largest contour
    # Parameters: image, top-left corner, bottom-right corner, color (BGR), thickness
    # Debug: Draw only the second largest contour  
    debug_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)  # Convert to BGR for colored contours  
    cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0, 255, 0), 2)     
    cv2.drawContours(debug_img, [second_largest_contour], -1, (0, 255, 0), 2)  
      
    cv2.imwrite("normalized_target_debug.jpg", debug_img)  
          # return M, img.shape[1], img.shape[0]  
    return x, y, w, h

def calculate_perspective_shift(image_array):

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
    x, y, w, h = cv2.boundingRect(second_largest_contour)
    # Assuming x, y, w, h are the x-coordinate, y-coordinate, width, and height of the original rectangle
    # center_x = x + w / 2
    # center_y = y + h / 2

    # # Increase size by 25%
    # w = w * 1.25
    # h = h * 1.25

    # # Adjust top-left corner to keep the center the same
    # x = center_x - w / 2
    # y = center_y - h / 2

    # Step 2: Define the points of the bounding box in the source image
    src_pts = np.float32([[x, y], [x+w, y], [x+w, y+h], [x, y+h]])

    # Step 3: Define the target points for the square (assuming width == height for a perfect circle)
    side_len = max(w, h)
    dst_pts = np.float32([[0, 0], [side_len, 0], [side_len, side_len], [0, side_len]])

    # Step 4: Calculate the perspective transform matrix
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)

    #print(M, side_len)
    # Step 5: Apply the perspective warp transformation
    #warped_img = cv2.warpPerspective(img, M, (side_len, side_len))
    #cv2.imwrite("normalized_target_debug-1.jpg", warped_img)
      

    return M, side_len


def correct_perspective(image_array, rotation_matrix, side_len):
    img_transformed = cv2.warpPerspective(image_array, rotation_matrix, (side_len, side_len))
    cv2.imwrite("normalized_target_debug.jpg", img_transformed)
    return img_transformed

def calculate_target_zones(image_array):

    height, width = image_array.shape[:2]
    center = int(width/2)
    distanceBetween = int(width / 8); 
    # Draw the center of the circle
    cv2.circle(image_array,(center, center),distanceBetween,(0,0,255),3)
    nextRad = distanceBetween
    # new array of circles
    circles = []

    # Draw the 4 circles
    for i in range(4):
        nextRad = nextRad + distanceBetween
        cv2.circle(image_array,(center, center),nextRad,(0,0,255),3)
        circles.append(nextRad)

    cv2.imwrite("circles.jpg", image_array)
    return circles, width / 2

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

