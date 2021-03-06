#!/usr/bin/env python
import rospy
import sys
import os
from PIL import Image
from naoqi import (ALBroker, ALProxy, ALModule)
from std_msgs.msg import( String )
from naoqi_bridge_msgs.msg import(
    WordRecognized,
    )
import actionlib
from dialogsystem_msgs.msg import *
from dialogsystem_msgs.srv import *

import cv2
import numpy as np
import cv_bridge
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import roslib
import mutex
import utility as u
 
class FaceDetector(object):
	def __init__(self,cascadeFile):
		try:
			self.cascadeFile=cascadeFile#trained parameters of Haarcascade algorithim
			self.faceCascade=cv2.CascadeClassifier(self.cascadeFile)#load detector
			self.currentImage=''
			rospy.loginfo('Face detection started successfully')
		except Exception,e:
			rospy.logwarn('Failed to load the Haar classifier. Please check the cascade xml-file '+str(self.cascadeFile))
			
	def detectFace(self,imageFile,outputfile,scale,mn,ms,typ):
		self.rec=[]
		if typ=='COMPRESSED':
				self.currentImage=imageFile
		else:
				self.currentImage='current raw image'
		try:    
			if typ=='COMPRESSED':
				self.currentImage=imageFile
				self.colorImage=cv2.imread(self.currentImage)
			else:
				self.colorImage=imageFile
			if(len(self.colorImage.shape)>2):
				self.grayImage=cv2.cvtColor(self.colorImage,cv2.COLOR_BGR2GRAY)
			else:
				self.grayImage=self.colorImage.copy()
			self.rl=[]
			self.lw=[]
			self.faces,self.rl,self.lw = self.faceCascade.detectMultiScale3(self.grayImage,
                                                      scaleFactor=scale,minNeighbors=mn,minSize=ms,
                                                      flags = 0,outputRejectLevels=True)#detect all possible faces
			
			rospy.loginfo('Found: '+str(len(self.faces))+' faces!')
			
			
			if(len(self.faces)>0):
				j=list(self.lw).index(max(self.lw))
				(x,y,width,height)=self.faces[j]
				self.rec=self.grayImage[y: y + height, x: x + width]
				cv2.rectangle(self.colorImage, (x, y), (x+width, y+height), (0, 255, 0), 2)
				cv2.putText(self.colorImage, str(self.lw[j]), (x,y),
                                            cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 2.5, (0, 255, 0), 1, cv2.LINE_AA)
			cv2.imwrite(outputfile,self.colorImage)#only for system supporting display function
			rospy.loginfo('Face detection terminated successfully')
				
		except Exception,e:
			rospy.logwarn('Failed to detect Image. Please check the image file '+self.currentImage+str(e))
		return np.array(self.rec,dtype='uint8')
			




class FaceRecognizer(object):

	def __init__(self):
		try:

			#ros node
			rospy.init_node('faceAnalyzer')
			rospy.on_shutdown(self.cleanup)
                        self.cvSynchronizer=mutex.mutex()
			self.cvSynchImage=mutex.mutex()
			self.cvSynchImage.testandset()
			#lock model for training
			self.cvSynchronizer.testandset()
			#create utilities
			self.ut=u.Utility(None)
			#actions and services
			#service server to handle dialogManager's requests
			self.dgVsSrv=rospy.Service('dialogVisionService',DialogVisionService,self.dgVsSrvHandler)
			#action server to handle long dialogManager's requests such as online facerecognition Training
			self.dgVsAct=actionlib.SimpleActionServer('dialogVisionAction',DialogVisionActionAction,self.dgVsActHandler,False)
			self.dgVsAct.start()

			#subscribers
			self.sub = rospy.Subscriber("rosCamera/image",Image,self.imageBuffering)

			#parameters
			self.cvReset=rospy.get_param('CVRESET','off')
			self.pathToDataset=rospy.get_param('PATH_TO_DATASET','../data/facerecognition/faces')
			self.pathToDetection=rospy.get_param('PATH_TO_DETECTION','../data/facerecognition/detection')
			self.pathToDetector=rospy.get_param('PATH_TO_DETECTOR','../data/facerecognition/haarcascade_frontalface_default.xml')
			self.cvThreshold=float(rospy.get_param('CVTHRESHOLD','0.0'))
			self.cvRthreshold=float(rospy.get_param('CVRTHRESHOLD','25000.0'))
			self.cvDimension=int(rospy.get_param('CVDIMENSION','80')) 
			self.cvFaceWindow=int(rospy.get_param('CVFACEWINDOW','30')) 
			self.cvNeighbor=int(rospy.get_param('CVNEIGHBOR','6')) 
			self.cvScale=float(rospy.get_param('CVSCALE','1.06'))
	  		self.cvScanFrequency=int(rospy.get_param('CVSCANFREQUENCY','5'))
			self.cvInstanceFrequency=int(rospy.get_param('CVINSTANCEFREQUENCY','3'))
                      	self.cvIdimensionDefault=int(rospy.get_param('CVIDIMENSIONDEFAULT','150'))
			self.cvIdimension=int(rospy.get_param('CVIDIMENSION',self.cvIdimensionDefault))

		        
			#attributes
			self.cvImageBuffer=[]
			self.INDEX=-1
			self.INSTANCEINDEX=0
			if rospy.get_param('VIDEOMODE','remote')=='remote':
				self.cvMode='rgb8'
			else:
				self.cvMode='bgr8'
			for i in range(self.cvScanFrequency):
				self.cvImageBuffer.append(None)
                     	self.total=0
			self.success=0
			self.currentImage=[]#current image
			#create folders for online record of faces and detection
			try:
				if not os.path.exists(self.pathToDetection):
	    				os.makedirs(self.pathToDetection)
				if not os.path.exists(self.pathToDataset):
	    				os.makedirs(self.pathToDataset)
			except Exception,e:
				rospy.logwarn('Failed to create folders for online record of faces and detection: '+str(e))
			self.bridge = CvBridge()
			self.facerec=cv2.face.createEigenFaceRecognizer()
			self.facedec=FaceDetector(self.pathToDetector)
			if(self.cvReset=='off'):
		          for the_file in os.listdir(self.pathToDataset):
				    file_path = os.path.join(self.pathToDataset, the_file)
			            if os.path.isfile(file_path):
					    os.unlink(file_path)     
			#pretraining
			imt,lt,imtt,ltt=self.loadDataset(self.pathToDataset,self.pathToDetection)
			self.train(imt,lt)
			self.predictMany(imtt,ltt)
			rospy.loginfo('Total: '+str(self.total)+', Success: '+str(self.success))
			rospy.loginfo('Init of face recognizer successful')
			
		except Exception,e:
			rospy.logwarn('Face recognizer not startet properly: '+str(e))
		#unlock model
		self.cvSynchronizer.unlock()
		self.cvSynchImage.unlock()

	def train(self,images,labels):
		try:
			self.facerec.train(images,np.array(labels,dtype='int'))
			rospy.loginfo('Training of face recognizer successful')
		except:
			rospy.logwarn('Failed to train model')		
		
	def loadDataset(self,pathToDataset,pathToDetection):
		 images =[]
		 labels=[]
		 tests=[]
		 testlabels=[]
		 meanSize=0.0
		 i=0
		 try:
			 for f in os.listdir(pathToDataset):
				i+=1
				if not False:
			
					rec=self.facedec.detectFace(os.path.join(pathToDataset,f),
		                                                    os.path.join(pathToDetection,str(i)+'.jpg'),
                                                                    self.cvScale,self.cvNeighbor,
                                                                     (self.cvFaceWindow,self.cvFaceWindow),'COMPRESSED')
					self.total+=1
					if len(rec)!=0:
						 self.success+=1
						 meanSize=meanSize+rec.shape[0]*rec.shape[1]
						 label = int(f.split('_')[1])
						 instance=int(f.split('_')[2].split('.')[0])
						 if not (instance>0 and instance%4==0):#1/5 ofdataset for training
							 images.append(rec.copy())
							 labels.append(label)
						 else:
							 tests.append(rec.copy())
							 testlabels.append(label)
			 meanSize=int(np.sqrt(meanSize/(len(labels)+len(testlabels))))
			 rospy.loginfo('Loading of dataset for training successful')
		 except:
		 	rospy.logwarn('Failed to load dataset')
		 self.cvIdimension=meanSize
		 return (self.resize(images,self.cvIdimension),labels,self.resize(tests,self.cvIdimension),testlabels)


	def predictMany(self,images,labels):
		pred=[]
		try:
			for i in range(len(images)):
				pred.append(self.predict(images[i]))
				rospy.loginfo('class: '+str(pred[i][0])+', conf: '+str(pred[i][1]))
                                if labels!=[]:
					rospy.logwarn('Expected: '+str(labels[i]))
			rospy.loginfo('Multiple prediction successful')
		except:
			rospy.logwarn('Failed to predict many')
		return pred

	def predict(self, image):
  		try:
			pred=self.facerec.predict(image)
			rospy.loginfo('Single prediction successful')
			return pred
			
		except:
 			rospy.logwarn('Failed to predict one')
			return []

	def resize(self,images,meanSize):
		normImages=[]
		try:		
			for i in range(len(images)):
				if(images[i].shape[0]*images[i].shape[1]<meanSize*meanSize):
					normImages.append(np.array(cv2.resize(images[i].copy(),(meanSize,meanSize),
		                                          interpolation=cv2.INTER_LINEAR),dtype='uint8'))#enlarge
				else:
					normImages.append(np.array(cv2.resize(images[i].copy(),(meanSize,meanSize),
		                                          interpolation=cv2.INTER_AREA),dtype='uint8'))#shrink
			rospy.loginfo('Resizing of images successful')
		except:
			rospy.logwarn('Failed to normalize/resize dataset')
		return normImages

	def addImages(self,path,image, name, idname,instance,extension):
		try:
			idname=str(idname)
			instance=str(instance)
			fullname=os.path.join(path,name+'_'+idname+'_'+instance+'.'+extension)
			cv2.imwrite(fullname,image)
			rospy.loginfo('Insertion of training images successful')
			return True
		except:
			rospy.logwarn(' Failed to add images into database')
			return False
				
	def getNextId(self,pathToDataset):
		nid=-1
		try:
			images=os.listdir(pathToDataset)
			for i in images:
				if int(i.split('_')[1])>nid:
					nid=int(i.split('_')[1])
			rospy.loginfo('New ID successful')
		except:
			rospy.logwarn(' Failed to provide new ID for face identification')
			return -1
                return nid+1

	def getNameById(self,pathToDataset,nid):
		name=''
		try:
			images=os.listdir(pathToDataset)
			for i in images:
				if int(i.split('_')[1])==nid:
					return str(i.split('_')[0])
			rospy.loginfo('Retrieval of name by ID successful')
		except:
			rospy.logwarn('Failed to provide face name flltered by ID ')
		
                return name

	def getNextInstance(self,pathToDataset,nid,name):
		instance=-1
		try:
			images=os.listdir(pathToDataset)
			for i in images:
				if int(i.split('_')[1])==nid and str(i.split('_')[0])==name:
					if int(i.split('_')[2].split('.')[0])>instance:
						instance=int(i.split('_')[2].split('.')[0])
			rospy.loginfo('Retrieval of instance by name and ID successful')
		except:
			rospy.logwarn(' Failed to provide new face instance  flltered by ID and name')
		 	return -1
                return instance+1

	def captureImage(self):
		img=[]
		try:
			img=np.array(self.currentImage,dtype='uint8').copy()
			self.currentImage=[]
			rospy.loginfo('Image capture successful')
		except:
			rospy.logwarn(' Failed to capture image')
		return img
	
	def imageBuffering(self,image):
		while(not self.cvSynchImage.testandset()):
			rospy.sleep(0.1)
		try:
                        self.INDEX+=1
			self.INDEX%=self.cvScanFrequency
			self.currentImage = self.bridge.imgmsg_to_cv2(image, self.cvMode)
			self.cvImageBuffer[self.INDEX]=self.currentImage.copy()




                       


			rospy.loginfo('Buffering of current image successful')
		except:
			rospy.logwarn(' Failed to buffer image')

		self.cvSynchImage.unlock()
       
           
	def dgVsActHandler(self,msg):
		#lock the model before training to avoid corrupted prediction meanwhile
		while(self.cvSynchronizer.testandset()):
			rospy.sleep(0.1)
		try:
			if msg.data_in.commandName == 'TRAINING':
				#train face recognition model
				imt,lt,imtt,ltt=self.loadDataset(self.pathToDataset,self.pathToDetection)
				self.train(imt,lt)
				self.predictMany(imtt,ltt)
				rospy.loginfo('Total: '+str(self.total)+', Success: '+str(self.success))
				rospy.loginfo('Init of face recognizer successful')
			self.dgVsAct.set_succeeded()
		except Exception,e:
			rospy.logwarn(' Failed to train model requested by dialog manager')
		#unlock the model
		self.cvSynchronizer.unlock()

	def dgVsSrvHandler(self,msg):
	    data_out=DialogVisionMsg()
	    data_out.typ='return'
	    data_out.commandName=''
	    data_out.userName=''
	    data_out.userId=''
	    data_out.accuracy=''
	    flags=False
	    try:
		if msg.data_in.commandName == 'GETNAMEBYID':
			data_out.commandName='GETNAMEBYID'
			nid=int(msg.data_in.userId)
			data_out.userId=str(nid)
			data_out.userName=self.getNameById(self.pathToDataset,nid)
			data_out.accuracy=msg.data_in.accuracy
		else:
			if msg.data_in.commandName == 'SAVEIMAGES' :
				data_out.commandName='SAVEIMAGES'
				if self.cvImageBuffer[0] == None:
					raise Exception('Image buffer empty')
				else:
					img=self.cvImageBuffer[0].copy()
					for i in range(1,self.cvScanFrequency):
						if self.cvImageBuffer[i]!=None:
							img+=self.cvImageBuffer[i]
						else:
							img+=self.cvImageBuffer[0]
					img/=self.cvScanFrequency
					nid=int(msg.data_in.userId)
					data_out.userId=str(nid)
					data_out.accuracy=msg.data_in.accuracy
					img=np.array(img,dtype='uint8')
					name=msg.data_in.userName
					data_out.userName=name
					extension='jpg'
					nberfailed=0
					for i in range(self.cvInstanceFrequency):
						instance=self.getNextInstance(self.pathToDataset,nid,name)
						if(not self.addImages(self.pathToDataset,img.copy(),name,nid,instance,extension)):
							nberfailed+=1
					if nberfailed==self.cvInstanceFrequency:
						raise Exception('FaceAnalyzer failed to save images of current user')
			
			else:
				if msg.data_in.commandName=='IDENTIFYUSER':
					found=False
					max_iter=90
					#lock model while predicting to avoid conflict with parallel training
					if(not self.cvSynchronizer.testandset()):
						raise Exception('CONFLICT_PREDICTION_TRAINING')
					flags=True#mark that we lock model
					data_out.commandName='IDENTIFYUSER'
					if self.cvImageBuffer[0] == None:
						raise Exception('Image buffer empty')
					else:
						while (not found) and max_iter>0:
							img=np.array(self.cvImageBuffer[0].copy(),dtype='uint')
							for i in range(1,self.cvScanFrequency):
								if self.cvImageBuffer[i]!=None:
									img+=self.cvImageBuffer[i]
								else:
									img+=self.cvImageBuffer[0]
							img/=self.cvScanFrequency
							img=np.array(img,dtype='uint8')
							#face detection
							self.INSTANCEINDEX+=1
							img=self.facedec.detectFace(img,
				                                                    os.path.join(self.pathToDetection,str(self.INSTANCEINDEX)+'.jpg'),
		                                                                    self.cvScale,self.cvNeighbor,
		                                                                    (self.cvFaceWindow,self.cvFaceWindow),'UNCOMPRESSED')
							#check if face detection succeded
							if(len(img)==0):#failed
								max_iter-=1
							else:
								found=True
								break	
							if max_iter<=0:
								raise Exception('FaceAnalyzer failed to detect face on images of current user')
						#normalize image
						if self.cvIdimension <=0.0:
							rospy.set_param('CVIDIMENSION',self.cvIdimensionDefault)
							self.cvIdimension=rospy.get_param('CVIDIMENSION',self.cvIdimensionDefault)
					        [img]=self.resize([img],self.cvIdimension)
						#face recognition
						result=self.predict(img)
						if result==[]:
							#failed to recognize. No model available
							data_out.accuracy='unknownperson'
							data_out.userName='unknownname'
							data_out.userId=str(self.getNextId(self.pathToDataset))	
						else:
						        [label,score]=result
							#evaluation
							if score <= self.cvThreshold:
								data_out.accuracy='knownperson'
								data_out.userName=self.getNameById(self.pathToDataset,int(label))
								data_out.userId=str(label).rstrip().lstrip()
							else:
								if score <= self.cvRthreshold:
									data_out.accuracy='notwellknownperson'
									data_out.userName=self.getNameById(self.pathToDataset,int(label))
									userId1=str(label).rstrip().lstrip()
									userId2=str(self.getNextId(self.pathToDataset))
									data_out.userId=str(self.ut.compress(int(userId1),int(userId2)))
									
								else:
									data_out.accuracy='unknownperson'
									data_out.userName='unknownname'
									data_out.userId=str(self.getNextId(self.pathToDataset))
						
	    except Exception,e:
		rospy.logwarn(' FaceAnalyzer failed to process message from DialogManager: '+str(e))
		data_out.commandName='REQUESTFAILED'
	    #unlock model anyway
	    if flags:
	    	self.cvSynchronizer.unlock()	    
	    return DialogVisionServiceResponse(data_out)
        
	def cleanup(self):
		rospy.logwarn('Shutting down faceAnalyzer node ...')	




if __name__=="__main__":
    
    try:
        FaceRecognizer()
	rospy.spin()
    except:
        rospy.logwarn('Shutting down faceAnalyzer node ...')
