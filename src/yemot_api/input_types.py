from enum import StrEnum, auto
from typing import TypedDict


class FileAction(StrEnum):
    COPY = auto()
    MOVE = auto()
    DELETE = auto()


class UpdateTemplateEntries(StrEnum):
    DELETE = auto()
    UNBLOCK = auto()
    BLOCK = auto()


class UploadPhoneList(StrEnum):
    UPDATE = auto()
    NEW = auto()
    REMOVE = auto()


class RenderYMGRFileConvertType(StrEnum):
    JSON = auto()
    CSV = auto()
    HTML = auto()


class CampaignStatusEntries(StrEnum):
    ALL = auto()
    PENDING = auto()
    BLOCKED = auto()
    DONE = auto()
    ACCEPTED = auto()
    FAILED = auto()
    NO_ANSWER = auto()
    BUSY = auto()
    AMD = auto()
    RINGING = auto()
    UP = auto()
    BRIDGED = auto()
    REMOVE_REQUEST = auto()
    REDIAL = auto()
    CANCELED = auto()
    ERROR = auto()


class CampaignAction(StrEnum):
    ADD = "add"
    BLOCK = "block"
    HANGUP = "hangup"
    STOP = "stop"
    SET_PAUSED = "setPaused"
    SET_MAX_ACTIVE_CHANNELS = "setMaxActiveChannels"
    SET_MAX_BRIDGED_CHANNELS = "setMaxBridgedChannels"


class GetIvr2DirOrderBy(StrEnum):
    NAME = auto()
    DATE = auto()
    MTIME = auto()
    CUSTOMERDID = auto()
    UPLOADER = auto()
    SIZE = auto()
    SOURCE = auto()


class CallAction(StrEnum):
    MOVE_CALL_TO = "set:GOasap="
    ADD_TO_CONF_ROOM_DATA = "path:add:"
    REMOVE_FROM_CONF_ROOM_DATA = "path:remove:"
    REMOVE_USER_FROM_CONF_ROOM = "kick"
    MUTE_USER_CONF_ROOM = "mute"
    UN_MUTE_USER_CONF_ROOM = "unmute"
    LOWER_HAND_CONF_ROOM = "lowerhand"
    RAISE_HAND_CONF_ROOM = "raisehand"
    CONF_ROOM_NEW_GOTO = "set:ConfbridgeNewGoto="
    SET_LANG = "action=set:Clanguage="


class DoubleAuthAction(StrEnum):
    SEND_CODE = "SendCode"
    VERIFY_CODE = "VerifyCode"


class RunTzintukMethod(StrEnum):
    TPL = auto()
    TZL = auto()
    OTHER = auto()


class TzintukimListManagementAction(StrEnum):
    GET_LISTS = "getlists"
    GET_LIST_ENTRIES = "getlistEnteres"
    GET_LOG_LIST = "getLogList"
    RESET_LIST = "resetList"


class CreateTaskType(StrEnum):
    SEND_SMS = "SendSMS"
    RUN_TZINTUK = "RunTzintuk"
    MOVE_ON_FILE = "MoveOnFile"


class SipExtensionManagementAction(StrEnum):
    SET = "Set"
    GET = "Get"


class ValidationCallerIdAction(StrEnum):
    SEND = "send"
    VALID = "valid"


class ValidationCallerIdValidType(StrEnum):
    CALL = "CALL"
    SMS = "SMS"


class QueueManagementAction(StrEnum):
    KICK = "kick"
    PAUSE = "pause"
    UNPAUSE = "unpause"


class PirsumPhoneManagementAction(StrEnum):
    GET_REGISTRATION_STATUS = "GetRegistrationStatus"
    REGISTRATION = "Registration"
    UN_REGISTRATION = "UnRegistration"


class QueueCallBackAction(StrEnum):
    GET_QUEUES = "getQueues"
    GET_LIST = "getList"
    REMOVE_NUMBER = "removeNumber"


class MfaSessionAction(StrEnum):
    IS_PASS = "isPass"
    TRY = "try"
    GET_MFA_METHODS = "getMFAMethods"
    SEND_MFA = "sendMFA"
    VALID_MFA = "validMFA"
    ADD_METHOD = "addMethod"
    REVALIDATE_METHOD = "reValidMethod"
    VALID_METHOD = "validMethod"
    DELETE_METHOD = "deleteMethod"
    GET_MFA_TRUST_TOKENS = "getMFATrustTokens"
    DELETE_TRUST_TOKEN = "deleteTrustToken"
    GET_MFA_TRUST_IPS = "getMFATrustIps"
    SET_MFA_TRUST_IPS = "setMFATrustIps"


class RunTzintukInput1(TypedDict):
    phone: str
    callerId: str


class RunTzintukInput2(TypedDict):
    phones: list[str]
    callerId: str


class RunCampaignPhonesDict(TypedDict):
    name: str | None
    moreinfo: str | None
    blocked: bool | None
    text: str | None
