import cv2 as cv
from camModules.machine import Machine


def display(vid):
    vid = cv.VideoCapture(vid)
    while True:
        ret, frame = vid.read()
        width = int(frame.shape[1] * 0.75)
        length = int(frame.shape[0] * 0.75)
        if ret:
            frame = cv.resize(frame, (width, length))
            cropped_images, class_ids, x_list, w_list, y_list, h_list = machine.detect(frame, "big")
            frame = bounding_box(frame, x_list, y_list, w_list, h_list)
            cv.imshow('Frame', frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

        else:
            break
    cv.destroyAllWindows()
    vid.release()


def bounding_box(image, x_list, y_list, w_list, h_list):
    for x_val in x_list:
        position = x_list.index(x_val)
        cv.rectangle(image,
                     (x_val, y_list[position]),
                     (x_val + w_list[position], y_list[position] + h_list[position]),
                     (255, 0, 0),
                     2)
    return image


machine = Machine("cfg/settings.ini")
display("DASH_720.mp4")

