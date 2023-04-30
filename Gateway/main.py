import subprocess

try:
    import sys
except ImportError:
    subprocess.check_call(['pip', 'install', 'sys'])
try:
    import time
except ImportError:
    subprocess.check_call(['pip', 'install', 'time'])
try:
    import keyboard
except ImportError:
    subprocess.check_call(['pip', 'install', 'keyboard'])

from yolov5.detect import *
from adafruitIO import *
from uart import *

weight_path = 'weights/mask_yolov5.pt'
ai_data = LoadModel(weights=weight_path, source='0')

controller1 = Controller('STM')
controller2 = Controller('STM')
controllers = [controller1, controller2]
feed_payload["system-button"] = "1"  # If there is no internet connection, system will run by default
while True:
    EnsureConnection()
    for controller in controllers:
        if feed_payload['system-button'] == "1":
            controller.setEnable(True)
        elif feed_payload['system-button'] == "0":
            controller.setEnable(False)

    controller1.ReadData(period=10, sensorType=TEMP_HUMID)
    controller2.ReadData(period=10, sensorType=MQ9)

    if feed_payload['system-button'] == "1":
        labels_data, frame = RunDetect(ai_data, conf_thres=0.5, hide_conf=True)
        payload = ""
        if len(labels_data):
            payload = labels_data[0][0]
            if payload == "with_mask":
                payload = "Đeo khẩu trang"
            elif payload == "without_mask" or payload == "mask_weared_incorrect":
                payload = "Không đeo khẩu trang"
        else:
            payload = "Không có người"
        feed_payload['face-mask-detector-ai'] = payload
        SendDatawithPeriod(feed_name='face-mask-detector-ai', payload=payload, period=5)
