import time
from picamera import PiCamera

# Initialize the camera
camera = PiCamera()

# Set the resolution
camera.resolution = (640, 480)  # Set to your desired resolution

# Set the zoom (crop)
camera.zoom = (0.25, 0.25, 0.5, 0.5)  # Crop to the center half of the frame

# Set the capture rate
capture_rate = 0.5  # captures every 2 seconds

image_count = 0

while True:
    # Capture an image
    camera.capture(f'image_{image_count}.jpg')

    # Run your image processing script here
    # process_image(f'image_{image_count}.jpg')

    # Increment the image count
    image_count += 1

    # Wait for the next capture
    time.sleep(capture_rate)