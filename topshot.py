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
#previous_image = correct_perspective(camera.capture_array(), M, side_len)  
previous_image = cv.imread("Capture-0.jpg")
hits = []
scores = []
print("Starting!")

test_images = ["Capture-0.jpg", "Capture-1.jpg"]

while len(hits) < 1:  
    # Capture an image  
    #image_array = correct_perspective(camera.capture_array(), M, side_len)
    #cv.imwrite("Capture-" + str(image_count) + ".jpg", image_array)
    image_array = cv.imread("Capture-1.jpg")
    image_count += 1  
    center, radius = find_hit_coordinates(previous_image, image_array)
    if center and radius:
        hits.append([center[0],center[1]])
        score = score_hit(center, radius, circles)
        scores.append(score)
        print("Hit! ", center[0],center[1], score, image_count)
    else:
        print("No hit found")
    # Wait for the next capture  
    previous_image = image_array
    time.sleep(capture_rate)  

totalScore = 0
print(hits)
for hit in hits:
    draw_hit_and_score(image_array, hit[0], hit[1], 5)
    cv.imwrite("Finalscore.jpg", image_array)
for score in scores:
    totalScore += score
print("Total: ", totalScore)

