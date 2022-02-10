import sys
# requrements = ["os","CrRadio.CrRadio.*", "CrRadio.RadioEnvironment",]
# trouble = []

# for i in requrements:
#     try:
#         exec("import "+i)
#     except ModuleNotFoundError as e:
#         trouble.append(i)
#     except ImportError as e:
#         if not i[0]==".":
#             requrements.append("."+i)
#         trouble.append(i)
#     finally:
#         if i[1:] in trouble:
#             trouble.remove(i[1:])
# else:
#     if len(trouble)==0:
#         print("All modules successfully imported.")
#     else:
#         print("Some modules cannot be imported. ") #! Flash red
#         print("Troubles importing: ")
#         for y in trouble:
#             print("\t -  "+y)




import os
from CrRadio.CrRadio import CrRadio
from CrRadio.RadioEnvironment import *

crRadio = CrRadio(placement=1, debug=True)
crRadio.sendFile(os.path.abspath("./test.b64"))