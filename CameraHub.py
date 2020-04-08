#############################################
# Object detection via RTSP - YOLO - OpenCV
# Author : Frank Schmitz   (Dec 11, 2018)
# Website : https://www.github.com/zishor
############################################

import cv2
import logging
import sys
from camModules.machine import Machine


def car_detect(frame):
    images, ids, x_list, w_list, y_list, h_list = machine.detect(frame, "big")
    return images, ids, x_list, w_list, y_list, h_list


def rescale_frame(frame, percent=75):
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)


def numberplate_detect(images, j, i, frame_no):
    current = images.index(i)
    if ids[current] != "Numplate":
        numberplates, id = machine.detect(i, "number")
        #show_image(numberplates, "title")
        return numberplates, id
    else:
        return [], []


def ocr_detect(numberplates, numberpl, frame_no):
    total = 0
    current = numberplates.index(numberpl)
    #show_image(numberplates[0], "numberplate")
    cropped, ids, confidences = machine.detect(numberpl, "ocr")
    for i in confidences:
        total += i
    if len(confidences) > 0:
        average = total / len(confidences) #Take longest average as correct result
    else:
        average = 0
    final_result = "".join(ids).upper()
    return final_result, average


try:
    machine = Machine("cfg/settings.ini")
    config = machine.settings()
    videoout = None
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
    logging.info('Start monitoring, press q to quite')
    frame_no = 0
    # COLORS = np.random.uniform(0, 255, size=(len(classes), 3))
    logging.info('Openining ' + config['DEVICES']['Camera'])

    sys._excepthook = sys.excepthook
    cap = cv2.VideoCapture(config['DEVICES']['Camera'])
    logging.info('Stream open ')
    frame_counter = 0
    recordtimer = 0

    while(True):

        try:

            frame_no += 1
            ret, frame = cap.read()
            if ret:
                if type(frame) != "NoneType":
                    rescale_frame(frame, 50)
                    images, ids, x_list, w_list, y_list, h_list = car_detect(frame)
                    for i in x_list:
                        current = x_list.index(i)
                        cv2.rectangle(frame,
                                      (i,y_list[current]),
                                      (i + w_list[current], y_list[current] + h_list[current]),
                                      (255,0,0),
                                      2)
                    cv2.imshow("Frame", frame)
                    if cv2.waitKey(50) & 0xFF == ord('q'):
                        break


                    # if len(images) != 0:
                    #     for i, j in zip(images, ids):
                    #         logging.info("Car!")
                    #         show_image(i, "Car")
                    #         numberplates, ids = numberplate_detect(images, j, i, frame_no)
                    #         for numberpl in numberplates:
                    #             if len(numberplates) == 0:
                    #                 pass
                    #             else:
                    #                 final_result, average = ocr_detect(numberplates, numberpl, frame_no)
                    #                 print(f"From frame {frame_no}:")
                    #                 print(final_result)
                    #                 print(f"Average: {average}")

                else:
                    cap = cv2.VideoCapture(config['DEVICES']['Camera'])
            else:
                cap = cv2.VideoCapture(config['DEVICES']['Camera'])

        except Exception as e:
            logging.exception(e)
            try:
                cap = cv2.VideoCapture(config['DEVICES']['Camera'])
            except Exception as e2:
                logging.info('Failed to re-connect')
    cv2.destroyAllWindows()
    cap.release()

except Exception as e:
   # just_the_string = traceback.format_exc()
    logging.exception(e)


