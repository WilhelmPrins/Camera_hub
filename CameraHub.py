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
import sys
import traceback


def show_image(image, title):
    #img = cv2.imread(image)
    cv2.imshow(f"{title}", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def settings():
    config = configparser.ConfigParser()
    config.read("cfg/settings.ini")
    return config


def get_output_layers(net):
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return output_layers


def detect(image, state):
    try:

        classes = []
        try:
            Width = image.shape[1]
            Height = image.shape[0]
        except:
            logging.error('Failed to draw prediction box')
            return

        if state == "big":
            weights = config["AI"]["Weights_big"]
            configuration = config["AI"]["Config_big"]
            net = cv2.dnn.readNet(weights, configuration)
            with open(config['AI']['Classes_big'], 'r') as f:
                classes = [line.strip() for line in f.readlines()]
        elif state == "number":
            weights = config["AI"]["Weights_number"]
            configuration = config["AI"]["Config_number"]
            net = cv2.dnn.readNet(weights, configuration)
            with open(config['AI']['Classes_number'], 'r') as f:
                classes = [line.strip() for line in f.readlines()]
        elif state == "ocr":
            weights = config["AI"]["Weights_ocr"]
            configuration = config["AI"]["Config_ocr"]
            net = cv2.dnn.readNet(weights, configuration)
            with open(config['AI']['Classes_ocr'], 'r') as f:
                classes = [line.strip() for line in f.readlines()]
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        scale = 0.00392

        blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)
        net.setInput(blob)

        outs = net.forward(get_output_layers(net))

        class_ids = []
        confidences = []
        x_values = []
        organized = []
        y_list = []
        w_list = []
        h_list = []
        conf_threshold = 0.5
        nms_threshold = 0.4
        firstrun = True
        cropped_images = []

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
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    x_values.append(detection[0])
                    organised = sorted(x_values)
                    corr_position = organised.index(detection[0])
                    class_ids.insert(corr_position, classes[class_id])
                    confidences.insert(corr_position, float(confidence))
                    y_list.insert(corr_position, y)
                    w_list.insert(corr_position, w)

                    if state == "big" or state == "number":
                        # image = cv2.imread(image, 1)
                        cropped_image = image[int(y):int(y)+int(h), int(x):int(x)+int(w)]
                        cropped_images.insert(corr_position, cropped_image)

        organised = sorted(x_values)
        organised, w_list, class_ids, cropped_images = filterdub(w_list, organised, cropped_images, class_ids, state)

        if len(cropped_images) > 0:
            return cropped_images, class_ids
        elif state == "ocr":
            return [], class_ids
        else:
            return [], []


    except Exception as error:
        e = traceback.format_exc()
        logging.info(e)


def filterdub(width, x_list, cropped_images, identified_ids, state):
    for x, w in zip(x_list, width):
        next_index = x_list.index(x) + 1
        if x == x_list[-1]:
            # last character
            pass
        elif x + (w * 0.5) > x_list[next_index]:
            if (x + w * 0.5 - x_list[next_index]) / w > 0.35:
                #print("indication")
                next_id = identified_ids[next_index]
                identified_ids.remove(next_id)
                x_list.remove(x_list[next_index])
                width.remove(width[next_index])
                if state != "ocr":
                    cropped_images.remove(cropped_images[next_index])
            else:
                pass
    return x_list, width, identified_ids, cropped_images


videoout = None
logging.basicConfig(format='%(asctime)s - %(message)s {%(pathname)s:%(lineno)d}', level=logging.INFO)
logging.info('Start monitoring, press q to quite')
config = settings()
frame_no = 0
# COLORS = np.random.uniform(0, 255, size=(len(classes), 3))
logging.info('Openining '+config['DEVICES']['Camera'])

sys._excepthook = sys.excepthook


def car_detect(frame):
    images, ids = detect(frame, "big")

    return images, ids


def numberplate_detect(images, j, i, frame_no):
    current = images.index(i)
    if ids[current] != "Numplate":
        numberplates, id = detect(i, "number")
        #show_image(numberplates, "title")
        return numberplates, id
    else:
        return [], []


def ocr_detect(numberplates, numberpl, frame_no):
    current = numberplates.index(numberpl)
    show_image(numberpl, "numberplate")
    confidences, ids = detect(numberplates[0], "ocr")
    final_result = "".join(ids).upper()
    return final_result


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
            # break  # if user pressed a key other than the given key the loop will break
            None

        try:
            frame_no += 1
            ret, frame = cap.read()
            #show_image(frame, "frame")
            if type(frame) != "NoneType":
                images, ids = car_detect(frame)
                if len(images) != 0:
                    for i, j in zip(images, ids):
                        if j != "Numplate":
                            numberplates, ids = numberplate_detect(images, j, i, frame_no)
                            for numberpl in numberplates:
                                if len(numberplates) == 0:
                                    pass
                                else:
                                    final_result = ocr_detect(numberplates, numberpl, frame_no)
                                    print(f"From frame {frame_no}:")
                                    print(final_result)
                        else:
                            final_result = ocr_detect(images, i, frame_no)
                            print(f"From frame {frame_no}")
                            print(final_result)


            else:
                cap = cv2.VideoCapture(config['DEVICES']['Camera'])

        except Exception as e:
            logging.exception(e)
            try:
                cap = cv2.VideoCapture(config['DEVICES']['Camera'])
            except Exception as e2:
                logging.info('Failed to re-connect')

    if (videoout is not None): videoout.release()

except Exception as e:
   # just_the_string = traceback.format_exc()
    logging.info(e)

