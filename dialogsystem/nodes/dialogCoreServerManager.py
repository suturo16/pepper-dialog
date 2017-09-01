#!/usr/bin/env python

import socket
import sys
import rospy
import roslib
from std_msgs.msg import String
import subprocess
import os
#Here is a client for core management of dialogue


SELF_CLIENT_SOCKET=''

class DialogCoreClientManager(object):
   def __init__(self):

        #constants to mark begin and end of discussions
	self.UNKNOWN_PERSON='UNKNOWNPERSON'
	self.GETGUESTINFO='GETGUESTINFO'
        self.SIMPLEREQUEST='SIMPLEREQUEST'
	self.ERRORREQUEST='ERRORREQUEST'
	self.UNKNOWN_RETURN='UNKNOWNRETURN'
        self.IDENTIFY='IDENTIFY'
	self.AUTHPASS='AUTHPASS'
	self.SETUSERDATA='SETUSERDATA'
	self.CUTCAKE='CUTCAKE'
	self.INCREASE='INCREASE'
	self.DECREASE='DECREASE'
	self.FALSE='FALSE'
	self.TRUE='TRUE'
	self.CLOSEUSER='CLOSEUSER'   
        self.TALKSTART=':TALKSTART'
        self.TALKEND=':TALKEND'
        self.INIT   =':INIT'
        self.USERID='-1'
	self.USERNAME=''
        rospy.init_node('dialogCoreServerManager')
        rospy.on_shutdown(self.cleanup)
        rospy.loginfo("Starting core server manager node...")
        #read the parameter
	self.pathToUserDialogData=rospy.get_param('PATH_TO_USERDIALOGDATA','../ChatScript/USERS')
        self.CORESERVERIP = rospy.get_param("CORESERVERIP", "localhost")
        self.CORESERVERPORT = int(rospy.get_param("CORESERVERPORT", "1024"))
        self.CORESERVERPATH=rospy.get_param("CORESERVERPATH", "clear")
        self.CORESERVERCWD=rospy.get_param("CORESERVERCWD", "")
        self.ADDR = (self.CORESERVERIP, self.CORESERVERPORT) 
        self.BOT='authentify'
        self.DATA_IN=' '
        self.DATA_OUT=''
        self.COMMAND=''
        #Publisher
        self.pub=rospy.Publisher('~coreDialogBus',String,queue_size=1000)
        # Subscriber
        rospy.Subscriber('dialogManager/coreDialogBus', String, self.process)
	#clean users' folder for dialog contexts
	for the_file in os.listdir(self.pathToUserDialogData):
	    file_path = os.path.join(self.pathToUserDialogData, the_file)
            if os.path.isfile(file_path):
		    os.unlink(file_path) 
        #chartscript server
        rospy.loginfo("starting core server Manager ...")
        self.SERVERPROCESS=subprocess.Popen([self.CORESERVERPATH],cwd=self.CORESERVERCWD)    
        #connection to chatscript server cd BINARIES && ./LinuxChatScript64
        #initalize the dialogue
        #rospy.sleep(10)
        #self.process(String(self.TALKSTART))

  

   def cleanup(self):
        global SELF_CLIENT_SOCKET
        rospy.loginfo("Shutting down core server manager node...")
        self.SERVERPROCESS.terminate()
        self.SERVERPROCESS.kill()
        SELF_CLIENT_SOCKET.close()

   def queryChatScript(self):
	  global SELF_CLIENT_SOCKET
	  #socket
          SELF_CLIENT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	  SELF_CLIENT_SOCKET.connect(self.ADDR)

	  #request of the user sent to server for processing
	  SELF_CLIENT_SOCKET.sendall((self.USERID+chr(0)+self.BOT+chr(0)+self.DATA_IN +chr(0))) 

	  #system's reaction
 	  ANS = SELF_CLIENT_SOCKET.recv(1024)

	  #close socket allocated for request 
	  SELF_CLIENT_SOCKET.close() 
	
	  return ANS

   def process(self,msg):
	  
          #process message from dialogmanager and forward it to ChatScript
          try:
		  #split msg and decapsulate it
		  # the format of msg.data is self.COMMAND+';'+username+';'+userid+';'+bot+';'+cInput
		  message=msg.data.split(';')

		  command=message[0].rstrip().lstrip()
		  #set commansd
		  self.COMMAND=command

		  #set username
		  self.USERNAME=message[1].rstrip().lstrip()	
		   #set bot
		  if message[3].rstrip().lstrip()!='':
			   self.BOT=message[3].rstrip().lstrip()
		 

		  if self.COMMAND==self.TALKEND:
			self.USERID=-1
			self.BOT='authentify'
			self.DATA_IN=':reset'
			self.queryChatScript()
		  else:
			  #set input
			  if self.COMMAND==self.SIMPLEREQUEST and self.USERID<0:
				  #check that ChatScript is aware of the talker
					self.COMMAND=self.ERRORREQUEST
					self.DATA_IN=self.UNKNOWN_PERSON
					self.BOT='authentify'
			  else:
										
					self.DATA_IN=message[4].rstrip().lstrip()
					if(self.DATA_IN==''):
						self.DATA_IN=' '

		          #set user id
			  #In case the process caused by chatscript or pr2 failed,use the current id to announce problem
			  # current id is never empty per reccurence
			  if message[2].rstrip().lstrip()!='':
				   self.USERID=message[2].rstrip().lstrip()
			  
	
			  #query ChatScript
		 	  self.DATA_OUT = self.queryChatScript()

			  

			  #print Inputs and Outputs of core system manager
			  if self.COMMAND==self.CLOSEUSER:
				rospy.loginfo('CORE SERVER INPUT: '+self.DATA_IN) 
			  	rospy.loginfo('CORE SERVER OUTPUT: USER '+self.USERID+' closed')
				#return control to ChatScript controller
				self.USERNAME=''
				self.USERID='-1'
				self.BOT='authentify'	
				self.DATA_IN=':reset' 
				self.queryChatScript() 
			  else:
		      	 	#publish reaction by adding the user id			
				 self.pub.publish(String(self.USERID+';'+self.DATA_OUT))
				 rospy.loginfo('CORE SERVER INPUT: '+self.DATA_IN) 
				 rospy.loginfo('CORE SERVER OUTPUT: '+self.DATA_OUT)


			  
          except Exception,e:
                  rospy.logwarn('CoreServerManager failed to send query to Chatscript: '+str(e))  
		  

	 
	  
 
  
                    

if __name__=="__main__":
    
    try:	
        DialogCoreClientManager()
	rospy.loginfo('We came here')
        rospy.spin()
    except:
	e = sys.exc_info()[0]
        rospy.loginfo("Danger: An ERROR ocurred: %s" % e)
