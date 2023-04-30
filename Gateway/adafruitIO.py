import subprocess
import time
import requests

try:
    from Adafruit_IO import MQTTClient, Client, Dashboard
except ImportError:
    subprocess.check_call(['pip', 'install', 'adafruit-io'])
try:
    import sys
except ImportError:
    subprocess.check_call(['pip', 'install', 'sys'])

try:
    import numpy as np
except ImportError:
    subprocess.check_call(['pip', 'install', 'numpy'])

try:
    import ping3
except ImportError:
    subprocess.check_call(['pip', 'install', 'ping3'])

AIO_USERNAME = "USER_NAME"
AIO_KEY = "AIO_KEY"

feed_available = False
send_startTime = 0
send_TimeOut = 1500
MAX_FAIL = 3

aio = Client(AIO_USERNAME, AIO_KEY)
feeds = None
client = MQTTClient(AIO_USERNAME, AIO_KEY)
feeds_to_publish = {}
feeds_to_subscribe = {}
feed_timer = {}
feed_payload = {}

ControlBuffer = {}

connecting = False
needToCheckConnection = True
connectReqIsSent = False


def setSendStartTime(current_time):
    global send_startTime
    send_startTime = current_time


def connected(client):
    global feed_available
    global connecting
    global needToCheckConnection
    global connectReqIsSent
    global timeCalculator
    global feeds
    global aio
    print("Ket noi thanh cong ...")
    connecting = True
    needToCheckConnection = False
    feeds = aio.feeds()
    get_feed_by_kw('sensor', feeds_to_publish, feed_timer)
    get_feed_by_kw('ai', feeds_to_publish, feed_timer)
    subscribe_feed_by_kw("button", feeds_to_subscribe)
    subscribe_feed_by_kw("sensor", feeds_to_subscribe)
    subscribe_feed_by_kw("ai", feeds_to_subscribe)
    getLastValue(feeds_to_subscribe)
    timeCalculator.setEnable()
    feed_available = True
    connectReqIsSent = False


def subscribe_feed_by_kw(keyword, buffer):
    for feed in feeds:
        name = str(feed.name)
        if keyword in name:
            client.subscribe(feed.key)
            buffer[name] = feed.key


def subscribe(client, userdata, mid, granted_qos):
    print("Subscribe thanh cong ...")


def disconnected(client):
    print("Ngat ket noi ...")


def message(client, feed_id, payload):
    global needToCheckConnection
    global send_TimeOut
    # print("Nhan du lieu: ", payload, ", feed id: ", feed_id)
    print("Nhan du lieu: ", payload, ", feed id: ", feed_id, " at", str(time.perf_counter()))
    if feeds_to_subscribe['system-button'] == feed_id:
        processSystemButton(payload)
    else:
        feed_names = list(ControlBuffer.keys())
        for feed_name in feed_names:
            if feeds_to_publish[feed_name] == feed_id:
                # Calculate RTT
                feedRTT = duration(ControlBuffer[feed_name].startTime)
                timeCalculator.UpdateTimerParam(feedRTT)
                send_TimeOut = timeCalculator.getSuggestedTimeOut()
                print("New time out:", str(send_TimeOut))
                ###############
                print("Remove from control buffer")
                ControlBuffer.pop(feed_name)
                if len(feed_names) == 1:
                    needToCheckConnection = False
                break


def processSystemButton(payload):
    global needToCheckConnection
    feed_payload['system-button'] = payload
    needToCheckConnection = False


def get_feed_by_kw(kw, buffer, timer_buffer):
    for feed in feeds:
        name = str(feed.name)
        if kw in name:
            buffer[name] = str(feed.key)
            timer_buffer[name] = time.perf_counter()


def duration(start_time):
    current_time = time.perf_counter()
    if current_time < start_time:
        return (current_time + (sys.float_info.max - start_time)) * 1000
    return (current_time - start_time) * 1000


def getLastValue(feedBuffer):
    response = requests.get(HTTPContent())
    if response.ok:
        data = response.json()
        for name in feedBuffer:
            for feedInfo in data:
                if feedInfo['name'] == name:
                    feed_payload[name] = feedInfo['last_value']
                    break


def HTTPContent():
    return "https://io.adafruit.com/api/v2/MrMPTM/feeds/" + "?x-aio-key=" + AIO_KEY


def SendDatawithPeriod(feed_name, payload, period, qos=0):
    global client
    global feed_timer
    if not feedAvaiable() or not adafruitIsConnected():
        return
    start_time = feed_timer[feed_name]
    if duration(start_time) >= period * 1000:
        feed_timer[feed_name] = time.perf_counter()
        client.publish(feeds_to_publish[feed_name], payload, qos=qos)
        print("Publishing value", payload, "to", feed_name, " at:", str(time.perf_counter()))
        raiseAttention(feed_name)


def SendData(feed_name, qos=0):
    global client
    if not feedAvaiable() or not adafruitIsConnected():
        return
    client.publish(feeds_to_publish[feed_name], feed_payload[feed_name], qos=qos)
    # print("Publishing value", feed_payload[feed_name], "to", feed_name)
    print("Publishing value", feed_payload[feed_name], "to", feed_name, " at:", str(time.perf_counter()))
    raiseAttention(feed_name)


def feedAvaiable():
    return feed_available


def adafruitIsConnected():
    global connecting
    return connecting


def raiseAttention(feed_name):
    global send_startTime
    global needToCheckConnection
    send_startTime = time.perf_counter()
    if feedAvaiable():
        AddToControlBuffer(feed_name, send_startTime)
    needToCheckConnection = True


def EnsureConnection():
    global connecting
    global client
    global feed_available
    global send_startTime
    global connectReqIsSent
    global needToCheckConnection
    global timeCalculator
    global ControlBuffer
    response_time = True
    if not needToCheckConnection:
        return
    feedToProcess = getTimeOutFeed()
    if len(feedToProcess) > 0 or duration(send_startTime) >= send_TimeOut:
        print("TIME OUT")
        # Check internet connection first
        response_time = ping3.ping("google.com")
        if response_time is False:
            # There is no wifi, the connection to adafruitIO must be disconnected too
            setDisConnectState()
            feed_payload["system-button"] = "1"
            return
        elif connecting is False:  # There is internet connection but there is no connection to adafruitIO -> Connect
            if connectReqIsSent:  # If connect message is sent, wait for it
                return
            print("Try to connect to adafruitIO")
            client.connect()
            client.loop_background()
            connectReqIsSent = True
        elif connecting is True and feedAvaiable():  # The problem cause by packet lost
            for feed_name in feedToProcess:
                timeCalculator.UpdateTimerParam(duration(feedToProcess[feed_name].startTime))  # Widen timeout interval
                client.publish(feeds_to_publish[feed_name], feed_payload[feed_name])
                print("Re-publishing value", feed_payload[feed_name], "to", feed_name)
                raiseAttention(feed_name)
                # Decrease time to live
                ControlBuffer[feed_name].DecreaseTimeToLive()
                if ControlBuffer[feed_name].isDead():
                    ControlBuffer.pop(feed_name)


def setDisConnectState():
    global connecting
    global feed_available
    global client
    global ControlBuffer
    global timeCalculator
    connecting = False
    feed_available = False
    client.setDisConnect()
    ControlBuffer.clear()
    timeCalculator.setDisabled()


def getTimeOutFeed():
    timeoutbuffer = {}
    for feed_name in ControlBuffer:
        if duration(ControlBuffer[feed_name].startTime) < send_TimeOut:
            continue
        timeoutbuffer[feed_name] = ControlBuffer[feed_name]
    return timeoutbuffer


class feedController:
    def __init__(self, payload, max_fail, startTime):
        self.time_to_live = max_fail
        self.payload = payload
        self.startTime = startTime

    def DecreaseTimeToLive(self):
        self.time_to_live = self.time_to_live - 1

    def isDead(self):
        return self.time_to_live == 0


class TimeCalculator:
    def __init__(self):
        self.enable = False
        self.RTT = None
        self.devRTT = 50
        self.TimeOut = None
        self.alpha = 0.125
        self.beta = 0.25

    def UpdateTimerParam(self, newRTT):
        print(newRTT)
        if self.enable is False:
            return
        if self.RTT is None:
            self.RTT = newRTT
        else:
            self.RTT = (1 - self.alpha) * self.RTT + self.alpha * newRTT

        self.devRTT = (1 - self.beta) * self.devRTT + self.beta * abs(newRTT - self.RTT)
        self.TimeOut = self.RTT + 4 * self.devRTT
        print(self.TimeOut)

    def getSuggestedTimeOut(self):
        return self.TimeOut

    def setEnable(self):
        self.enable = True

    def setDisabled(self):
        self.enable = False


def AddToControlBuffer(feed_name, sendStartTime):
    feed_controller = feedController(feed_payload[feed_name], MAX_FAIL, sendStartTime)
    ControlBuffer[feed_name] = feed_controller


client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
send_startTime = time.perf_counter()
timeCalculator = TimeCalculator()
