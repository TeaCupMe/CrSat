import base64 as b64
def encodeImage(path:str="./images/image.jpg"):
    with open(path, "rb") as image:
        image_read = image.read()

    with open("./images/imagetest.b64", "wb") as image:
        image.write(b64.encodebytes(image_read))

def decodeImage(path:str = "./images/newimage.b64"):

    with open("./images/newimage.b64", "rb") as image:
        image_read = image.read()

    with open("./images/newimage.jpg", "wb") as image:
        image.write(b64.decodebytes(image_read))

decodeImage("./images/newimage.b64")
