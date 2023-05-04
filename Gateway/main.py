import sys
import time
from adafruitIO import *
from uart import *


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

