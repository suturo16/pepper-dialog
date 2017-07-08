#!/usr/bin/env python
import paramiko
import rospy
import roslib
from std_msgs.msg import String
import utility as u
import  paramiko.client as pc
import subprocess
# Sphinx-based ASR



class AsrSphinx:
   def __init__(self):
      try:
        rospy.init_node('sphinx_asr')
        self.client=None
        self.confirmation="0"
        rospy.on_shutdown(self.cleanup)
        rospy.loginfo("Starting gstreamer sphinx asr...")
        #read the parameter
        self.INDEX = rospy.get_param("INDEX", "1")
        self.NBTHREADS = rospy.get_param("NBTHREADS", "4")
        self.BEAMSIZE = rospy.get_param("BEAMSIZE", "3") 
        self.HOST = rospy.get_param("HOST", "localhost")
        self.PORT = rospy.get_param("PORT", "7000")
        self.RPCPORT = rospy.get_param("RPCPORT", "8000")
        self.DATAPATH = rospy.get_param("DATAPATH", "demo")
        self.ASRPATH= rospy.get_param("ASRPATH", "pocketsphinx_continuous")
        self.ASRCWD=rospy.get_param("ASRCWD", "/home/franklin/Desktop/sut/src/pocketsphinx")
        self.TRESHOLD=rospy.get_param("TRESHOLD", "-10000")
        self.HMM=rospy.get_param("HMM", "model/en-us-adapt")
        self.MLLR=rospy.get_param("MLLR", "model/mllr_matrix")
        rospy.loginfo("Parameters loaded in sphinx asr node...")
        self.ASRPROCESS=subprocess.Popen([self.ASRPATH,str(self.INDEX),str(self.NBTHREADS),str(self.BEAMSIZE),str(self.HOST),str(self.PORT),str(self.DATAPATH),str(self.ASRCWD),str(self.RPCPORT),str(self.TRESHOLD),str(self.HMM),str(self.MLLR)],cwd=self.ASRCWD)   
        rospy.loginfo("Started in sphinx asr node...") 
        self.sleep()
      except:
        rospy.loginfo("Error in sphinx asr node...") 
  

   def cleanup(self):
        if self.ASRPROCESS!=None:
           self.ASRPROCESS.terminate()
           self.ASRPROCESS.kill()
        rospy.loginfo("Shutting down sphinx asr node...")
      
   def sleep(self):
        while not rospy.is_shutdown():
              rospy.sleep(10)
 
   
if __name__=="__main__":
   AsrSphinx()
       
