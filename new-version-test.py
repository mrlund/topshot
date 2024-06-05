import cv2  
import numpy as np  
from picamera2 import Picamera2  
import time  
  
# Initialize the camera  
picam2 = Picamera2()  
picam2.start()  
  
def capture_image():  
    frame = picam2.capture_array()  
    return frame  
  
def find_target(frame):  
    # Convert to grayscale  
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  
    # Threshold to detect the black circle  
    _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)  
    # Find contours  
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  
    for contour in contours:  
        # Approximate the contour to a circle  
        (x, y), radius = cv2.minEnclosingCircle(contour)  
        if radius > 10 and radius < 100:  # Filter out small and large contours  
            return (int(x), int(y)), int(radius)  
    return None, None  
  
def calculate_zone_distances(radius):  
    return [radius * i for i in range(1, 5)]  
  
def draw_target_zones(frame, center, radius):  
    zone_distances = calculate_zone_distances(radius)  
    for i, distance in enumerate(zone_distances):  
        cv2.circle(frame, center, int(distance), (0, 255, 0), 2)  
    return frame  
  
def detect_shots(prev_frame, curr_frame, center, radius):  
    # Detect new holes in the target  
    diff = cv2.absdiff(prev_frame, curr_frame)  
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)  
    _, thresh_diff = cv2.threshold(gray_diff, 50, 255, cv2.THRESH_BINARY)  
    contours, _ = cv2.findContours(thresh_diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  
      
    shots = []  
    for contour in contours:  
        (x, y), shot_radius = cv2.minEnclosingCircle(contour)  
        if shot_radius > 2:  # Filter out noise  
            distance = np.sqrt((x - center[0])**2 + (y - center[1])**2)  
            zone = min(int(distance // radius) + 1, 5)  
            points = 10 - (zone - 1) * 2  
            shots.append(((int(x), int(y)), points))  
    return shots  
  
def draw_shots(frame, shots):  
    for (x, y), points in shots:  
        cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)  
    return frame  
  
def main():  
    # Capture initial frame to detect target and correct perspective  
    initial_frame = capture_image()  
    center, radius = find_target(initial_frame)  
      
    if center is None or radius is None:  
        print("Target not found.")  
        return  
  
    # Draw the target zones once  
    initial_frame = draw_target_zones(initial_frame, center, radius)  
      
    prev_frame = initial_frame  
    total_score = 0  
    detected_shots = []  
  
    while len(detected_shots) < 10:  
        curr_frame = capture_image()  
          
        new_shots = detect_shots(prev_frame, curr_frame, center, radius)  
        for shot in new_shots:  
            if shot not in detected_shots:  
                detected_shots.append(shot)  
                total_score += shot[1]  
          
        # Draw the detected shots on the current frame  
        curr_frame = draw_shots(curr_frame, detected_shots)  
          
        # Display current frame for debugging purposes (optional)  
        cv2.imshow("Current Frame", curr_frame)  
        if cv2.waitKey(1) & 0xFF == ord('q'):  
            break  
          
        # Update previous frame  
        prev_frame = curr_frame  
  
        # Sleep for 1 second before capturing the next frame  
        time.sleep(1)  
  
    # Draw final results  
    final_frame = draw_shots(initial_frame, detected_shots)  
    cv2.putText(final_frame, f'Total Score: {total_score}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)  
  
    # Save the final image  
    cv2.imwrite("final_result.png", final_frame)  
    print("Final result saved as final_result.png")  
  
    # Display the final image  
    cv2.imshow("Final Result", final_frame)  
    cv2.waitKey(0)  
    cv2.destroyAllWindows()  
  
if __name__ == "__main__":  
    main()  

