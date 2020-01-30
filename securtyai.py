#############################################
# Object detection via RTSP - YOLO - OpenCV
# Author : Frank Schmitz   (Dec 11, 2018)
# Website : https://www.github.com/zishor
############################################

import os
import os.path
import cv2
import numpy as np
import imageio
import datetime
import keyboard
import time
import configparser
import datetime
import logging

counter = 0
imageio.plugins.ffmpeg.download()
detectedobjects = []


def settings():
    config = configparser.ConfigParser()
    config.read("cfg/settings.ini")
    return config

def get_output_layers(net):
    
    layer_names = net.getLayerNames()
    
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    return output_layers

def save_image(image, class_id, confidence, x, y, x_plus_w, y_plus_h):
    global counter
    label = str(classes[class_id])


    dirname = os.path.join("output", label, datetime.datetime.now().strftime('%Y-%m-%d'))
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    filename = label + '_' + datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S_%f') + '_c_' + "{:.2f}".format(confidence) + '.jpg'
    draw_prediction(image, class_id, confidence, x, y, x_plus_w,y_plus_h)
    cv2.imwrite(os.path.join(dirname, filename), image)


    if (counter>3):
        time.sleep(3)
        counter=0
    else:
        counter+=1

def save_video(image):
    global videoout, videoname
    dirname = os.path.join("output", datetime.datetime.now().strftime('%Y-%m-%d'))
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    filename =  datetime.datetime.now().strftime('%Y-%m-%d_%H_video') + '.avi'
    if (videoout is  None):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        logging.info("videout is NONE")
        h, w, _ = image.shape
        videoout = cv2.VideoWriter(os.path.join(dirname, filename), fourcc, 20.0, (w, h))
    else:
        if (videoname!=filename):
            videoout.release()
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            h, w, _ = image.shape
            videoout = cv2.VideoWriter(os.path.join(dirname, filename), fourcc, 20.0, (w, h))

    videoname = filename
    videoout.write(image)





def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    label = str(classes[class_id])
    color = COLORS[class_id]
    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 3)
    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 3)

def detect(framenum, image, recordtimer):
    Width=0
    Height=0
    try:
        Width = image.shape[1]
        Height = image.shape[0]
    except:
        logging.error('Failed to draw prediction box')
        return


    scale = 0.00392
    
    net = cv2.dnn.readNet(config["AI"]["weights"], config["AI"]["Config"])
    blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)
    
    net.setInput(blob)
    
    outs = net.forward(get_output_layers(net))

    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.5
    nms_threshold = 0.4
    firstrun = True

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > float(config["VIDEO"]["confidence"]):
                center_x = int(detection[0] * Width)
                center_y = int(detection[1] * Height)
                w = int(detection[2] * Width)
                h = int(detection[3] * Height)
                x = center_x - w / 2
                y = center_y - h / 2
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])
                if (str(classes[class_id]) in config["VIDEO"]["detect"]):
                    if (recordtimer >= round(time.time() * 1000)):
                        firstrun = False
                    else:
                        firstrun = True

                    recordtimer = round(time.time()*1000)+1000

                    logging.info(str(classes[class_id])+' ('+str(round(confidence*100,0))+'% x:'+str(x)+' y:'+str(y)+' w:'+str(w)+' h:'+str(h))

   # detectedobjects.append([framenum,class_ids])

    
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    orgImage = image.copy()
    for i in indices:
        i = i[0]
        box = boxes[i]
        x = box[0]
        y = box[1]
        w = box[2]
        h = box[3]
        draw_prediction(orgImage, class_ids[i], confidences[i], round(x), round(y), round(x + w), round(y + h))
        if (firstrun==True):
            save_image(orgImage, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))

    dorecord = round(recordtimer - round(time.time() * 1000))

    if (dorecord>=0):
      #  print ("timer " + str(round(dorecord)))
        save_video(orgImage)
    return image, recordtimer

    
# Doing some Object Detection on a video
classes = None
videoout = None
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

logging.info('Start monitoring, press q to quite')
config = settings()
with open(config['AI']['Classes'], 'r') as f:
    classes = [line.strip() for line in f.readlines()]

COLORS = np.random.uniform(0, 255, size=(len(classes), 3))
logging.info('Openining '+config['DEVICES']['Camera'])
try:
    cap = cv2.VideoCapture(config['DEVICES']['Camera'])
    logging.info('Stream open ')

    frame_counter = 0
    recordtimer = 0
    while(True):

        try:  # used try so that if user pressed other than the given key error will not be shown
            if keyboard.is_pressed('q'):  # if key 'q' is pressed
                logging.info('Bye bye!')
                break  # finishing the loop
        except:
            break  # if user pressed a key other than the given key the loop will break

        try:
            ret, frame = cap.read()
            frame_counter= frame_counter+1
            if np.shape(frame) != ():
                frame, recordtimer = detect(frame_counter,frame,recordtimer)
            else:
                cap = cv2.VideoCapture(config['DEVICES']['Camera'])
                logging.error('No frame')
               # cap = cv2.VideoCapture(config['DEVICES']['Camera'])

        except Exception as e:
            logging.error(e)
            try:
                cap = cv2.VideoCapture(config['DEVICES']['Camera'])
            except Exception as e2:
                logging.info('Failed to re-connect')

    if (videoout is not None): videoout.release()

except Exception as e:
    logging.error(e)

