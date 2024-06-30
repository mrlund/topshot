import time  
from picamera2 import Picamera2  
import cv2 as cv
import normalize_target

  
def process_and_save_image(image_array, image_path):  
    # Your image processing logic here using OpenCV  

    # Save the processed image to disk  
    cv.imwrite(image_path, image_array)
  
# Initialize the camera  
camera = Picamera2()  
  
# Get the default camera configuration  
camera_config = camera.create_still_configuration()  
  
# Set the resolution to the highest supported by the Pi Camera Module 3  
camera_config['main']['size'] = (4608, 2592)  
  
# Apply the configuration  
camera.configure(camera_config)  
  
# Set the Region of Interest (ROI) for cropping  
# The values are actual pixel values (left, top, width, height)  
roi_left = 1992  # Starting x position (25% of 4608)  
roi_top = 248   # Starting y position (25% of 2592)  
roi_width = 904  # Width of the crop (50% of 4608)  
roi_height = 996  # Height of the crop (50% of 2592)  
camera.set_controls({"ScalerCrop": (roi_left, roi_top, roi_width, roi_height)})  
  
# Set the capture rate  
capture_rate = 1  # captures every 1 second  
image_count = 0  
  
camera.start()
while True:  
    # Capture an image  
    image_path = f'image_{image_count}.jpg'  
    image_array = camera.capture_array()  

    process_and_save_image(image_array, image_path) 
    #normalize_target.normalize_and_save_image(image_array, image_path,  debug_path="debug_image.jpg")
  
    # Run your image processing script here  
    #process_image(image_path)  
      
    # Increment the image count  
    image_count += 1  
      
    # Wait for the next capture  
    time.sleep(capture_rate)  
