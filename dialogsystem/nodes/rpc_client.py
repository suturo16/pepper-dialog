#!/usr/bin/env python


import roslib
import rospy
import xmlrpclib

from std_msgs.msg import( String )

from naoqi_bridge_msgs.msg import(
    WordRecognized )
import sys
from naoqi import ALProxy
import numpy as np
import numpy.linalg as la
import numpy.random as rd
import json
class Client(object):
      def __init__(self):
	 #parameters
	 rospy.init_node('rpc_client')
	 rospy.on_shutdown(self.cleanup)
	 self.PR2IP=str(rospy.get_param('PR2IP','192.168.101.123'))
	 self.PR2PORT=str(rospy.get_param('PR2PORT','37936'))
         
	 try:
            #publisher to the query_return topics towards dialogManager
           self.pub = rospy.Publisher("~query_return", String ,queue_size=1000)
           # Subscribe to the dialogManager string topic
           rospy.Subscriber('dialogManager/query', String, self.sendQuery)
           
	   print(self.PR2IP,self.PR2PORT)
           self.client = xmlrpclib.ServerProxy('http://'+self.PR2IP+':'+self.PR2PORT+"/RPC2")
	   rospy.logwarn('connection successful')
         except Exception,e:
	   self.client=None
           rospy.logwarn(str(e))
           rospy.logwarn('The new pr2 addresses are:'+str(rospy.get_param('PR2IP','127.0.0.1'))+' and '+str(rospy.get_param('PR2PORT','8000')))
      


      def sendQuery(self,msg):
	   #msg.data=id:name:...
	   self.pub.publish(self.setter(msg.data.split(';')))

      def test(self):
	          i=-1
		  while True:
			  self.PR2IP=str(rospy.get_param('PR2IP','192.168.101.123'))
	                  self.PR2PORT=str(rospy.get_param('PR2PORT','37936'))
			  print self.PR2PORT,self.PR2IP
			#try:
			  i%=6
			  i+=1
			  request=[["setCake","0",5,"Franklin"],["setCake","1",5,"Georg"],["getAllGuestInfos","All"],["getGuestInfo","0"],["decreaseCake","1",2],["increaseCake","0",7],["getAllGuestInfos","All"]]
			  print(self.setter(request[i]))
			  #print(self.client.cutCake("cake"))
			  rospy.sleep(2)
                        #except Exception,e:
		        #  rospy.logerr("Failed client: "+str(e))
	  

      def getGuestInfo(self,guestId):
	  try:
		res=self.client.getGuestInfo(str(guestId))
		rospy.logwarn("Request GetGuestInfo to PR2 successfull")
	  except Exception,e:
		res=None
		rospy.logwarn("Request GetGuestInfo to PR2 failed: "+str(e))
	  return res

      def getAllGuestInfos(self,status):
          status="all"
	  try:
		res=self.client.getAllGuestInfos(str(status))
		rospy.logwarn("Request GetAllGuestInfos to PR2 successfull")
	  except Exception,e:
		res=None
		rospy.logwarn("Request GetAllGuestInfos to PR2 failed: "+str(e))
	  return res

      #on close
      def cleanup(self):
        rospy.loginfo("Shutting down rpc_client node...")
    
      def setter(self,request):
	   if(len(request)>0):
		#request[0]=type
		if(request[0]=='setCake'):
                   #request=[type, id, amount, name]
		  
			finalrequest='{"guestId":"'+str(request[1]) +'","query":{"type":"'+str(request[0])+'","amount":'+str(request[2])+ ',"guestName":"'+str(request[3])+'"}}'
                else:
                   if(request[0]=='increaseCake'):
		   #request=[type, id, amount]
		       
			   finalrequest='{"guestId":"'+str(request[1])+'","query":{"type":"'+str(request[0])+'","amount":'+str(request[2])+'}}'
                   else:
                        if(request[0]=='decreaseCake'):
                        #request=[type, id, amount]
			 
			   finalrequest='{"guestId":"'+str(request[1])+'","query":{"type":"'+str(request[0])+'","amount":'+str(request[2])+'}}'
			else:
		                if(request[0]=='setLocation'):
		                #request=[type, id, value/location]
				 
			           finalrequest='{"guestId":"'+str(request[1])+'","query":{"type":"'+str(request[0])+'","value":"'+str(request[2])+'"}}'
				else:
					if(request[0]=='getGuestInfo'):
						#request=[type,id]
						return self.getGuestInfo(request[1])
					else:
						if(request[0]=='getAllGuestInfos'):
							#request=[type,status]
							return self.getAllGuestInfos(request[1])

		try:    
			rospy.loginfo('Pass json')
		        finalrequest=json.dumps(json.loads(finalrequest))
			rospy.loginfo('Pass json')
			res= self.client.assertDialogElement(finalrequest)
			rospy.loginfo('Pass rpc')
			rospy.logwarn("Request to PR2 successful.")
		except Exception,e:
			rospy.logwarn("Request to PR2 failed: \n Request:"+finalrequest+' - '+str(e))
			res=None
		
           else:	  
	  	rospy.logwarn("Empty request to PR2 failed.")
	  	res=None
	   return res

if __name__=="__main__":
    
    try:
        Client()
        #Client().test()
	rospy.spin()
    except Exception,e:
        rospy.logerr(e)
