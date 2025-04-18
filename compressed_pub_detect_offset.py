# use conda::base
from ultralytics import YOLO
from PIL import Image
import cv2
import numpy as np
import torch
from collections import deque
import rospy
from std_msgs.msg import Float32MultiArray
from sensor_msgs.msg import CompressedImage
from scipy.optimize import least_squares
from find_cam import find_cam
from detect_offset import compute_offset_image, process_results
import detect_light_ring
import os
from datetime import datetime
import argparse

last_mos = np.array([0, 0, 0])
CHECK_TILT = False
SAVE_CLIP = False

# Global variable for latest image frame
latest_image = None

def compressed_image_callback(msg):
    global latest_image
    # Convert CompressedImage to OpenCV image
    np_arr = np.frombuffer(msg.data, np.uint8)
    latest_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

if __name__ == "__main__":
    # Parse the robot_name argument
    parser = argparse.ArgumentParser(description="Tool Offset Publisher")
    parser.add_argument("robot_name", type=str, help="Name of the robot")
    args = parser.parse_args()
    robot_name = args.robot_name

    # Load models
    model = YOLO("models/studs-seg2.pt")
    light_ring_model = YOLO("models/lightringv2.pt")

    filtered_center = np.array([0, 0])

    if SAVE_CLIP:
        save_dir = os.path.join("saved_clips", "clip" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(save_dir, exist_ok=True)
    else:
        save_dir = None

    rospy.init_node('tool_offset_publisher', anonymous=True)

    # Dynamically set topics based on robot_name
    image_topic = f"/yk_{robot_name}/gen3_image"
    tool_offset_topic = f"/yk_{robot_name}/tool_offset"

    # Subscribers & Publishers
    rospy.Subscriber(image_topic, CompressedImage, compressed_image_callback, queue_size=1)
    tool_offset_pub = rospy.Publisher(tool_offset_topic, Float32MultiArray, queue_size=2)
    block_tilt_pub = rospy.Publisher('block_tilt', Float32MultiArray, queue_size=2)

    rate = rospy.Rate(8)
    while not rospy.is_shutdown():
        if latest_image is None:
            rospy.logwarn_throttle(5.0, "Waiting for compressed image...")
            rate.sleep()
            continue

        try:
            cv2.imshow("Latest Image", latest_image)
            offset = compute_offset_image(latest_image, model, save_visual=save_dir, visualize=True)
            cv2.waitKey(1)  # Add this line to allow OpenCV to process the window events
        except Exception as e:
            rospy.logwarn(f"Offset computation failed: {e}")
            offset = None

        # if CHECK_TILT:
        #     try:
        #         tilt = detect_light_ring.detect_lightring(latest_image, model=light_ring_model, z=30, e_center=[210, 270])
        #     except Exception as e:
        #         rospy.logwarn(f"Tilt detection failed: {e}")
        #         tilt = None

        if offset is not None:
            msg = Float32MultiArray()
            msg.data = offset
            tool_offset_pub.publish(msg)

        if CHECK_TILT and tilt is not None:
            msg = Float32MultiArray()
            msg.data = tilt
            block_tilt_pub.publish(msg)

        rate.sleep()
