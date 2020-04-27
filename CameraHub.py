import cv2
import logging
import os
import sys

import keyboard
from imutils import auto_canny

from camModules.machine import Machine
from camModules import aicollection
from imutils.video import FileVideoStream
from imutils.video import FPS
import time


def processNumberplate(image):
    n_images, n_ids, n_x_list, n_w_list, n_y_list, n_h_list = numberplate.detect(image)

    if len(n_images) > 0:

        for plates in n_images:
            total = 0
            current = n_images.index(plates)
            [], ids, confidences, [], [], [] = ocr.detect(plates)

            plate = ""
            for i in range(0, len(confidences) - 1):
                total += confidences[i]
                plate = plate + '%.2f ' % confidences[i]

            if len(confidences) > 0:
                average = total / len(confidences)  # Take longest average as correct result
            else:
                average = 0.0
            result = "".join(ids).upper()
            # logging.info("Numberplate " + result + " " + plate + "Avr: " + str(average))
            if (average > float(config['VIDEO']['ocr'])):
                logging.info("Numberplate " + result + " " + plate + "Avg: " + str(average))
                return result, plates
            else:
                result = "lowquality"
                return result, plates
    return "noplate",[]



try:
    bigObject = Machine("cfg/settings.ini")
    bigObject.loadState("big")
    managequeue = aicollection.manageAIObjects(6)
    numberplate = Machine("cfg/settings.ini")
    numberplate.loadState("number")

    ocr = Machine("cfg/settings.ini")
    ocr.loadState("ocr")

    config = ocr.config
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
    logging.info('Start monitoring, press q to quit')
    frame_no = 0
    logging.info('Openining ' + config['DEVICES']['Camera'])

    fvideo = FileVideoStream(config['DEVICES']['Camera']).start()
    time.sleep(1.0)
    fps = FPS().start()
    logging.info('Stream open ')
    frame_counter = 0
    recordtimer = 0

    while(True):

        try:
            frame_no += 1
            frame = fvideo.read()
            #if keyboard.is_pressed('q'):
            #    break

            if (len(frame)>0):

                #print("frame " + str(frame_no))
                width = int(frame.shape[1] * 75 / 100)
                height = int(frame.shape[0] * 75 / 100)
                dim = (width, height)
                cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
                images, ids, x_list, w_list, y_list, h_list = bigObject.detect(frame)
                for image in images:
                    result, plate = processNumberplate(image)
                    if (result != "lowquality" and result !="noplate"):
                        newimage = aicollection.aiTrack(result, plate, image)
                        if (aicollection.valid.validate(newimage)):
                            logging.info("Validated... ")
                            managequeue.addAIObject(newimage)

            else:
                logging.error("Bad connection, restarting")
                python = sys.executable
                os.execl(python, python, *sys.argv)

           # cv2.imshow("Frame", frame)
           # cv2.waitKey(1)
            fps.update()


        except Exception as e:
            logging.exception(e)
            logging.error("Bad connection, exit")
            break

    cv2.destroyAllWindows()
    fvideo.stop()
    fps.stop()
    logging.info("elasped time: {:.2f}".format(fps.elapsed()))
    logging.info("approx. FPS: {:.2f}".format(fps.fps()))

except Exception as e2:
    logging.exception(e2)


