import logging
import configparser
import cv2
import traceback
import numpy as np


class Machine:

    def __init__(self, link):
        self.link = link

    def settings(self):
        config = configparser.ConfigParser()
        config.read(self.link)
        return config

    def get_output_layers(self, net):
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        return output_layers

    def filterdub(self, width, x_list, cropped_images, identified_ids, state, y_list, h_list):
        for x, w in zip(x_list, width):
            next_index = x_list.index(x) + 1
            if x == x_list[-1]:
                # last character
                pass
            elif x + w > x_list[next_index]:
                if (x + w - x_list[next_index]) / w > 0.25:
                    # print("indication")
                    next_id = identified_ids[next_index]
                    identified_ids.remove(next_id)
                    x_list.remove(x_list[next_index])
                    width.remove(width[next_index])
                    y_list.remove(y_list[next_index])
                    h_list.remove(h_list[next_index])

                    if state != "ocr":
                        cropped_images.remove(cropped_images[next_index])
                else:
                    pass
        return x_list, width, identified_ids, cropped_images, y_list, h_list

    def detect(self, image, state):

        config = self.settings()

        try:
            Width = image.shape[1]
            Height = image.shape[0]
        except Exception as e:
            logging.exception(e)
            return [], []
        try:

            classes = []
            config = self.settings()
            logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

            if state == "big":
                weights = config["AI"]["Weights_big"]
                configuration = config["AI"]["Config_big"]
                net = cv2.dnn.readNet(weights, configuration)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
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

            scale = 0.00392

            blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)
            net.setInput(blob)

            outs = net.forward(self.get_output_layers(net))

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

                        x_values.append(x)
                        organised = sorted(x_values)
                        corr_position = organised.index(x)
                        class_ids.insert(corr_position, classes[class_id])
                        confidences.insert(corr_position, float(confidence))
                        y_list.insert(corr_position, y)
                        w_list.insert(corr_position, w)
                        h_list.insert(corr_position, h)

                        if state == "big":
                            # image = cv2.imread(image, 1)
                            cropped_image = image[int(y):int(y)+int(h), int(x):int(x)+int(w)]
                            cropped_images.insert(corr_position, cropped_image)
                        elif state == "number":
                            cropped_image = image[int(y):int(y) + int(h), int(x):int(x) + int(w)]
                            cropped_images.insert(corr_position, cropped_image)

            organised = sorted(x_values)
            organised, w_list, class_ids, cropped_images, y_list, h_list = self.filterdub(w_list, organised,
                                                                                          cropped_images,
                                                                                          class_ids,
                                                                                          state,
                                                                                          y_list,
                                                                                          h_list)
            if len(cropped_images) > 0:
                return cropped_images, class_ids, organised, w_list, y_list, h_list
            elif state == "ocr" and type(class_ids) != "NoneType":
                return [], class_ids, confidences, [], [], []
            else:
                return [], [], [], [], [], []


        except Exception as error:
            e = traceback.format_exc()
            logging.info(e)
            return [], [], [], [], [], []