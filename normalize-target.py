import cv2
import numpy as np

def normalize_target(image_nparr):
    # Convert bytes to numpy array
    img = cv2.imdecode(image_nparr, cv2.IMREAD_COLOR)
    _, img = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    ellipse = cv2.fitEllipse(contours[0])
    M = cv2.getRotationMatrix2D(ellipse[1], ellipse[2], 1)
    img = cv2.warpAffine(img, M, img.shape)
    return M


# # Threshold the image
# _, img = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY)

# # Find contours in the image
# contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# # Find the ellipse
# ellipse = cv2.fitEllipse(contours[0])

# # Calculate the transformation that would make the ellipse a circle
# M = cv2.getRotationMatrix2D(ellipse[1], ellipse[2], 1)

# # Apply the transformation to the image
# img = cv2.warpAffine(img, M, img.shape)

# # Save the transformed image
# cv2.imwrite('transformed_image.jpg', img)