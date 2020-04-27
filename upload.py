import requests
from io import StringIO
from io import BytesIO
from shutil import copyfile
from datetime import datetime
import xml.etree.ElementTree as ET
import numpy as np
import cv2
from PIL import Image
import logging

class UploadMetaData:

    def __init__(self, camera_key):
        self.camera_key = camera_key
        logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

    def send(self, numberplate, vehicle_image, numberplate_image):

        is_success, vehicle_buf_arr = cv2.imencode(".jpg", vehicle_image)
        is_success, num_buf_arr = cv2.imencode(".jpg", numberplate_image)
        byte_vehicle = vehicle_buf_arr.tobytes()
        byte_num = num_buf_arr.tobytes()


        metainfo = str(open('anpr.xml', 'r').read())
        metainfo = metainfo.replace("##NUMBERPLATE##", numberplate)
        metainfo = metainfo.replace("##DATETIME##", str(datetime.now()))


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

        if (response.status_code==200): logging.info ("Uploaded done: "+numberplate)
        else: logging.error ("Uploaded, Failed with error "+response.status_code)

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