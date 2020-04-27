
from collections import defaultdict
from datetime import datetime
import time
import threading
import upload
import configparser
import xml.etree.ElementTree as ET
import logging
import re

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
        logging.info ("ready to uploaded")
        data = upload.UploadMetaData(config["Upload"]["Camera_key"])
        code, meta = data.send(self.numberplate, self.picVehicle, self.picNumberplate)

        if (code==200):  logging.info ("Uploaded, Success")
        else:  logging.info ("Uploaded, Failed with code: "+str(self.numberplate))
        if (code==504):
            logging.error("Gateway Timeout - please investigate. Error "+str(code))



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
            logging.info ("increase count " + f": {self.aaiobjects[aitrack.numberplate].count}" + f": {self.aaiobjects[aitrack.numberplate].numberplate}")

    def getAIObject (self,numberplate):
        return self.aaiobjects[numberplate]

    def update(self,aitrack):
        #print ("Update obj "+aitrack.numberplate)
        #print("Detection count "+aitrack.count+" "+aitrack.numberplate)


        if (aitrack.count >=  3):
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


def detection(args):
    pass


class Valid:
    def __init__(self):
        self.valid_types = config["valid"]["types"].split(" ")
        self.valid_regex = config["valid"]["regex"].split(" ")
        self.regex_else = config["valid"]["else_regex"]
        self.manage = manageAIObjects(int(config["Timeout"]["Key_time"]))


    def regcheck(self,reg, plate):
        result = re.fullmatch(reg, plate)
        if (result): return True
        else: return False


    def validate(self, detection):
        matched = False
        for type in self.valid_types:
            if detection.numberplate[:len(type)] == type:
                position = self.valid_types.index(type)
                return self.regcheck(self.valid_regex[position],detection.numberplate)
        if (matched==False):
            return self.regcheck(self.regex_else, detection.numberplate)


config = configparser.ConfigParser()
config.read("cfg/uploadSettings.ini")

#ai = aiTrack("C123412","","")
valid = Valid()
#print(valid.validate(ai))


