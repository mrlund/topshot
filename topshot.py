import time
from picamera import PiCamera
import io
from PIL import Image
import numpy as np
import normalize_target
import topshotlib

# Initialize the camera
camera = PiCamera()

# Set the resolution
camera.resolution = (640, 480)  # Set to your desired resolution

# Set the zoom (crop)
camera.zoom = (0.25, 0.25, 0.5, 0.5)  # Crop to the center half of the frame

# Set the capture rate
capture_rate = 1  # captures every 2 seconds
stream = io.BytesIO()
#Capture an image
camera.capture(stream, format='jpeg')
image_bytes = stream.getvalue()
nparr = np.frombuffer(image_bytes, np.uint8)
matrix = normalize_target.normalize_target(nparr)

#Draw the center of the target and the circles




# Start capturing images, and scoring when there's a difference

image_count = 0
while True:
    # Capture an image
    with PiCamera() as camera:
        camera.capture(stream, format='jpeg')
    stream.seek(0)
    image = Image.open(stream)

    # Convert the image into a numpy array
    image_np = np.array(image)
    # Run your image processing script here
    
    # process_image(f'image_{image_count}.jpg')

    # Increment the image count
    image_count += 1

    # Wait for the next capture
    time.sleep(capture_rate)