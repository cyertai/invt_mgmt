#!/usr/bin/python
"""
NOTE: missing shebang line will cause mouse-grab
"""

import os
import sys
import pdb
import time
import yaml
import argparse

import numpy as np
import cv2

import rospy
from sensor_msgs.msg import CameraInfo, Image
from cv_bridge import CvBridge
import camera_info_manager as cim
from std_msgs.msg import String

cvRos = CvBridge()


class rpiCameraPublisher(object):

    def __init__(self, cam_name='head_camera', cam_id=3):
        print('hello')
        # node_name = rospy.get_param('/camera_frame')
        call_space = rospy.get_namespace()
        param_dict = rospy.get_param(call_space)
        node_name='camera_node'
        node_param = param_dict[node_name]
        ###########
        cam_id = int(node_param['video_device'][-1]) #camera_param['video_device'][-1]
        camera_frame_id = node_param['camera_frame_id']
        calib_url = node_param['calib_url']
        frame_rate = node_param['framerate']
        ###########
        self.IMAGE_PUBLISHER = rospy.Publisher('image_raw' , Image, queue_size=1)
        self.INFO_PUBLISHER = rospy.Publisher('camera_info', CameraInfo, queue_size=1)
        ###########
        rospy.init_node('%s' % node_name)

        self.cam_name = node_name
        self.frame_id = camera_frame_id
        self.cam_id = cam_id
        self.calib_url = calib_url
        self.cam_capture = None
        self.cam_info = cim.CameraInfoManager(cname=self.cam_name, url=self.calib_url)
        self.cam_info.loadCameraInfo()
        #self.param_dict = node_param
        self.framerate = frame_rate
        # clean release
        rospy.on_shutdown(self.cleanRelease)
        # publisher
        self.publishCameraImage()

        rospy.spin()

    def publishCameraImage(self):
        self.cam_capture = cv2.VideoCapture(self.cam_id)
        flag, img = self.cam_capture.read()
        while not rospy.is_shutdown():
            flag, img = self.cam_capture.read()
            if flag:
                # self.cam_info.loadCameraInfo()
                ros_img_msg = cvRos.cv2_to_imgmsg(img, encoding="bgr8")
                ros_img_msg.header.frame_id = self.frame_id
                current_cam_info = self.cam_info.getCameraInfo()
                current_cam_info.header.frame_id = self.frame_id

                publish_time = rospy.Time.now()
                current_cam_info.header.stamp = publish_time
                ros_img_msg.header.stamp = publish_time

                self.IMAGE_PUBLISHER.publish(ros_img_msg)
                self.INFO_PUBLISHER.publish(current_cam_info)

            time.sleep(1.0/self.framerate)

    def cleanRelease(self):
        print('INITIATING CLEAN SHUTDOWN')
        if self.cam_capture is not None:
            if self.cam_capture.isOpened():
                print('releasing camera')
                self.cam_capture.release()
            else:
                print('no cameras attached to release')
        return


if __name__ == "__main__":

    k = rpiCameraPublisher()
