import logging
import configparser
import cv2
import traceback
import numpy as np

class Machine:

    def __init__(self, link):
        self.link = link
        self.config = configparser.ConfigParser()
        self.config.read(self.link)

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

    def loadState(self, state):
        self.state = state
        if state == "big":
            self.weights = self.config["AI"]["Weights_big"]
            self.configuration = self.config["AI"]["Config_big"]
            self.net = cv2.dnn.readNet(self.weights, self.configuration)

            with open(self.config['AI']['Classes_big'], 'r') as f:
                self.classes = [line.strip() for line in f.readlines()]
        elif state == "number":
            self.weights = self.config["AI"]["Weights_number"]
            self.configuration = self.config["AI"]["Config_number"]
            self.net = cv2.dnn.readNet(self.weights, self.configuration)
            # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            with open(self.config['AI']['Classes_number'], 'r') as f:
                self.classes = [line.strip() for line in f.readlines()]
        elif state == "ocr":
            self.weights = self.config["AI"]["Weights_ocr"]
            self.configuration = self.config["AI"]["Config_ocr"]
            self.net = cv2.dnn.readNet(self.weights, self.configuration)
            with open(self.config['AI']['Classes_ocr'], 'r') as f:
                self.classes = [line.strip() for line in f.readlines()]

    def detect(self, image):
        try:
            Width = image.shape[1]
            Height = image.shape[0]
        except Exception as e:
            logging.exception(e)
            return [], []
        try:
            if self.state == "big":
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
            scale = 0.00392
            #if np.all(np.array(image.shape)):
                #return [], [], [], [], [], []
            # Sometime the image are broken
            try:
                blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)
            except Exception as e:
                #logging.exception("bad quality image ")
                return  [], [], [], [], [], []

            self.net.setInput(blob)

            outs = self.net.forward(self.get_output_layers(self.net))
            class_ids = []
            confidences = []
            x_values = []
            organized = []
            y_list = []
            w_list = []
            h_list = []
            cropped_images = []


            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    #if (confidence>0): logging.info (str(class_id)+" "+str(confidence))
                    if confidence > float(self.config["VIDEO"]["confidence"]):
                        center_x = int(detection[0] * Width)
                        center_y = int(detection[1] * Height)
                        w = int(detection[2] * Width)
                        h = int(detection[3] * Height)
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)

                        x_values.append(x)
                        organised = sorted(x_values)
                        corr_position = organised.index(x)
                        class_ids.insert(corr_position, self.classes[class_id])
                        confidences.insert(corr_position, float(confidence))
                        y_list.insert(corr_position, y)
                        w_list.insert(corr_position, w)
                        h_list.insert(corr_position, h)

                        if self.state == "big" or self.state == "number":
                            # image = cv2.imread(image, 1)
                            cropped_image = image[int(y):int(y)+int(h), int(x):int(x)+int(w)]
                            cropped_images.insert(corr_position, cropped_image)

            organised = sorted(x_values)
            organised, w_list, class_ids, cropped_images, y_list, h_list = self.filterdub(w_list, organised,
                                                                                          cropped_images,
                                                                                          class_ids,
                                                                                          self.state,
                                                                                          y_list,
                                                                                          h_list)
            if len(cropped_images) > 0:
                return cropped_images, class_ids, organised, w_list, y_list, h_list
            elif self.state == "ocr" and type(class_ids) != "NoneType":
                return [], class_ids, confidences, [], [], []
            else:
                return [], [], [], [], [], []


        except Exception as error:
            e = traceback.format_exc()
            logging.info(e)
            return [], [], [], [], [], []