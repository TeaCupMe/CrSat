
import os
import base64 as b64
import spidev
import time
from CrRadio.lib_nrf24 import NRF24
import RPi.GPIO as GPIO
from CrRadio.RadioEnvironment import *

from app import DisplayImageWidget
import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets, QtCore, QtGui



def getNewImage():
    command = [CrRadioCommand.StartImage.value]
    command.extend([0]*(32-len(command)))
    radio.write(command)
    while True:
        radio.write(command)
        print("image requested")
        while not radio.available():
            # pass
            time.sleep(10000/1000000.0)
        
        buf = []
        radio.read(buf, 32)
        print(str(buf)+"\n" if len(buf)>0 else "", end = "")
        if buf[0] == CrRadioCommand.StartImage.value:
            print("recieved")
            break

    string = ""
    c = 0
    with open("./images/newimage.b64", "wb") as file:
        while not buf[0] == CrRadioCommand.FinishImage.value:
            while not radio.available([0]):
                pass
                #time.sleep(10000/1000000.0)
            if (buf[1]<<8|buf[2])%1 == 0:
                print("recieved", (buf[1])<<8 | buf[2], "packages")
            buf = []
            radio.read(buf, 32)
            if not buf[0] == CrRadioCommand.FinishImage.value:
                for i in buf[3:]:
                    if i!="=":
                        file.write(i.to_bytes(1, byteorder = 'big'))
            #file.write(buf[3:])
            c+=1
    print(f"finished, recieved {c} packages")
    with open("./images/newimage.b64", "rb") as read_image, open("./images/newimage.jpg", "wb") as write_image:
        write_image.write(b64.decodebytes(read_image.read()))


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

    radio = NRF24(GPIO, spidev.SpiDev())
    radio.begin(0, 5)
    time.sleep(1)
    radio.setRetries(15, 15)
    radio.setPayloadSize(32)
    radio.setChannel(0x60)

    radio.setDataRate(NRF24.BR_1MBPS)
    radio.setPALevel(NRF24.PA_MAX)
    radio.setAutoAck(True)
    radio.enableDynamicPayloads()
    radio.enableAckPayload()

    radio.openWritingPipe(pipes[0])
    radio.openReadingPipe(1, pipes[1])
    radio.printDetails()

    radio.startListening()

    app = QtWidgets.QApplication(sys.argv)
    display_image_widget = DisplayImageWidget()
    display_image_widget.show()
    sys.exit(app.exec_())
                
                

