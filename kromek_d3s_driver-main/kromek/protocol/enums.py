class ErrorCode(object):
    UNKNOWN = 0x0
    ALREADY_CONNECTED_USB = 0x1
    ALREADY_CONNECTED_BT = 0x2
    NOT_IMPLEMENTED = 0x3
    UNKNOWN_MESSAGE_ID = 0x4
    UNKNOWN_COMPONENT_ID = 0x5
    SIGMA_NOT_ENUMERATED = 0x6
    TN15_NOT_ENUMERATED = 0x7
    SIGMA_FREEZE_DETECTED = 0x8
    TN15_FREEZE_DETECTED = 0x9

    @classmethod
    def is_recoverable(cls, err):
        return (
            err == ErrorCode.SIGMA_NOT_ENUMERATED
            or err == ErrorCode.TN15_NOT_ENUMERATED
            or err == ErrorCode.SIGMA_FREEZE_DETECTED
            or err == ErrorCode.TN15_FREEZE_DETECTED
        )


class Component(object):
    GAMMA_DETECTOR = 0x01
    NEUTRON_DETECTOR = 0x02
    INTERFACE_BOARD = 0x07


class MessageType(object):
    # Commands
    SET_GAIN = 0x02
    SET_BIAS = 0x07
    SET_LLD = 0x09

    # Requests
    GET_GAIN = 0x82
    GET_BIAS = 0x87
    GET_SERIAL_NO = 0x88
    GET_LLD = 0x89
    GET_16BIT_SPECTRUM = 0xC1
    INITIALIZE = 0xC4
    GET_STATUS = 0xC5

    # Errors
    ERROR = 0xC0

    @classmethod
    def has_response(cls, type):
        return (
            type == MessageType.GET_GAIN
            or type == MessageType.GET_BIAS
            or type == MessageType.GET_SERIAL_NO
            or type == MessageType.GET_LLD
            or type == MessageType.GET_16BIT_SPECTRUM
            or type == MessageType.INITIALIZE
            or type == MessageType.GET_STATUS
        )
