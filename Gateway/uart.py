import subprocess

try:
    import serial.tools.list_ports
except ImportError:
    subprocess.check_call(['pip', 'install', 'pyserial'])
try:
    import sys
except ImportError:
    subprocess.check_call(['pip', 'install', 'sys'])

from adafruitIO import feed_payload, SendData
import time

FAIL_LIMIT = 5
TIME_OUT = 1000
# sensor code
TEMP_HUMID = 0
MQ9 = 1

NORMAL = 0
WAIT_DATA = 1
PROCESS_DATA = 2

RESPONSE = 0
REQUEST = 1
ABORT = 2

NAK = 0
ACK = 1
RESEND = 2
ABORT = 3

seq = 0

connectionBuffer = {}


def FindName(key):
    if key == "T":
        return "temp-sensor"
    if key == "H":
        return "humidity-sensor"
    if key == "G":
        return "co-sensor"
    else:
        return None


def getPort(keyword):
    # Take port
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    for port in ports:
        strPort = str(port)
        if keyword in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
    return commPort


def ConnectSerial(port, baundrate=115200):
    global connectionBuffer
    ser = None
    if (port != "None"):
        time.sleep(1)
        ser = serial.Serial(port, baudrate=baundrate)
        print("Connected to", port)
        connectionBuffer[ser] = True
    else:
        print("Port is not found")
    return ser


def parseData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    seq = splitData[0]
    pktIndex = splitData[1]
    pktCount = splitData[2]
    feed_name = FindName(splitData[3])
    payload_int = splitData[4]
    payload_float = splitData[5]
    check_sum = splitData[6]
    payload = float(str(payload_int) + "." + str(payload_float))
    ret = (int(check_sum) == (int(seq) + int(payload_int) + int(payload_float) + int(pktIndex) + int(pktCount)))
    return ret, (pktIndex == pktCount), seq, feed_name, payload


def readSerial(ser):
    bytesToRead = ser.inWaiting()  # Take data from buffer
    return (bytesToRead > 0), bytesToRead


def writeString(ser, data):
    ser.write(str(data).encode())


def writeBytes(ser, data):
    ser.write(data)


class Controller:
    def __init__(self, port):
        self.state = NORMAL
        self.mess = ""
        self.lastContent = 0
        self.start_time = 0
        self.timeOut_count = 0
        # self.ser = ConnectSerial(getPort(port))  #for debug, turn this on
        self.ser = 0
        self.targetPort = 0
        self.port_to_connect = port
        self.feed_names = []
        self.enable = False

    def ReadData(self, period, sensorType, qos=0):
        if not self.enable:
            return

        global seq
        global feed_names
        try:
            if self.state == NORMAL:
                if duration(self.start_time) < period * 1000:
                    # Check re-send request from MCU
                    success, bytesToRead = readSerial(self.ser)
                    while success:  # This case is when message is found and receiving
                        new_mess = self.ser.read(bytesToRead).decode("UTF-8")
                        self.mess = self.mess + new_mess
                        ret, completedMess, remainedMess = self.getCompletedMessage(self.mess)
                        if ret is True and len(completedMess):
                            ret, isLastMessage = self.decodeMessage(completedMess)
                            if ret == RESEND:
                                writeBytes(self.ser, self.lastContent)
                                self.mess = ""
                                break
                        success, bytesToRead = readSerial(self.ser)
                    ##########################
                else:
                    # Send request to MCU
                    self.mess = ""
                    self.lastContent = self.packageContent(REQUEST, sensorType, seq, FAIL_LIMIT, 0)
                    writeBytes(self.ser, self.lastContent)
                    # print(self.lastContent)
                    self.state = WAIT_DATA
                    self.start_time = startTimer()
                    self.feed_names = []
                    print("REQUEST DATA")
                    # print(self.lastContent)
            if self.state == WAIT_DATA:
                while True:
                    success, bytesToRead = readSerial(self.ser)
                    while success:  # This case is when message is found and receiving
                        new_mess = self.ser.read(bytesToRead).decode("UTF-8")
                        self.mess = self.mess + new_mess
                        ret, completedMess, remainedMess = self.getCompletedMessage(self.mess)
                        # print(completedMess)
                        if not ret:  # there is wrong-format sub-mess
                            self.lastContent = self.packageContent(RESPONSE, sensorType, seq, FAIL_LIMIT, ACK)
                            writeBytes(self.ser, self.lastContent)
                            self.start_time = startTimer()
                            remainedMess = ""  # Clear mess
                        elif len(completedMess):  # analyze completed message
                            ret, isLastMessage = self.decodeMessage(completedMess)
                            if ret == RESEND:  # there is resend mess
                                # RESEND REQUEST
                                print('RESENT REQUESTED FROM MCU')
                                writeBytes(self.ser, self.lastContent)
                                self.start_time = startTimer()  # Re-start timer
                                self.ser.read(bytesToRead).decode("UTF-8")  # Get remaining mess out of buffer
                                remainedMess = ""  # Clear mess
                            elif ret == ABORT:
                                print('ABORT REQUESTED FROM MCU')
                                self.start_time = startTimer()
                                remainedMess = ""  # Clear mess
                                self.state = NORMAL
                                self.feed_names = []
                            elif ret == ACK and isLastMessage:  # all completed mess ACK
                                print('SEND ACK')
                                self.state = NORMAL
                                self.lastContent = self.packageContent(RESPONSE, sensorType, seq, FAIL_LIMIT, ACK)
                                writeBytes(self.ser, self.lastContent)
                                # All packet ACK, start uploading value to adafruit
                                for feed_name in self.feed_names:
                                    SendData(feed_name)
                                ##################################################
                                self.start_time = startTimer()
                            elif ret == NAK:  # there is corrupted packet
                                print('SEND NAK')
                                self.lastContent = self.packageContent(RESPONSE, sensorType, seq, FAIL_LIMIT, NAK)
                                writeBytes(self.ser, self.lastContent)
                                self.start_time = startTimer()
                                wait(500)  # Wait for other packets to be fully loaded to buffer
                                self.ser.read(bytesToRead).decode("UTF-8")  # Get remaining message out of buffer
                                remainedMess = ""  # Clear message
                                self.feed_names = []  # Clear feed buffer
                        success, bytesToRead = readSerial(self.ser)
                        self.mess = remainedMess
                    # This case is when no message is found
                    if duration(self.start_time) >= TIME_OUT and self.timeOut_count < FAIL_LIMIT:
                        print('TIMEOUT WAITING FOR DATA FROM MCU')
                        writeBytes(self.ser, self.lastContent)
                        self.start_time = time.perf_counter()
                        self.timeOut_count = self.timeOut_count + 1
                    elif duration(self.start_time) >= TIME_OUT and self.timeOut_count >= FAIL_LIMIT:
                        print('TIMEOUT WAITING FOR DATA FROM MCU REACHES LIMIT')
                        self.lastContent = self.packageContent(ABORT, sensorType, seq, FAIL_LIMIT, NAK)  # Send abort
                        writeBytes(self.ser, self.lastContent)
                        self.timeOut_count = 0
                        self.state = NORMAL

                    if self.state == NORMAL:
                        seq = (seq + 1) // 8
                        self.start_time = time.perf_counter()
                        break
        except:
            if self.SerialisConnected():
                connectionBuffer.pop(self.ser)

        if (not self.SerialisConnected()):
            self.TryToReconnect()

    def SerialisConnected(self):
        if self.ser in connectionBuffer.keys():
            return connectionBuffer[self.ser]
        else:
            return False

    def TryToReconnect(self):
        self.targetPort = getPort(self.port_to_connect)
        if self.targetPort != "None":  # Try to connect if any STM32 port is found
            try:
                self.ser = ConnectSerial(self.targetPort)
            except:
                connectedSerials = list(connectionBuffer.keys())
                for Serial in connectedSerials:
                    if Serial.port == self.targetPort:
                        self.ser = Serial
                        break
            connectionBuffer[self.ser] = True
            self.state = NORMAL
            self.start_time = time.perf_counter()  # Start timer
        else:
            print("Can't find port")
            return

    def packageContent(self, req, type_sensor, seq_num, fail_limit, ack):
        checksum = req + seq_num + fail_limit + ack
        content = bytearray(6)
        content[0] = req
        content[1] = type_sensor
        content[2] = seq_num
        content[3] = fail_limit
        content[4] = ack
        content[5] = checksum
        return content

    def decodeMessage(self, mess):
        isLastPacket = False
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            if (start > end):
                print("Wrong syntax")
                return NAK, isLastPacket  # not success due to wrong syntax
            mess_to_parse = mess[start:end + 1]
            if 'Re-send' in mess_to_parse:  # REQUIRED TO RESEND MESSAGE FROM MCU
                return RESEND, isLastPacket
            if 'Abort' in mess_to_parse:
                return ABORT, isLastPacket
            try:  # If there are error, this mess is in wrong format
                ret, isLastPacket, seq, feed_name, payload = parseData(mess_to_parse)
                if ret:  # If data isn't corrupted, add feed's payload to buffer
                    feed_payload[feed_name] = payload
                    self.feed_names.append(feed_name)
                else:
                    return NAK, isLastPacket  # not success due to checksum not true
            except:
                return NAK, isLastPacket
            # Restructure mess
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end + 1:]

        return ACK, isLastPacket  # Send success

    def getCompletedMessage(self, mess):
        completed_mess = ""
        remained_mess = mess
        while ("#" in remained_mess) and ("!" in remained_mess):
            start = remained_mess.find("!")
            end = remained_mess.find("#")
            if start > end:
                return False, completed_mess, remained_mess
            completed_mess = completed_mess + remained_mess[start:end + 1]
            remained_mess = remained_mess[end + 1:]
        return True, completed_mess, remained_mess

    def setEnable(self, state):
        self.enable = state


def startTimer():
    global timeOut_count
    timeOut_count = 0
    return time.perf_counter()


def duration(start_time):
    current_time = time.perf_counter()
    if current_time < start_time:
        return (current_time + (sys.float_info.max - start_time)) * 1000
    return (current_time - start_time) * 1000


def wait(millisec):
    start = time.perf_counter()
    while duration(start) < millisec:
        pass
