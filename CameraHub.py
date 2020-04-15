import cv2
import logging
from camModules.machine import Machine
from camModules import aicollection


def recta(x_list, w_list, y_list, h_list):
    for i in x_list:
        current = x_list.index(i)
        cv2.rectangle(frame,
                      (i, y_list[current]),
                      (i + w_list[current], y_list[current] + h_list[current]),
                      (255, 0, 0),
                      2)
    return frame


def car_detect(frame):
    images, ids, x_list, w_list, y_list, h_list = machine.detect(frame, "big")
    return images, ids, x_list, w_list, y_list, h_list


def rescale_frame(frame, percent=75):
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)


def numberplate_detect(image):
    images, ids, x_list, w_list, y_list, h_list = machine.detect(image, "number")
    return images, ids, x_list, w_list, y_list, h_list


def ocr_detect(numberplates, numberpl):
    total = 0
    current = numberplates.index(numberpl)
    [], ids, confidences, [], [], []  = machine.detect(numberpl, "ocr")
    for i in confidences:
        total += i
    if len(confidences) > 0:
        average = total / len(confidences) #Take longest average as correct result
    else:
        average = 0.0
    final_result = "".join(ids).upper()
    return final_result, average


try:
    machine = Machine("cfg/settings.ini")
    config = machine.settings()
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
    logging.info('Start monitoring, press q to quite')
    frame_no = 0
    logging.info('Openining ' + config['DEVICES']['Camera'])

    cap = cv2.VideoCapture(config['DEVICES']['Camera'])
    logging.info('Stream open ')
    frame_counter = 0
    recordtimer = 0

    while(True):

        try:

            frame_no += 1
            ret, frame = cap.read()
            if ret:
                frame = rescale_frame(frame,100)
                images, ids, x_list, w_list, y_list, h_list = car_detect(frame)
                frame = recta(x_list, w_list, y_list, h_list)
                for car in images:
                    n_images, n_ids, n_x_list, n_w_list, n_y_list, n_h_list = numberplate_detect(car)
                    if len(n_images) > 0:
                        for plates in n_images:
                            result, average = ocr_detect(n_images, plates)
                            newimage = aicollection.aiTrack(result, plates, car)
                            aicollection.manage.addAIObject(newimage)
                            print(result)
                    # elif len(n_images) == 0:
                    #     result = "#NONUMBERPLATE"
                    #     average = 0.0
                    #     temp_image = cv2.imread("numberplate.jpg")
                    #     newimage = aicollection.aiTrack(result, temp_image, car)
                    #     aicollection.manage.addAIObject(newimage)

                cv2.imshow("Frame", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
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
                    pass
            else:
                pass

        except Exception as e:
            logging.exception(e)

    cv2.destroyAllWindows()
    cap.release()

except Exception as e:
   # just_the_string = traceback.format_exc()
    logging.exception(e)


