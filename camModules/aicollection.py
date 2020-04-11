
from collections import defaultdict
from datetime import datetime
import time
import threading

class aiTrack:

    def __init__(self, numberplate, picNumberplate, picVehicle):
        self.numberplate = numberplate
        self.picNumberplate = picNumberplate
        self.picVehicle = picVehicle
        self.createdTime = datetime.now()
        self.count = 1

    def increaseCount(self):
        self.count+=1

class manageUploads:

    def upload(self,aiTrack):
        print ("aitrack uploaded")

class manageAIObjects:

    def __init__(self, expireTime):
        self.manageUpload = manageUploads()
        self.aaiobjects = defaultdict()
        self.expireTime=expireTime
        aithread = threading.Thread(target=self.cycleObjects, args=(1,))
        aithread.start()

    def addAIObject (self,aiTrack):
        if aiTrack.numberplate not in self.aaiobjects.keys():
            self.aaiobjects[aiTrack.numberplate] = aiTrack
        else:
            self.aaiobjects[aiTrack.numberplate].increaseCount()
            print ("increase count "+str(aiTrack.count))

    def getAIObject (self,numberplate):
        return self.aaiobjects[numberplate]

    def update(self,aitrack):
        #print ("Update obj "+aitrack.numberplate)
        if (aitrack.count == 3):
            print("uploading: ", aitrack.numberplate)
            self.manageUpload.upload(aitrack)


    def cycleObjects(self,name):
        while (True):
            time.sleep(1)
            currentTime = datetime.now()
            for aitrack in list(self.aaiobjects.values()):
                self.update(aitrack)
                age =  (currentTime - aitrack.createdTime).total_seconds()
                if (self.expireTime <= age):
                    del self.aaiobjects[aitrack.numberplate]
                    time.sleep(1)


manage = manageAIObjects(5)


