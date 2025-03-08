#use conda::base
from ultralytics import YOLO
from PIL import Image
import cv2
import time
import numpy as np
import torch
from collections import deque
last_mos = np.array([0,0])
last_mos_queue = deque(maxlen=10)
def process_results2(results):
    transform = np.array([0.01, 0.01, 1])
    global last_mos
    if len(results) == 1:
        result = results[0]
        if not (results[0].keypoints.conf is None):
            mid_of_studs = results[0].keypoints.xy[0,1,:]
            mid_of_studs_conf = results[0].keypoints.conf[0,1]
            last_mos = 0.8 * last_mos + 0.2 * np.array(mid_of_studs.to('cpu'))
            output = np.zeros(3)
            output[:2] = last_mos
            output[2] = mid_of_studs_conf.cpu().item()
            #output = output @ transform.T
            print("center: ", last_mos, "with confidence", mid_of_studs_conf.cpu().item())
        else:
            print("no lego keypoints detected")
            output = np.zeros(3)
        
        return output
    

def process_results(results):
    transform = np.array([0.01, 0.01, 1])
    global last_mos_queue
    
    if len(results) == 1:
        result = results[0]
        if not (results[0].keypoints.conf is None):
            mid_of_studs = results[0].keypoints.xy[0, 1, :]
            mid_of_studs_conf = results[0].keypoints.conf[0, 1]
            
            # Convert the new measurement to CPU and append to the queue
            new_measurement = np.array(mid_of_studs.to('cpu'))
            last_mos_queue.append(new_measurement)
            
            # Compute the rolling average
            rolling_average = np.mean(np.array(last_mos_queue), axis=0)

            output = np.zeros(3)
            output[:2] = rolling_average
            output[2] = mid_of_studs_conf.cpu().item()

            print("center: ", rolling_average, "with confidence", mid_of_studs_conf.cpu().item())
        else:
            print("no lego keypoints detected")
            output = np.zeros(3)
        
        return output
    else:
        print("No results to process or unexpected input.")
        return np.zeros(3)
    

def compute_offset(camera, model, fx = 1000 , fy = 1000, z = 30.0):
    '''
    Arguments: 
    camera to read from, and yolo keypoint model to use
    camera focal and depth in mm. Assume cx, cy are at image center, and assume fixed z
    Outputs:
    [x,y,confidence] if detected, None otherwise
    '''
    ret, og_frame = camera.read()
    if ret:
        h, w, c = og_frame.shape
    else:
        print("read frame file")
        return None
    start_w = (w - 480) // 2
    end_w = start_w + 480

    # Crop the middle section
    og_frame = og_frame[:, start_w:end_w, :]
    results = model.predict(og_frame, show = True, verbose = False)
    output = process_results(results)
    output[:2] -= np.array([210,270])#diff from center
    output[:2] *= z
    output[:2] /= np.array([fx, fy])
    if output[2] > 0.7:
        return output[:2] / 1000 #mm to meter
    else:
        return None

model = YOLO("studs_keypoints.pt")
camera = cv2.VideoCapture(4)
filtered_center = np.array([0,0])

# Set the loop rate (e.g., 10 Hz)
while True:
    # Get the detected offset
    offset = compute_offset(camera, model)
    print(offset)


    

              
     


# model = YOLO("yolov8n.pt")


while True:
    
    ret, og_frame = camera.read()
    h, w, c = og_frame.shape

# Calculate the start and end points for the width dimension to get the middle 480 pixels
    start_w = (w - 480) // 2
    end_w = start_w + 480

    # Crop the middle section
    og_frame = og_frame[:, start_w:end_w, :]
    results = model.predict(og_frame, show = True, verbose = False)
    process_results(results)
        # light_ring = results[0].boxes[0]
        # box = light_ring.xyxy[0]  # x1, y1, x2, y2 format
        # x1, y1, x2, y2 = map(int, box)
        # confidence = light_ring.conf.item()
        # cv2.rectangle(og_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green box
        #                 # Put confidence text
        # cv2.putText(og_frame, f'{confidence:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
                    
    # t0 = time.perf_counter()
    
    # print("infer time:", time.perf_counter() - t0)
    