import requests
from io import StringIO
from io import BytesIO
from shutil import copyfile
from datetime import datetime
import xml.etree.ElementTree as ET
import numpy as np
import cv2
from PIL import Image

class UploadMetaData:

    def __init__(self, camera_key):
        self.camera_key = camera_key
    def send(self, numberplate, vehicle_image, numberplate_image):
        # cv2.imwrite(f"{numberplate}.jpg", numberplate_image)
        # cv2.imwrite(f"{numberplate}vehicle.jpg", vehicle_image)

        is_success, vehicle_buf_arr = cv2.imencode(".jpg", vehicle_image)
        is_success, num_buf_arr = cv2.imencode(".jpg", numberplate_image)
        byte_vehicle = vehicle_buf_arr.tobytes()
        byte_num = num_buf_arr.tobytes()

        # fvehicle_image = BytesIO()
        # fvehicle_image.write(vehicle_image)
        # fvehicle_image.seek(0)
        #
        # fnumberplate_image = BytesIO()
        # fnumberplate_image.write(numberplate_image)
        # fnumberplate_image.seek(0)

        metainfo = str(open('anpr.xml', 'r').read())
        metainfo = metainfo.replace("##NUMBERPLATE##", numberplate)
        metainfo = metainfo.replace("##DATETIME##", str(datetime.now()))


        # to be replaced - not good code
        # tree = ET.parse("anpr.xml")
        # root = tree.getroot()
        # root[4].text = str(datetime.now())
        # root[8][0] = str(numberplate)
        # tree.write("ianpr.xml")
        # metainfo = str(open('anpr.xml', 'r').read())
        #####

        fanpr = StringIO()
        fanpr.write(metainfo)
        fanpr.seek(0)


        multipart_form_data = {
            'anpr.xml': ("anptr.xml", fanpr),
            'detectionPicture.jpg': ('detectionPicture.jpg', byte_vehicle),
            'licensePlatePicture.jpg': ('licensePlatePicture.jpg', byte_num)
            }

        response = requests.post('http://165.0.58.129/post/v2/'+self.camera_key, files=multipart_form_data)

        fanpr.close()
        # fnumberplate_image.close()
        # fvehicle_image.close()
        return response.status_code, metainfo


#
# vehicle_image = open('CA221947vehicle.jpg','rb').read()
# numberplate_image = open('CA221947.jpg','rb').read()
# data = UploadMetaData("6zNkpmpd5YUFYtN2")
#
# code = data.send("CA221947",vehicle_image,numberplate_image)
#
# if (code==200): print ("Uploaded, Success")
# else: print ("Uploaded, Failed")