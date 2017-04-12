import os
import sys
import pdb
import time
import yaml

import numpy as np
import cv2

import rospy
from sensor_msgs.msg import CameraInfo
from sensor_msgs.msg import Image
from cv_bridge import CvBridge as cvros


IMAGE_PUBLISHER = rospy.Publisher('image', Image, queue_size=1)
INFO_PUBLISHER = rospy.Publisher('camera_info', CameraInfo, queue_size=1)

def buildCameraInfoMsg(calib_dict):
    cam_info = CameraInfo()
    cam_info.distortion_model = calib_dict['distortion_model']
    cam_info.K = calib_dict['K']
    return cam_info

def publishUSBCam(cam_id=0, calib_file=None, fps=10):
    rospy.init_node('rpi_usb_cam')
    if calib_file is None:
        raise ValueError("no calibration data file provided")
    with f=open(calib_file):
        calib_data = yaml.load(f)

    cam_info = buildCameraInfoMsg(calib_data)
    v = cv2.VideoCapture(cam_id)
    wait_time = 1.0/fps

    while True:
        flag, img = v.read()
        if flag:
            ros_img = cvros.cv2_to_imgmsg(img, encoding='bgr8')
            IMAGE_PUBLISHER.publish(ros_img)
            INFO_PUBLISHER.publish(cam_info)
        else:
            pass # publish nothing

        time.sleep(wait_time)

