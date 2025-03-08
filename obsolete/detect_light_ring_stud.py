#use conda::base
from ultralytics import YOLO
from PIL import Image
import cv2
import time
import numpy as np


def find_center(xyxy):
    img_center = [240,240]
    h_lim = [30,300]
    w_lim = [30,300]
    ratio_lim = 1.8
    center_tolerance = 100

    x1, y1, x2, y2 = map(int, xyxy)
    h, w = (x2-x1, y2-y1)
    cx, cy = ((x1 + x2)/2, (y1 + y2)/2)

    if h < h_lim[0] or h > h_lim[1]:
         return None
    if w < w_lim[0] or w > w_lim[1]:
         return None
    if w/h > ratio_lim or h/w > ratio_lim:
         return None
    return np.array([cx - img_center[0], cy - img_center[1]])
def check_centered(cxcy):
    offset = np.array([36,-36])
    tol = np.array([10,10])
    xy = cxcy + offset
    if abs(xy[0]) > tol[0]:
        print("x tilt by ", xy[0])
    if abs(xy[1]) > tol[1]:
        print("y tilt by ", xy[1])
    if abs(xy[0]) <= tol[0] and abs(xy[1]) <= tol[1]:
        print("No Tilt")
    

    

              
     


# model = YOLO("yolov8n.pt")
model = YOLO("lightring_stud.pt")
camera = cv2.VideoCapture(4)
while True:
    
    ret, og_frame = camera.read()
    h, w, c = og_frame.shape

# Calculate the start and end points for the width dimension to get the middle 480 pixels
    start_w = (w - 480) // 2
    end_w = start_w + 480

    # Crop the middle section
    og_frame = og_frame[:, start_w:end_w, :]
    results = model.predict(og_frame, show = False, verbose = False, device = 'cpu')
    if len(results[0].boxes) > 0:
        # light_ring = results[0].boxes[0]
        # box = light_ring.xyxy[0]  # x1, y1, x2, y2 format
        # x1, y1, x2, y2 = map(int, box)
        # confidence = light_ring.conf.item()
        # cv2.rectangle(og_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green box
        #                 # Put confidence text
        # cv2.putText(og_frame, f'{confidence:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        for detection in results[0].boxes:  # Accessing the detections
            confidence = detection.conf.item()
            if confidence > 0.6:
                box = detection.xyxy[0]  # x1, y1, x2, y2 format
                x1, y1, x2, y2 = map(int, box)  # Convert to integers for OpenCV
                # Draw the rectangle on the original frame
                if detection.cls.item() == 0:
                    cv2.rectangle(og_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green box
                    # Put confidence text
                    cv2.putText(og_frame, f'{confidence:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                else:
                    cv2.rectangle(og_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Green box
                    # Put confidence text
                    cv2.putText(og_frame, f'{confidence:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                # center = find_center(detection.xyxy[0])
                
                # if center is not None:
                #     print(center)
                #     check_centered(center)
                    
    # t0 = time.perf_counter()
    
    # print("infer time:", time.perf_counter() - t0)
    cv2.imshow("Detections", og_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
            break