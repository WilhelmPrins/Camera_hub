
from collections import defaultdict
from datetime import datetime
import time
import threading
import upload
import configparser
import xml.etree.ElementTree as ET

class aiTrack:

    def __init__(self, numberplate, picNumberplate, picVehicle):
        self.numberplate = numberplate
        self.picNumberplate = picNumberplate
        self.picVehicle = picVehicle
        self.createdTime = datetime.now()
        self.count = 1

    def increaseCount(self):
        self.count+=1
        self.createdTime = datetime.now()

    def upload(self):
        print ("aitrack uploaded")
        data = upload.UploadMetaData(config["Upload"]["Camera_key"])
        code, meta = data.send(self.numberplate, self.picVehicle, self.picNumberplate)
        print(f"{self.numberplate} uploaded. Code {code}")
        #print(meta)




class manageAIObjects:

    def __init__(self, expireTime):
        self.aaiobjects = defaultdict()
        self.expireTime=expireTime
        aithread = threading.Thread(target=self.cycleObjects, args=(1,))
        aithread.start()

    def addAIObject (self,aitrack):
        if aitrack.numberplate not in self.aaiobjects.keys():
            self.aaiobjects[aitrack.numberplate] = aitrack
        else:
            self.aaiobjects[aitrack.numberplate].increaseCount()
            print ("increase count " + f": {self.aaiobjects[aitrack.numberplate].count}" + f": {self.aaiobjects[aitrack.numberplate].numberplate}")

    def getAIObject (self,numberplate):
        return self.aaiobjects[numberplate]

    def update(self,aitrack):
        #print ("Update obj "+aitrack.numberplate)
        print(aitrack.count)
        if (aitrack.count == 3):
            print("uploading: ", aitrack.numberplate)
            aitrack.upload()
            del self.aaiobjects[aitrack.numberplate]


    def cycleObjects(self,name):
        while (True):
            time.sleep(0.1)
            currentTime = datetime.now()
            for aitrack in list(self.aaiobjects.values()):
                self.update(aitrack)
                age =  (currentTime - aitrack.createdTime).total_seconds()
                if (self.expireTime <= age):
                    del self.aaiobjects[aitrack.numberplate]


class Valid:
    def __init__(self):
        self.valid_types = config["valid"]["types"].split(",")
        self.manage = manageAIObjects(int(config["Timeout"]["Key_time"]))
        self.lengths = config["valid"]["lengths"].split(",")
        self.if_else = int(config["valid"]["if_else"])

    def validate(self, detection):
        for i in self.valid_types:
            if detection.numberplate[:2] == i:
                position = self.valid_types.index(i)
                if len(detection.numberplate) >= int(self.lengths[position]):
                    print("Match")
                    self.manage.addAIObject(detection)
                    break
                else:
                    pass
            elif i == self.valid_types[-1] and detection.numberplate[:2] != i:
                if len(detection.numberplate) >= self.if_else:
                    print("Match, unique")
                    self.manage.addAIObject(detection)




config = configparser.ConfigParser()
config.read("cfg/uploadSettings.ini")
valid = Valid()


