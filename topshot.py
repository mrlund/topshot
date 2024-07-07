import time  
from picamera2 import Picamera2  
import cv2 as cv
import normalize_target
from topshot_lib import calculate_perspective_shift, calculate_target_zones, correct_perspective, draw_hit_and_score, find_hit_coordinates, find_target, score_hit


# Initialize the camera  
camera = Picamera2()  
  
# Get the default camera configuration  
camera_config = camera.create_still_configuration()  
  
# Set the resolution to the highest supported by the Pi Camera Module 3  
camera_config['main']['size'] = (4608, 2592)  
  
# Apply the configuration  
camera.configure(camera_config)  


camera.start()
target_array = camera.capture_array()
x, y, w, h = find_target(target_array)

camera.stop()
# Set the Region of Interest (ROI) for cropping  
camera.set_controls({"ScalerCrop": (int(x - (w*1.77/4)), y, int(w*1.77), w)})  

camera.start()
roi_only = camera.capture_array()
cv.imwrite("roi_only.jpg", roi_only)

M, side_len = calculate_perspective_shift(roi_only)

corrected = correct_perspective(roi_only, M, side_len)

circles, targetCenter = calculate_target_zones(corrected)


# Set the capture rate  
capture_rate = 1  # captures every 1 second  
image_count = 0  
previous_image = {}  
hits = []
scores = []

while len(hits) < 10:  
    # Capture an image  
    image_array = correct_perspective(camera.capture_array())

    if previous_image:
        hitX, hitY = find_hit_coordinates(previous_image, image_array)
        if hitX and hitY:
            print("Hit! ", hitX, hitY)
            hits.append([hitX,hitY])
            scores.append(score_hit(hitX, hitY, circles))
            image_count += 1  
      
    # Wait for the next capture  
    time.sleep(capture_rate)  

totalScore = 0
for i in len(hits):
    draw_hit_and_score(image_array, hits[i][1], hits[i][2])
    totalScore += scores[i]


