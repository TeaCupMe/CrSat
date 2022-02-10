import enum


class CrRadioState(enum.Enum):
    Init = 1
    Idle = 2
    AwaitingForImage = 3
    ImageSending = 4
    ImageRecieving = 8
    AwaitingCommand = 16
    Error = 7


class CrRadioEventResult(enum.Enum):
    Ok = 1
    GenericError = 2
    TimeoutError = 3
    NoInfoError = 13
    TypeError = 21

    def __bool__(self):
        if self.value == CrRadioEventResult.Ok.value:
            return True
        else:
            return False

    def __str__(self):
        return self.name


class CrRadioMessageType(enum.Enum):
    Command = 1
    ImagePiece = 3
    Ack = 9


class CrRadioCommand(enum.Enum):
    StartImage = 3
    FinishImage = 5


class WrongPackageSize(Exception):
    pass


class WrongPackageType(Exception):
    pass


def splitStringToPieces(string: str, *,  n=29) -> str:
    chunks = [string[i:i+n] for i in range(0, len(string), n)]
    chunks[-1] = chunks[-1]+"="*(n-len(chunks[-1]))
    return chunks, len(chunks)


def splitPieceIndex(index: int) -> tuple[int, int]:
    if index >= 65536:
        raise ValueError(
            f"Image piece index should not be bigger than 65535, {index} recieved")
    high = (index >> 8) & 0b11111111
    low = index & 0b11111111
    return (high, low)


def estimateTime(dt: list) -> int:

    _time = len(dt)/1000
    # self._print(f"Estimated time: {_time}")
    return _time  # !!! TODO: #7 Replace placeholder of _estimateTime() method


def preparePackage(package: list, *, hashsum: bool = False, ack: bool = True, desiredAck: bool = False) -> CrRadioEventResult:
    if (package[1] << 8 | package[2]) % 50 == 0:
        print("Sending package... Calculated index: ",
          (package[1] << 8) | package[2])
    if not isinstance(package, (list)):
        state = CrRadioState.Error
        raise WrongPackageType(
            f"Package must be of type 'list', type '{type(package)}' recieved!!!")

    if len(package) > 32:
        state = CrRadioState.Error
        raise WrongPackageSize(
            (f"Package array must be of lenght 32 at most, {len(package)} bytes recieved!!!"))

    elif hashsum and not len(package) > 31:
        state = CrRadioState.Error
        raise WrongPackageSize(
            f"Because you specified including hashsum, package array must be of lenght 31 at most, {len(package)} bytes recieved!!!")
    # if not all(0<=)                           #!  TODO #8 Add content check for buffer elements before sending

    if len(package) != 32:
        package.extend([0]*(32-len(package)))
    return package
