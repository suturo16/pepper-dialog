#!/usr/bin/env python

import roslib
import rospy
from std_msgs.msg import String
import sys
from naoqi import ALProxy


class Synthesizer:
    def __init__(self):
        rospy.init_node('synthesizer')
        rospy.on_shutdown(self.cleanup)
        #read the parameter
        self.PEPPERIP = rospy.get_param("PEPPERIP", "192.168.101.69")
        self.PEPPERPORT = rospy.get_param("PEPPERPORT", "9559") 
        try:
	    self.tts = ALProxy("ALTextToSpeech", self.PEPPERIP, int(self.PEPPERPORT))
            #self.mic_spk = ALProxy("ALAudioDevice", self.PEPPERIP, int(self.PEPPERPORT))
	except Exception,e:
	    rospy.loginfo("Could not create proxy to ALTextToSpeech")
	    rospy.loginfo("Error was: ",e)
	try:
            #Changes the volume
            self.tts.setVolume(0.7)
        except:
            rospy.loginfo("Could not set the volume")
        # Subscribe to the message topics
        rospy.Subscriber('~message', String, self.synthesize)

       
    #synthesize msg to voice   
    def synthesize(self, msg):
        #speak
        if(self.tts!=None):
                #self.mic_spk.closeAudioInputs()
		rospy.set_param('busy',1)
		speech=msg.data.split('.')
		for i in range(len(speech)):
		    try:
		    	self.tts.say(speech[i])
	            except:
			self.tts.say('I found some problems')
		# Print the recognized words on the screen
		rospy.loginfo(msg.data)
		rospy.sleep(3)
                #self.mic_spk.openAudioInputs()
		rospy.set_param('busy',0)
        else:
            rospy.loginfo("Speech synthesis cannot be provided...")
    def cleanup(self):
        rospy.loginfo("Shutting down synthesizer node...")



if __name__=="__main__":
    
    try:
        Synthesizer()
        rospy.spin()
    except:
	pass
