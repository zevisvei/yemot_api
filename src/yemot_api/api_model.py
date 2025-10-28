from datetime import date as datetime_date
from datetime import datetime
from datetime import time as datetime_time
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator


class ApiModel(BaseModel):
    api_call_id: str | None = Field(default=None, alias="ApiCallId")
    api_phone: str | None = Field(default=None, alias="ApiPhone")
    api_did: str | None = Field(default=None, alias="ApiDID")
    api_real_did: str | None = Field(default=None, alias="ApiRealDID")
    api_extension: str | None = Field(default=None, alias="ApiExtension")
    api_enter_id: str | None = Field(default=None, alias="ApiEnterID")
    api_enter_id_name: str | None = Field(default=None, alias="ApiEnterIDName")
    api_time: str | None = Field(default=None, alias="ApiTime")
    hangup: str | None = Field(default=None, alias="Hangup")
    api_hangup_extension: str | None = Field(default=None, alias="ApiHangupExtension")
    referred_from: str | None = Field(default=None, alias="ReferredFrom")


class QueueModel(BaseModel):
    customer_did: str = Field(alias="CustomerDID")
    real_did: str = Field(alias="RealDID")
    folder: str = Field(alias="Folder")
    phone: str = Field(alias="Phone")
    id_type: str | None = Field(default=None, alias="IdType")
    enter_id: str | None = Field(default=None, alias="EnterId")
    date: Annotated[
        datetime_date, BeforeValidator(lambda v: _parse_dd_mm_yyyy(v))
    ] = Field(alias="Date", description="Date in format dd/mm/yyyy")  # https://stackoverflow.com/questions/79788585/how-to-handle-custom-date-format-dd-mm-yyyy-in-query-params-with-inherited-mod
    time: datetime_time = Field(alias="Time")
    hebrew_date: str = Field(alias="HebrewDate")
    module: str = Field(alias="Module")
    queue_status: str = Field(alias="QueueStatus")
    queue_total_seconds: int = Field(alias="QueueTotalSeconds")
    queue_total_time: str = Field(alias="QueueTotalTime")
    queue_waiting_seconds: int = Field(alias="QueueWaitingSeconds")
    queue_waiting_time: str = Field(alias="QueueWaitingTime")
    answer_seconds: int | None = Field(default=None, alias="AnswerSeconds")
    answer_time: str | None = Field(default=None, alias="AnswerTime")
    answer_number: str | None = Field(default=None, alias="AnswerNumber")
    queue_record_path: str | None = Field(default=None, alias="QueueRecordPath")
    yemot_call_id: str | None = Field(default=None, alias="YemotCallID")
    yd_timestamp: int | None = Field(default=None, alias="YDTimestamp")


class QueueSettingsModel(BaseModel):
    api_call_id: str | None = Field(default=None, alias="ApiCallId")
    yemot_call_id: str | None = Field(default=None, alias="YemotCallID")
    api_phone: str | None = Field(default=None, alias="ApiPhone")
    api_did: str | None = Field(default=None, alias="ApiDID")
    api_real_did: str | None = Field(default=None, alias="ApiRealDID")
    api_extension: str | None = Field(default=None, alias="ApiExtension")
    api_enter_id: str | None = Field(default=None, alias="ApiEnterID")
    api_enter_id_name: str | None = Field(default=None, alias="ApiEnterIDName")
    api_time: str | None = Field(default=None, alias="ApiTime")


class RoutingModel(BaseModel):
    customer_did: str = Field(alias="CustomerDID")
    real_did: str = Field(alias="RealDID")
    folder: str = Field(alias="Folder")
    phone: str = Field(alias="Phone")
    id_type: str = Field(alias="IdType")
    enter_id: str = Field(alias="EnterId")
    date: Annotated[
        datetime_date, BeforeValidator(lambda v: _parse_dd_mm_yyyy(v))
    ] = Field(alias="Date", description="Date in format dd/mm/yyyy")
    time: datetime_time = Field(alias="Time")
    hebrew_date: str = Field(alias="HebrewDate")
    module: str = Field(alias="Module")
    routing: str = Field(alias="Routing")
    your_id: str = Field(alias="YourID")
    dial_status: str = Field(alias="DialStatus")
    dial_time: int = Field(alias="DialTime")
    answer_time: int = Field(alias="AnswerTime")
    answer_number: str = Field(alias="AnswerNumber")


def _parse_dd_mm_yyyy(v: str) -> datetime_date:
    print(f"Parsing date: {v} ({type(v)})")
    if isinstance(v, str):
        return datetime.strptime(v, "%d/%m/%Y").date()
    return v
