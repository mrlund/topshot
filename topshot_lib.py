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
    if len(image_array.shape) == 3 and image_array.shape[2] == 3:  
        image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)  

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
    # Function to calculate the bounding box area and aspect ratio of a contour

def contour_area_and_perimeter(contour):
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)
    return area, perimeter

def filter_contours(contours, min_area, max_area):
    filtered_contours = []
    for contour in contours:
        area, perimeter = contour_area_and_perimeter(contour)
        if min_area <= area <= max_area:
            filtered_contours.append((contour, area, perimeter))
    return filtered_contours

def preprocess_and_draw_contours(prev_image_array, new_image_array, tolerance=100, min_area=500, max_area=3000):
    prev_image_copy = prev_image_array.copy()
    new_image_copy = new_image_array.copy()

    if len(prev_image_copy.shape) == 3 and prev_image_copy.shape[2] == 3:  
        prev_image_copy = cv2.cvtColor(prev_image_copy, cv2.COLOR_BGR2GRAY)  

    if len(new_image_copy.shape) == 3 and new_image_copy.shape[2] == 3:  
        new_image_copy = cv2.cvtColor(new_image_copy, cv2.COLOR_BGR2GRAY)

    _, prev_binary = cv2.threshold(prev_image_copy, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, new_binary = cv2.threshold(new_image_copy, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    prev_contours, _ = cv2.findContours(prev_binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    prev_contours = filter_contours(prev_contours, min_area, max_area)

    new_contours, _ = cv2.findContours(new_binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    new_contours = filter_contours(new_contours, min_area, max_area)

    # Debug: Draw previous contours
    prev_contours_img = np.ones_like(prev_binary) * 255
    for contour, _, _ in prev_contours:
        cv2.drawContours(prev_contours_img, [contour], -1, (0, 0, 0), thickness=1)
    #cv2.imwrite("debug_prev_contours.jpg", prev_contours_img)

    # Debug: Draw new contours
    new_contours_img = np.ones_like(new_binary) * 255
    for contour, _, _ in new_contours:
        cv2.drawContours(new_contours_img, [contour], -1, (0, 0, 0), thickness=1)
    #cv2.imwrite("debug_new_contours.jpg", new_contours_img)

    remaining_contours = []
    for new_contour, new_area, new_perimeter in new_contours:
        match_found = False
        for prev_contour, prev_area, prev_perimeter in prev_contours:
            if abs(new_area - prev_area) < tolerance and abs(new_perimeter - prev_perimeter) < tolerance:
                match_found = True
                break
        if not match_found:
            remaining_contours.append(new_contour)

    result_img = np.ones_like(new_binary) * 255
    cv2.drawContours(result_img, remaining_contours, -1, (0, 0, 0), thickness=1)
    #cv2.imwrite("debug_remaining_contours.jpg", result_img)

    if remaining_contours:
        # Fit a circle around the first remaining contour
        (x, y), radius = cv2.minEnclosingCircle(remaining_contours[0])
        center = (int(x), int(y))
        radius = int(radius)
        return center, radius
    else:
        return None, None

def find_hit_coordinates(prev_image_array, new_image_array, min_area=100):

    # Preprocess the images and draw contours
    center, radius = preprocess_and_draw_contours(prev_image_array, new_image_array)

    if center is None or radius is None:
        print("No hit detected")
        return None, None

    print(f"Hit detected at {center} with radius {radius}")
        # Mark the hit location on the original image
    # Check if the new_image_array is already in BGR format
    if len(new_image_array.shape) == 2:  # Grayscale image
        hit_location_img = cv2.cvtColor(new_image_array, cv2.COLOR_GRAY2BGR)
    else:  # Already in BGR format
        hit_location_img = new_image_array.copy()

    cv2.circle(hit_location_img, (int(center[0]), int(center[1])), radius, (0, 0, 255), 2)
    cv2.imwrite("hit_location.jpg", hit_location_img)  # Save the image with the hit location marked

    return center, radius

def score_hit(center, radius, zones):
        # Calculate the smallest circle that contains any parts of the coords
    # Find the minimum and maximum x and y coordinates
    # min_x = np.min(coords[:,0,0])
    # min_y = np.min(coords[:,0,1])


    # iterate the circles and find the smallest circle that contains the coordinates
    x, y = center[0], center[1]
    min_circle = None
    points = 0
    for circle in zones:
        print(circle)
    # Calculate the distance from the point to the center of the circle
        distance = (x ** 2 + y ** 2) ** 0.5
        print(distance)
        # Check if the distance is less than the radius
        if distance < circle + radius:
            min_circle = circle
            #print the index of the circle
            points = (10 - zones.index(circle))
            print("Circle index: ", zones.index(circle), " Points: ", points)
            break

    return points

def draw_hit_and_score(image_array, x, y, score):
    cv2.circle(image_array,(int(x),int(y)),20,(255,0,0),3)
    cv2.putText(image_array, str(score), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 2, cv2.LINE_AA)
    return image_array

