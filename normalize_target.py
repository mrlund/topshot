import cv2  
import numpy as np  
  
def normalize_and_save_image(image_array, image_path, debug_path=None):  
    # Convert the image to grayscale if it is not already  
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
      
    if debug_path:  
        cv2.imwrite(debug_path, debug_img)  
      
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
    cv2.imwrite(image_path, img_transformed)  
  
# Example usage:  
# image_array = <your captured image array>  
# normalize_and_save_image(image_array, "transformed_image.jpg", debug_path="debug_image.jpg")  
