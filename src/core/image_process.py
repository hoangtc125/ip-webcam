import cv2
import numpy as np
import base64
import threading


def covert_base64(img, size=(640, 360)):
    img = cv2.resize(img, size)
    retval, buffer = cv2.imencode(".jpg", img)
    img = base64.b64encode(buffer).decode("utf-8")
    return img


def convert_gray_img(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


def save_image(img, path, size=None):

    def __save(img, path, size):
        print(f'_______ init threading save image ----')
        if size is not None:
            img = cv2.resize(img, size)
        cv2.imwrite(path, img)

    t = threading.Thread(target=__save, args=(
        img,
        path,
        size,
    ))
    t.daemon = True
    t.start()


def base64_to_numpy(img_base64):
    img_converted = base64.b64decode(img_base64)
    img_converted = np.frombuffer(img_converted, dtype=np.uint8)
    img = cv2.imdecode(img_converted, flags=1)
    return img
