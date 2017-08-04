#!/usr/bin/env python
import roslib
import rospy
from std_msgs.msg import( String )

from naoqi_bridge_msgs.msg import(
    WordRecognized )
import actionlib
from dialogsystem_msgs.msg import *
from dialogsystem_msgs.srv import *


import sys
from naoqi import ALProxy
import numpy as np
import numpy.linalg as la
import numpy.random as rd
import json

class DialogManager:
    def __init__(self):
 
        ################# attributes ###########################
	self.GETGUESTINFO='GETGUESTINFO'
	self.LASTTIMEIDENTIFY='LASTTIMEIDENTIFY'
	self.ONEMORETIMEIDENTIFY='ONEMORETIMEIDENTIFY'
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
        self.contactStatusPr2=-1                           # returned status of PR2-Robot when trying to connect to it. -1 for no connection
        self.questionnaire=[]                              # Input-Output associations      
        self.dictionary=[]                                 # ordered Bag of Words as Basis of the vector space model 
        self.REQUESTFINALFAILED='REQUESTFINALFAILED'       # pr2 could not execute the task successfully after starting it
        self.MISUNDERSTANDING='MISUNDERSTANDING'           # MISUNDERSTANDING
        self.LASTSAY='I did not say anything before'       # MISUNDERSTANDING                
        self.UNKNOWNQUESTION='UNKNOWNQUESTION'             # Reaction id for unknown user inputs
        self.UNKNOWN_PARAMETER='UNKNOWNPARAMETER'           # Reaction id for unknown service parameters entered by users
        self.REQUESTFAILED='REQUESTFAILED'                 # Reaction id when impossible to provide the service
        self.REQUESTDONE='REQUESTDONE'                     # Reaction id when service completed
        self.PROCESSINGREQUESTLONG='PROCESSINGREQUESTLONG' # Reaction id when a request can be processed and pr2 is busy
        self.PROCESSINGREQUESTSHORT='PROCESSINGREQUESTSHORT' # Reaction id when a request can be processed and pr2 is idle
        self.CUTCAKE='CUTCAKE'                             # Instruction cut cake
        self.TALKSTART=':TALKSTART'                         #constants to mark begin of discussions
        self.TALKEND=':TALKEND'                             #constants to mark end  of discussions
        self.REFLECTION='please let me call the bakery'    #pause mark
        self.pub=""                                        # publisher of output to speech synthesizer
        self.corepub=''                                    # publisher to core dialog manager topics      
        
        ########## Publishers and Subscribers #####################

        rospy.init_node('dialogManager')
        rospy.on_shutdown(self.cleanup)
        #publisher to the synthesizer message topics
        self.pub = rospy.Publisher("synthetiser/message", String ,queue_size=1000)
        # Subscribe to the asr word_recognized topics
        rospy.Subscriber('speechRecognizer/word_recognized', String, self.informationRetrieval)
        # Subscribe to the rpc status topics
        rospy.Subscriber('rpc_server/status', String, self.feedback)
        #publisher to the core manager's input topics
        self.corepub = rospy.Publisher("~coreDialogBus", String,queue_size=1000 )
        # Subscribe to the core manager's output topics
        rospy.Subscriber('dialogCoreServerManager/coreDialogBus', String, self.coreOutputProcessor)
	# publish to the query topic
        self.clientpub = rospy.Publisher("~query", String ,queue_size=1000)
        # Subscribe to the rpc client query_return topic
        rospy.Subscriber('rpc_client/query_return', String, self.receiveQuery)



        ############## Dialog Management #################### 

	
	
           
    #vision and speech responder
    def informationRetrieval(self,msg):
	try: 
		#check if message type is synchronization/new user detected
		if msg.data == self.TALKSTART:
		   #start user recognition/identification
		   userid=''
		   username=''
		   cInput=':reset'
		   bot='authentify'
		   self.corepub.publish(self.TALKSTART+';'+username+';'+userid+';'+bot+';'+cInput)
		else:
		   if msg.data == self.TALKEND:
			pass
		   else:
			#send recognized words/phrase to core dialogue manager for processing
			userid=''
			username=''
			cInput=msg.data
			bot=''
			self.corepub.publish(self.SIMPLEREQUEST+';'+username+';'+userid+';'+bot+';'+cInput)
	except Exception,e:
		rospy.loginfo("DialogManager failed to process speechrecognizer's output: "+str(e))
		username=''
		userid=''
		bot='pepper'
		cInput=self.UNKNOWN_PARAMETER
		self.corepub.publish(self.ERRORREQUEST+';'+username+';'+userid+';'+bot+';'+cInput)		

			       
           
    # rpc server/pr2 responder
    def feedback(self, status):
	userid=''
	try:
		message=json.loads(status.rstrip().lstrip())
		#complete
		typ=message['return']['type'].encode('utf8').rstrip().lstrip()
		if typ=='complete':
		   userid=str(int(message['guestId'].encode('utf8').rstrip().lstrip()))
		   success=str(int(message['return']['success'].encode('utf8').rstrip().lstrip()))
		   bot='pepper'
		   username=''
		   if success=='1':
			cInput= self.REQUESTDONE
		   else:
			cInput= self.REQUESTFINALFAILED
		   #send response to ChatScript
		   self.corepub.publish(self.CUTCAKE+';'+username+';'+userid+';'+bot+';'+cInput)


	except Exception,e:
		rospy.loginfo("DialogManager failed to process rpc server's output: "+str(e))
		username=''
		bot='pepper'
		cInput=self.UNKNOWN_RETURN
		self.corepub.publish(self.ERRORREQUEST+';'+username+';'+userid+';'+bot+';'+cInput)		

		
    
           
    #on close
    def cleanup(self):
        rospy.loginfo("Shutting down dialogManager node...")

	
    #service requester from face analyzer
    def dgVsSrvSender(self,msg):
	data_out=DialogVisionMsg()
	data_out.typ='query'
	data_out.commandName=''
	data_out.userName=''
	data_out.userId=''
	data_out.accuracy=''
	flags=False
	try:
		 rospy.wait_for_service('dialogVisionService')#wait for the service
		 dialogVisionService = rospy.ServiceProxy('dialogVisionService', DialogVisionService)#create proxy 
		 return dialogVisionService(msg).data_out
		
	except Exception,e:
		rospy.logwarn(' DialogManager failed to contact FaceAnalyzer: '+str(e))
		data_out.commandName='REQUESTFAILED'
	        data_out.typ='return'
	        return DialogVisionServiceResponse(data_out).data_out

     #action requester from face analyzer
    def dgVsActSender(self,msg):
	try:
		dialogVisionAction = actionlib.SimpleActionClient('dialogVisionAction', DialogVisionActionAction)
		dialogVisionAction.wait_for_server() 
		goal = DialogVisionActionGoal()
                goal.data_in=msg
		dialogVisionAction.send_goal(goal)
	except Exception,e:
		rospy.logwarn(' DialogManager failed to contact FaceAnalyzer: '+str(e))


    #rpc client/pr2 response to query responder  
    def receiveQuery(self,msg):
	userid=''
	try:
		message=json.loads(msg.data.rstrip().lstrip())
		#setCake
		typ=message['return']['type'].encode('utf8').rstrip().lstrip()
		if typ=='setCake':
		   userid=str(int(message['guestId'].encode('utf8').rstrip().lstrip()))
		   success=str(int(message['return']['success'].encode('utf8').rstrip().lstrip()))
		   bot='pepper'
		   username=''
		   if success=='1':
			cInput= self.PROCESSINGREQUESTLONG
		   else:
			cInput= self.REQUESTFAILED
		   #send response to ChatScript
		   self.corepub.publish(self.CUTCAKE+';'+username+';'+userid+';'+bot+';'+cInput)
		else:
		   if typ=='increaseCake' or typ=='decreaseCake'  :
			   userid=str(int(message['guestId'].encode('utf8').rstrip().lstrip()))
			   success=str(int(message['return']['success'].encode('utf8').rstrip().lstrip()))
			   bot='pepper'
			   username=''
			   if success=='1':
				cInput= self.PROCESSINGREQUESTLONG
			   else:
				cInput= self.REQUESTFAILED
				#send response to ChatScript
			   self.corepub.publish(self.CUTCAKE+';'+username+';'+userid+';'+bot+';'+cInput)
		   else:
			 if typ=='getGuestInfo':
				   userid=str(int(message['guestId'].encode('utf8').rstrip().lstrip()))
				   username=str(int(message['return']['name'].encode('utf8').rstrip().lstrip()))
				   location=str(message['return']['location'].encode('utf8').rstrip().lstrip())
				   delivered=str(int(message['return']['delivered'].encode('utf8').rstrip().lstrip()))
				   total=str(int(message['return']['total'].encode('utf8').rstrip().lstrip()))
				   bot='pepper'
				   cInput= self.UPDATEUSERDATA+' '+location+' '+total+' '+delivered
				   #send response to ChatScript
				   self.corepub.publish(self.GETGUESTINFO+';'+username+';'+userid+';'+bot+';'+cInput)
				

		
	except Exception,e:
		rospy.loginfo("DialogManager failed to process rpc client's output: "+str(e))
		username=''
		bot='pepper'
		cInput=self.UNKNOWN_RETURN
		self.corepub.publish(self.ERRORREQUEST+';'+username+';'+userid+';'+bot+';'+cInput)		


    #chatscript responder
    def coreOutputProcessor(self,msg):
	userid=''
        try:
		#Identification msg
		message=msg.data.split(';')
		olduserid=str(int(message[0].rstrip().lstrip()))
		command=message[1].rstrip().lstrip()
		if command == self.IDENTIFY :
			usermessage=message[2].rstrip().lstrip()
			self.LASTSAY=usermessage
			self.pub.publish(usermessage)
			#formulate request to face analyzer
			data=DialogVisionMsg()
			data.typ='query'
			data.userId=''
			data.userName=''
			data.commandName='IDENTIFYUSER'
			data.accuracy=''
			res=self.dgVsSrvSender(data)
			if res.commandName == 'REQUESTFAILED':
				 userid=''
		                 username=''
				 
				 cInput=':reset'
					
		   		 bot='authentify'
		   		 self.corepub.publish(self.TALKSTART+';'+username+';'+userid+';'+bot+';'+cInput)
			else:
				 userid=''
		                 username=''
		   		 cInput=res.accuracy+' '+res.userName+' '+res.userId
		   		 bot='authentify'
		   		 self.corepub.publish(self.IDENTIFY+';'+username+';'+userid+';'+bot+';'+cInput)
                else:
		    #User authentification successful
                    if command == self.AUTHPASS:
			#collect photos
			username=message[2].rstrip().lstrip()
			userid=str(int(message[3].rstrip().lstrip()))
			usermessage=message[4].rstrip().lstrip()
			#send user message to synthesizer
			self.LASTSAY=usermessage
			self.pub.publish(usermessage)
			#feedback to Chatscript feedback=command;username;userid;bot;input
			bot='pepper'
			cInput=':reset'
			#save annotated images of the user
			#formulate request to face analyzer
			data=DialogVisionMsg()
			data.typ='query'
			data.userId=userid
			data.userName=username
			data.accuracy=''
			data.commandName='SAVEIMAGES'
			res=self.dgVsSrvSender(data)
			if res.commandName == 'REQUESTFAILED':
				 userid=''
		                 username=''
		   		 cInput=':reset'
		   		 bot='authentify'
		   		 self.corepub.publish(self.TALKSTART+';'+username+';'+userid+';'+bot+';'+cInput)
			else:
		   		 self.corepub.publish(self.AUTHPASS+';'+username+';'+userid+';'+bot+';'+cInput)
				 #train the model after new samples
				 data.commandName='TRAINING'
				 self.dgVsActSender(data)	
		    else:
			if command == self.SETUSERDATA:
				usermessage=message[2].rstrip().lstrip()
				self.pub.publish(usermessage)
				#set user data at introduction: this name is from perception since user not yet official
				#username=self.getNameById(olduserid)
				userid=olduserid
				bot='pepper'
				#formulate request to face analyzer
				data=DialogVisionMsg()
				data.typ='query'
				data.userId=userid
				data.userName=''
				data.commandName='GETNAMEBYID'
				data.accuracy=''
				res=self.dgVsSrvSender(data)
				if res.commandName == 'REQUESTFAILED':
					 
					 username=''
					 cInput=':reset'
					 self.corepub.publish(self.AUTHPASS+';'+username+';'+userid+';'+bot+';'+cInput)
				else:
		
					 username=res.userName
					 cInput=username+' '+userid
					 self.corepub.publish(self.SETUSERDATA+';'+username+';'+userid+';'+bot+';'+cInput)
				   	
				   
				   
			else:
                           #Misunderstanding 
			   if command == self.MISUNDERSTANDING:
				self.pub.publish(self.LASTSAY) 
		           else:
				#cake query
				if command == self.CUTCAKE:
					username=message[2].rstrip().lstrip()
					userid=str(int(message[3].rstrip().lstrip()))
					registered=message[4].rstrip().lstrip()
					ordertype=message[5].rstrip().lstrip()
                                        nberpiece=message[6].rstrip().lstrip()
				        usermessage=message[7].rstrip().lstrip()
					#send user message
					self.LASTSAY=usermessage
					self.pub.publish(usermessage)
				        if registered == self.FALSE:
					   #setCake
				           #request=[type, id, amount, name]
					   request='setCake;'+userid+';'+nberpiece+';'+username
					   self.clientpub.publish(request)
                                        else:
					   #registered=TRUE
					   if ordertype == self.DECREASE:
					      #decrease
					      #request=[type, id, amount]
					      request='decreaseCake;'+userid+';'+nberpiece
					      self.clientpub.publish(request)
				           else:
		       			      #increase
					      #request=[type, id, amount]
					      request='increaseCake;'+userid+';'+nberpiece
					      self.clientpub.publish(request)
                                        #request directly change in the user data
					#request=[type,id]
					request='getGuestInfo;'+userid
					self.clientpub.publish(request)
                                else:
				      if command == self.CLOSEUSER:
					 nberpiece=message[3].rstrip().lstrip()
                                         usermessage=message[4].rstrip().lstrip()
					 self.LASTSAY=usermessage
                                         self.pub.publish(usermessage)
					 username=''
					 userid=str(int(message[2].rstrip().lstrip()))
					 bot='pepper'
					 cInput=':reset'
					 #decrease: drop all remaining pieces before closing the user
					 #request=[type, id, amount]
					 if int(nberpiece)>0:
						 request='decreaseCake;'+userid+';'+nberpiece
						 self.clientpub.publish(request)
					 self.corepub.publish(self.CLOSEUSER+';'+username+';'+userid+';'+bot+';'+cInput)
				      else:
					 if command==self.LASTTIMEIDENTIFY:
						usermessage=message[2].rstrip().lstrip()
						self.LASTSAY=usermessage
						self.pub.publish(usermessage)
					 else:
						 #simple output from ChatScript'
						 self.LASTSAY=command
						 self.pub.publish(command)      																			         



	except Exception,e:
		rospy.loginfo("DialogManager failed to process ChatScript's output: "+str(e))
         	username=''
		bot='pepper'
		cInput=self.UNKNOWN_PARAMETER
		self.corepub.publish(self.ERRORREQUEST+';'+username+';'+userid+';'+bot+';'+cInput)


     
             

if __name__=="__main__":
    
    try:
        DialogManager()
	rospy.spin()
    except Exception,e:
        rospy.logerr(e)
