import topshotlib
import cv2 as cv
# Start of the program
# ---------------------


targetImg = topshotlib.load_convert_image('./target.jpg')
bw_img = topshotlib.convertToBW(targetImg.copy())

circles, targetCenterX, targetCenterY = topshotlib.find_circles(bw_img)
points = []
fileNames = ['./target-0.jpg', './target-1.jpg', './target-2.jpg', './target-3.jpg', './target-4.jpg']
prevImg = topshotlib.convertToBW(topshotlib.load_convert_image(fileNames[0]))
for i in range(4): 
     nextImg = topshotlib.convertToBW(topshotlib.load_convert_image(fileNames[i+1]))
     point, prevImg = topshotlib.compare_and_markup(targetImg, prevImg, nextImg, circles, targetCenterX, targetCenterY)
     points.append(point)

scores = ' | '.join(map(str, points))
scores = scores + " | Total: " + str(sum(points))
print(scores)
# Write the scores to the image at the bottom
font = cv.FONT_HERSHEY_SIMPLEX
center_x = targetImg.shape[1] // 2
bottom_y = targetImg.shape[0] - 40  # 10 pixels from the bottom
cv.putText(targetImg, scores, (center_x, bottom_y), font, 2, (255, 0, 0), 2, cv.LINE_AA)
cv.imwrite('Results.jpg', targetImg)
