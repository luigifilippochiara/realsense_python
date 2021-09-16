import cv2
import pyrealsense2
from realsense_depth import DepthCamera


point = (400, 300)

def show_distance(event, x, y, args, params):
    global point
    point = (x, y)

# Initialize Camera Intel Realsense
dc = DepthCamera()

# Create mouse event
cv2.namedWindow("color frame")
cv2.setMouseCallback("color frame", show_distance)

while True:
    ret, depth_frame, color_frame = dc.get_frame()

    # Show distance for a specific point
    cv2.circle(color_frame, point, 4, (0, 0, 255))

    x, y = point

    distance = depth_frame[y, x]

    print(distance)

    cv2.putText(color_frame, "{}, {}: {}mm".format(x, y, distance), (x - 70, y - 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)

    cv2.imshow("depth frame", depth_frame)
    cv2.imshow("color frame", color_frame)
    key = cv2.waitKey(1)
    if key == 27:
        break

