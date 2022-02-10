import os
from CrRadio.CrRadio import CrRadio
from CrRadio.RadioEnvironment import *

crRadio = CrRadio(placement=0, debug=True)
crRadio.recieveFile("./recievedFile.b64")
# crRadio.sendFile(os.path.abspath("./test.b64"))