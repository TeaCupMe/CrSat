import time
from time import sleep
from types import resolve_bases
from typing import Tuple

import RPi.GPIO as GPIO
import spidev

from .lib_nrf24 import NRF24
from .RadioEnvironment import *

GPIO.setmode(GPIO.BCM)

#! TODO: #4 Rewrite all(nearly all) error returns into raise errors. Assignee: @TeaCupMe


class CrRadio:
    # * @param placement:   1 - on the satellite    0 - on the ground

    pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

    def __init__(self, *, placement=1, debug=False) -> None:
        self.state = CrRadioState.Init
        self.debug = debug
        self.radio = NRF24(GPIO, spidev.SpiDev())
        self.radio.begin(0, 5)
        time.sleep(1)

        self.radio.setRetries(15, 15)
        self.radio.setPayloadSize(32)
        self.radio.setChannel(0x60)

        self.radio.setDataRate(NRF24.BR_1MBPS)
        self.radio.setPALevel(NRF24.PA_MIN)

        self.radio.setAutoAck(True)
        self.radio.enableDynamicPayloads()

        self.radio.enableAckPayload()
        if placement == 1:

            self.radio.openWritingPipe(self.pipes[1])
            self.radio.openReadingPipe(1, self.pipes[0])
        else:
            self.radio.openWritingPipe(self.pipes[0])
            self.radio.openReadingPipe(1, self.pipes[1])
        self.state = CrRadioState.Idle
        self.radio.startListening()
        self.radio.stopListening()
        self.radio.startListening()
        if self.debug:
            print("\n\nRADIO DETAILS:")
            self.radio.printDetails()
            print("END OF RADIO DETAILS\n\n")

    def _readRadio(self, buff: list, *, buff_len: int = 32) -> CrRadioEventResult:
        if not self.radio.available():
            return CrRadioEventResult.NoInfoError
        try:
            self.radio.read(buf=buff, buf_len=buff_len)
        except:
            return CrRadioEventResult.GenericError
        return CrRadioEventResult.Ok

    # TODO: #1 Finish getAck function @TeaCupMe
    def getAck(self, *args, desired: list = None):
        self.radio.startListening()
        _sentTime = time.time()
        buf = []
        while time.time()-_sentTime < 1 and not self.radio.available():
            pass
        self._print(self.radio.available())
        if not self.radio.available():
            return CrRadioEventResult.TimeoutError

        self.radio.read(buf, 32)

        self._print(f"Ack-like message {buf}")
        if desired and len(desired)+1 != len(buf):
            return CrRadioEventResult.GenericError
        elif desired and any(buf[i] != desired[i] for i in range(1, len(desired))):
            return CrRadioEventResult.GenericError
        else:
            return CrRadioEventResult.Ok

    def sendAck(self, *args, intended: list = None):
        buf = []
        buf.append(CrRadioMessageType.Ack.value)
        if intended and isinstance(intended, list) and len(intended) <= 31:
            buf.extend(intended)
        if len(buf) != 32:
            buf.extend([0]*(32-len(buf)))
        self._print(f"Ack {buf} sent")
        self.radio.write(buf)

    def _splitPieceIndex(self, index: int) -> Tuple[int, int]:
        if index >= 65536:
            raise ValueError(
                f"Image piece index should not be bigger than 65535, {index} recieved")
        high = (index >> 8) & 0b11111111
        low = index & 0b11111111
        return (high, low)

    def _sendCommand(self, command: CrRadioCommand, *args, values: Tuple = tuple()) -> CrRadioEventResult:
        if not isinstance(command, CrRadioCommand):
            return CrRadioEventResult.TypeError
        buf = list()
        # TODO: #2 Write _sendCommand function @TeaCupMe
        buf.append(0)
        buf[0] = command.value
        self._print(values)
        if values:
            buf.extend(values)
        if len(buf) != 32:
            buf.extend([0]*(32-len(buf)))
        self._print(buf)
        self.radio.stopListening()
        self._print(self.radio.write(buf))
        self.radio.startListening()
        response = self.getAck()
        self._print(f"Command sent: {buf}")
        return response

    # TODO: #3 Rewrite sendFile function as open API. @TeaCupMe
    def sendFile(self, filePath: str) -> CrRadioEventResult:
        self.state = CrRadioState.ImageSending

        if filePath.split(".")[-1] != "b64":
            raise TypeError(
                f"Wrong file type: .b64 expected, {filePath.split('.')[-1]} got")
        with open(filePath, "r") as file:
            data = "".join(file.readlines())
            self._print(
                " ".join(["data len: ", str(len(data)), "\ndata:", ",".join(data)[:100]]))
            # file.close()

        packedData = self._splitStringToPieces(data)[0]
        print(
            f"Bytes to be transmitted: {len(data)}\nPackages to be transmitted: {len(packedData)}\nEstimated time: {self._estimateTime(packedData)}")
        resp = self._sendCommand(
            CrRadioCommand.StartImage, values=self._splitPieceIndex(len(packedData)))
        if not (bool(resp)):

            # SPELL
            print(
                f"{resp} Error occured while sending 'StartImage' command. Probably the reciever does not respond")
            return CrRadioEventResult.GenericError
        # self.radio.write(list("start"))
        for index in range(len(packedData)):
            _toSend = []
            # * Adding the first byte so that the
            _toSend.append(CrRadioMessageType.ImagePiece.value)
            # *      reciever knows what the message contains
            _splitIndex = self._splitPieceIndex(index)
            # * Adding two bytes of package index
            _toSend.append(_splitIndex[0])
            _toSend.append(_splitIndex[1])

            # * Adding actual data to the package
            _toSend.extend(packedData[index])
            self._print(f"Prepared package: {packedData[index]}")
            self._sendPackage(_toSend)  # * Sending package
        self._sendCommand(CrRadioCommand.FinishImage)
        return CrRadioEventResult.Ok

    # ! TODO #5 Rewrite recieveFile() method for open api
    def recieveFile(self, fileName: str) -> int:
        if fileName.split(".")[-1] != "b64":
            raise TypeError("Unappropriate file format: expected .b64")
        with open(fileName, "w") as file:
            self.radio.startListening()
            buff = [0]
            i = 1
            self._print("Listening for file...")
            while not buff[0] == CrRadioCommand.StartImage.value:

                if self.radio.available():
                    self.radio.read(buff, 32)
                    self._print(f"Message {buff} got")
            self.sendAck()
            self._print("'StartImage' command got")

            # while not string[:5]=="start":
            #     while not self.radio.available([0]):
            #         time.sleep(10000/1000000.0)
            #     self.radio.read(buff, 32)
            #     string == "".join([str(i) for i in buff])
            #     self.radio.writeAckPayload(1, [0, 1], len([0, 1]))
            # buff=[]
            # while not string[:3]=="end":
            #     buff=[]
            #     while not self.radio.available([0]):
            #         time.sleep(10000/1000000.0)
            #     self.radio.read(buff, 32)
            #     string == "".join([str(i) for i in buff])
            #     self.radio.writeAckPayload(1, [0, 1], len([0, 1]))
            #     file.write("".join(buff))

            return 0

    def _hash(self, data: list):
        toBeHashed = data.copy()
        for i in range(len(toBeHashed)):
            if not isinstance(toBeHashed[i], int):
                toBeHashed[i] = str(toBeHashed[i]).encode(encoding="UTF-8")
        hsh = sum(toBeHashed) % 255
        return hsh

    def _splitStringToPieces(self, string: str, *,  n=29) -> str:
        chunks = [string[i:i+n] for i in range(0, len(string), n)]
        chunks[-1] = chunks[-1]+"="*(n-len(chunks[-1]))
        return chunks, len(chunks)

    def _estimateTime(self, dt: list) -> int:

        _time = len(dt)/1000
        # self._print(f"Estimated time: {_time}")
        return _time  # !!! TODO: #7 Replace placeholder of _estimateTime() method

    def _sendPackage(self, package: list, *, hashsum: bool = False, ack: bool = True, desiredAck: bool = False) -> CrRadioEventResult:
        self._print("Sending package... Calculated index: ",
                    (package[0] << 8) | package[1])
        if not isinstance(package, (list)):
            self.state = CrRadioState.Error
            raise WrongPackageType(
                f"Package must be of type 'list', type '{type(package)}' recieved!!!")

        if len(package) > 32:
            self.state = CrRadioState.Error
            raise WrongPackageSize(
                (f"Package array must be of lenght 32 at most, {len(package)} bytes recieved!!!"))

        elif hashsum and not len(package) > 31:
            self.state = CrRadioState.Error
            raise WrongPackageSize(
                f"Because you specified including hashsum, package array must be of lenght 31 at most, {len(package)} bytes recieved!!!")
        # if not all(0<=)                           #!  TODO #8 Add content check for buffer elements before sending

        if hashsum:
            package.extend([0]*(31-len(package)))
            package.append(self._getHash(package))
        if len(package) != 32:
            package.extend([0]*(32-len(package)))
        # package.append(self._hash(package))
        self.radio.write(package)
        if ack:
            # ! TODO #11 Add error message if no ack recieved
            self.getAck(desired=package[1:] if desiredAck else None)
        return CrRadioEventResult.Ok

    def _print(self, message):  # ! TODO #13 Переписать метод _print() так, чтобы он работал не на if, а в зависимости от значения self.debug либо только писал лог, либо писал лог и выводил в консоль(на базе параметра file стандартного метода print())
        if self.debug:
            print(message)
        return

    def _parsePackage(self, package: list):  # ! TODO: #9 Finish package parsing function
        self._print("Parsing package: "+"["+"] ,[".join(package)+"]")
        command = package[0]

    def _getHash(self, package: list):
        return 0  # ! TODO #10 Add hashing function
