from RadioEnvironment import *

class Test:
    def __init__(self, a):
        print(self.f(a))
    def f(self, h):
        return h*4
        

# a = int(input())
# b = Test(a)

# print(65536&0b11111111)
# print(CrRadioEventResult.TimeoutError)
# print(bool(None))
# package = [12, 126]
# print((package[0]<<8)|package[1])
# print((12*256)+126)
buf = [0]*32  
buf[0] = CrRadioCommand.FinishImage.value
print(buf)


# _toSend = []
# _toSend.append(CrRadioMessageType.ImagePiece.value)     #* Adding the first byte so that the
                                                                    #*      reciever knows what the message contains
# _splitIndex = self._splitPieceIndex(index)
# _toSend.append(_splitIndex[0])                          #* Adding two bytes of package index 
# _toSend.append(_splitIndex[1])
# print(_toSend)



# print(bool(CrRadioEventResult.TypeError))


# for index in range(670):
#     _toSend = []
#     high = index >> 8
#     low = index%256
#     print(high, low)
# import base64
# def splt(n, string):
#     print(string)
#     open("imgbef.png", "wb").write(base64.decodebytes(string.encode()))
#     chunks = [string[i:i+n] for i in range(0, len(string), n)]
#     chunks[-1] = chunks[-1]+"="*(n-len(chunks[-1]))

#     print(chunks[-1])
#     print(len(chunks))
#     open("imgaft.png", "wb").write(base64.decodebytes(("".join(chunks)).encode()))
# with open("./test.b64", "r") as f:
    
#     splt(29, "".join([i[:-1] for i in f.readlines()]))
# print(2**16)

# a = None
# if not a:
#     print(123123)










# import sys
# import time
# i=0
# for k in range(10):
#                 i%=3
#                 i+=1
#                 # print("                             ", end='\r')
#                 sys.stdout.write("\rПоиск информации о вас"+i*".")
#                 sys.stdout.flush()
#                 time.sleep(0.5)
#                 if i==3:
#                     sys.stdout.write("\r                         ")

# a='''yo\
# u \
# ar\
# e g\
# a\
# y'''
# sys.stdout.write("\r                             ")
# for k in range(len(a)):

#                 sys.stdout.write("\r"+a[-k-1:])
#                 sys.stdout.flush()
#                 time.sleep(0.5)
                
