#!/usr/bin/env python
import rospy
import sys
import os
from PIL import Image as PILImage
from naoqi import (ALBroker, ALProxy, ALModule)
from std_msgs.msg import( String )
from naoqi_bridge_msgs.msg import(
    WordRecognized,
    )

import cv2
import numpy as np
import cv_bridge
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import roslib


class Util:
    # Methods for name conversion
    @staticmethod
    def to_naoqi_name(name):
        return "ros{}_{}".format(
            name.replace("/", "_"),
            rospy.Time.now().to_sec() )

class RosCamera(ALModule):

	def __init__(self):
		self.webcam=None
		self.broker=None
		self.videoDevice=None
		self.mode=None
		try:
			#ros topic to publish images
			rospy.init_node('rosCamera')
		        rospy.on_shutdown(self.cleanup)
			self.pub = rospy.Publisher("~image",Image,queue_size=1)
			self.bridge = CvBridge()
			self.mode=rospy.get_param('VIDEOMODE','remote')
			if self.mode=='local':
					self.webcam=cv2.VideoCapture(0)
			else:#remote call
								#parameter reading
					self.PEPPERIP = rospy.get_param("PEPPERIP", "192.168.101.69")
					self.PEPPERPORT = int(rospy.get_param("PEPPERPORT", 9559))
					self.naoqi_name = Util.to_naoqi_name( rospy.get_name() )

					#Start ALBroker (needed by ALModule)
					self.broker = ALBroker(self.naoqi_name + "_broker",
					    "0.0.0.0",   # listen to anyone
					     0,           # find a free port and use it
					    self.PEPPERIP,          # parent broker IP
					    self.PEPPERPORT )       # parent broker port
		
					#Init superclass ALModule
					ALModule.__init__( self, self.naoqi_name )

					 # Start naoqi proxies
					self.videoDevice = ALProxy("ALVideoDevice",self.PEPPERIP,self.PEPPERPORT)

					#Install global variables needed by Naoqi
        				self.install_naoqi_globals()

					#subscribe camera
					self.naoqi_name=self.videoDevice.subscribeCamera(self.naoqi_name,0,1,13,20)

					#open camera
					self.videoDevice.openCamera(0)

					#start camera
					self.videoDevice.startCamera(0)

			rospy.loginfo('rosCameca node started successfully')
		except:
			rospy.logwarn(' RosCamera did not start properly')


	def install_naoqi_globals(self):
		try:
			globals()[self.naoqi_name] = self
		except:
			rospy.logwarn(' Failed to globalize RosCamera')

	def cleanup(self):
		rospy.logwarn('Releasing camera ...')
		if self.mode=='local':
			if self.webcam!=None:
				self.webcam.release()
				
		else:
			if self.videoDevice!=None:
				self.videoDevice.stopCamera(0)
				self.videoDevice.closeCamera(0)
				self.videoDevice.unsubscribe(self.naoqi_name)
			if self.broker!=None:
				self.broker.shutdown()
		rospy.logwarn('Shutting down rosCamera node ...')

	def run(self):
 		while not rospy.is_shutdown():
			if self.mode=='local':
				try:
					ret,img=self.webcam.read()
					if ret:
						self.pub.publish(self.bridge.cv2_to_imgmsg(img, "bgr8"))
						rospy.loginfo('rosCamera node  sent image successfully')
				except:
					rospy.logwarn('rosCamera node  failed to send image')
			else: #remote
				try:
					img=self.videoDevice.getImageRemote(self.naoqi_name)
					if img!=() and img!=[]:
						#print len(img),len(img[6]),img[6][0],img[6][1],img[6][2],img[6].decode('hex')
						img=PILImage.frombytes("RGB", (int(img[0]),int(img[1])), img[6])
						self.pub.publish(self.bridge.cv2_to_imgmsg(np.array(img,'uint8'), "rgb8"))
						rospy.loginfo('rosCamera node  sent image successfully')
				except:
					rospy.logwarn('rosCamera node  failed to send image')
			rospy.sleep(3) #3 periods per second


if __name__=="__main__":
    
    try:
        RosCamera().run()
    except:
        rospy.logwarn('Shutting down rosCamera node ...')


