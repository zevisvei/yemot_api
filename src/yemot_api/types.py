from __future__ import annotations

import json
from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class GetSession(BaseModel):
    name: str
    units_expire_date: date = Field(alias="unitsExpireDate")
    email: str
    organization: str
    contact_name: str = Field(alias="contactName")
    phones: str
    invoice_name: str = Field(alias="invoiceName")
    invoice_address: str = Field(alias="invoiceAddress")
    fax: str
    access_password: str | None = Field(alias="accessPassword")
    units: float
    record_password: str | None = Field(alias="recordPassword")
    credit_file: str = Field(alias="creditFile")
    username: str


class GetTransactions(BaseModel):
    transactions: list[Transaction]
    total_count: int = Field(alias="totalCount")


class Transaction(BaseModel):
    id: int
    transaction_time: datetime = Field(alias="transactionTime")
    amount: float
    description: str
    who: str  # | Literal["ADMIN", "TRANSFER", "expire"]
    new_balance: float = Field(alias="newBalance")
    expire_date: date | None = Field(alias="expireDate")
    campaign_id: str | None = Field(alias="campaignId")


class TransferUnits(BaseModel):
    destination: str
    amount: float
    new_balance: float = Field(alias="newBalance")


class GetIncomingCalls(BaseModel):
    calls: list[Call]
    calls_count: int = Field(alias="callsCount")


class Call(BaseModel):
    did: str
    caller_id_num: str = Field(alias="callerIdNum")
    duration: int
    transfer_from: Literal["מועבר"] | None = Field(alias="transferFrom")
    id: str
    path: str | None


class UploadFile(BaseModel):
    path: str
    size: int
    converted_size: int | None = Field(default=None, alias="convertedSize")
    success: bool
    duration: float | None = None


class GetTemplates(BaseModel):
    templates: list[Template]


class Template(BaseModel):
    template_id: int = Field(alias="templateId")
    description: str | None
    caller_id: str = Field(alias="callerId")
    entries_count: int = Field(alias="entriesCount")
    blocked_entries_count: int = Field(alias="blockedEntriesCount")
    incoming_policy: Literal["OPEN", "BLACKLIST", "WHITELIST", "BLOCKED"] = Field(alias="incomingPolicy")
    customer_default: bool = Field(alias="customerDefault")
    max_active_channels: int = Field(alias="maxActiveChannels")
    max_bridged_channels: int = Field(alias="maxBridgedChannels")
    originate_timeout: float = Field(alias="originateTimeout")
    vm_detect: bool = Field(alias="vmDetect")
    filter_enabled: bool = Field(alias="filterEnabled")
    max_dial_attempts: int = Field(alias="maxDialAttempts")
    redial_wait: int = Field(alias="redialWait")
    redial_policy: Literal["NONE", "CONGESTIONS", "FAILED"] = Field(alias="redialPolicy")
    yemot_context: Literal["SIMPLE", "REPEAT", "MESSAGE", "VOICEMAIL", "BRIDGE", "OTHER"] = Field(alias="yemotContext")
    bridge_to: str | None = Field(alias="bridgeTo")
    play_private_msg: bool = Field(alias="playPrivateMsg")
    message_exists: bool = Field(alias="messageExists")
    message_duration: float = Field(alias="messageDuration")
    units_per_message: float = Field(alias="unitsPerMessage")
    more_info_exists: bool = Field(alias="moreinfoExists")
    more_info_duration: float = Field(alias="moreinfoDuration")
    remove_request: Literal["SILENT", "WITH_MESSAGE"] = Field(alias="removeRequest")


class GetTemplateEntries(BaseModel):
    template_id: int = Field(alias="templateId")
    entries: list[TemplateEntry]


class TemplateEntry(BaseModel):
    rowid: int
    index: int
    phone: str
    blocked: bool
    name: str | None
    more_info: str | None = Field(alias="moreinfo")


class UploadPhoneList(BaseModel):
    message: str
    template_id: int = Field(alias="templateId")
    total_parsed: int = Field(alias="totalParsed")
    rejected_records: list[RejectedRecord] = Field(alias="rejectedRecords")
    total_inserted: int = Field(alias="totalInserted")
    total_updated: int = Field(alias="totalUpdated")
    total_removed: int = Field(alias="totalRemoved")


class RejectedRecord(BaseModel):
    phone: str
    name: str | None
    more_info: str | None = Field(alias="moreinfo")
    blocked: bool
    error_state: Literal["DUPLICATE", "INVALID"] = Field(alias="errorState")
    original_row_number: int = Field(alias="originalRowNumber")


class RunCampaign(BaseModel):
    template_id: int = Field(alias="templateId")
    campaign_id: str = Field(alias="campaignId")
    entries_count: int = Field(alias="entriesCount")
    pending: int
    blocked: int
    estimated_price: float = Field(alias="estimatedPrice")
    customer_units: float = Field(alias="customerUnits")
    sms_count: int = Field(alias="smsCount")
    sms_price: float = Field(alias="smsPrice")


class CampaignStatus(BaseModel):
    campaign: CampaignStatusCampaign


class CampaignStatusCampaign(BaseModel):
    campaign_id: str = Field(alias="campaignId")
    campaign_status: Literal["STOPPING ", "PAUSED", "RUNNING", "STOPPED", "FINISHED"] = Field(alias="campaignStatus")
    template_id: int = Field(alias="templateId")
    who: str
    caller_id: str = Field(alias="callerId")
    blocked_entries: int = Field(alias="blockedEntries")
    pending_entries: int = Field(alias="pendingEntries")
    active_entries: int = Field(alias="activeEntries")
    bridged_entries: int = Field(alias="bridgedEntries")
    redial_entries: int = Field(alias="redialEntries")
    done_entries: int = Field(alias="doneEntries")
    failed_entries: int = Field(alias="failedEntries")
    total_entries: int = Field(alias="totalEntries")
    total_dialed: int = Field(alias="totalDialed")
    total_successful: int = Field(alias="totalSuccessful")
    total_bridged: int = Field(alias="totalBridged")
    total_failed: int = Field(alias="totalFailed")
    total_incoming: int = Field(alias="totalIncoming")
    total_incoming_bridged: int = Field(alias="totalIncomingBridged")
    max_active_channels: int = Field(alias="maxActiveChannels")
    max_bridged_channels: int = Field(alias="maxBridgedChannels")
    max_dial_attempts: int = Field(alias="maxDialAttempts")
    redial_wait: float = Field(alias="redialWait")
    redial_policy: Literal["FAILED", "NONE", "CONGESTIONS"] = Field(alias="redialPolicy")
    vm_detect: bool = Field(alias="vmDetect")
    play_private_msg: bool = Field(alias="playPrivateMsg")
    run_time: float = Field(alias="runTime")
    current_price: float = Field(alias="currentPrice")
    paused: bool
    entries: list[CampaignStatusEntry] | None


class CampaignStatusEntry(BaseModel):
    phone: str
    name: str | None
    more_info: str | None = Field(alias="moreinfo")
    entry_status: Literal["bridged", "done", "no_answer", "failed", "busy"] = Field(alias="entryStatus")
    duration: int | None
    bridged_duration: int | None = Field(alias="bridgedDuration")
    current_price: float = Field(alias="currentPrice")
    bridged: bool
    start_time: time | None = Field(alias="startTime")
    redials: list[CampaignStatusEntryRedial] | None


class CampaignStatusEntryRedial(BaseModel):
    entry_status: Literal["bridged", "done", "no_answer", "failed", "busy"] = Field(alias="entryStatus")
    duration: int | None
    bridged_duration: int | None = Field(alias="bridgedDuration")
    bridged: bool
    start_time: time | None = Field(alias="startTime")


class GetActiveCampaigns(BaseModel):
    campaigns: list[CampaignStatusCampaign]


class CampaignAction(BaseModel):
    campaign: CampaignStatusCampaign
    action: Literal["ADD", "BLOCK", "HANGUP", "STOP", "SET_PAUSED", "SET_MAX_ACTIVE_CHANNELS", "SET_MAX_BRIDGED_CHANNELS"]
    value: dict[str, str | RunCampaignPhonesDict] | str | int | None
    data: list[CampaignActionDataEntry]


class RunCampaignPhonesDict(BaseModel):
    name: str | None
    more_info: str | None = Field(alias="moreinfo")
    blocked: bool | None
    text: str | None


class CampaignActionDataEntry(BaseModel):
    phone: str
    action: Literal["add", "addblocked", "block", "unblock", "hangup", "failed"]


class ScheduleCampaign(BaseModel):
    customer_units: float = Field(alias="customerUnits")
    template_id: int = Field(alias="templateId")
    sched_time: datetime = Field(alias="schedTime")
    sched_id: int = Field(alias="schedId")
    entries_count: int = Field(alias="entriesCount")
    pending: int
    blocked: int
    estimated_price: float = Field(alias="estimatedPrice")


class GetScheduledCampaigns(BaseModel):
    total_count: int = Field(alias="totalCount")
    scheduled_campaigns: list[GetScheduledCampaignsEntry] = Field(alias="scheduledCampaigns")


class GetScheduledCampaignsEntry(BaseModel):
    sched_id: int = Field(alias="schedId")
    template_description: str | None = Field(alias="templateDescription")
    error: bool
    start_time: datetime = Field(alias="startTime")
    ip: str
    create_time: datetime = Field(alias="createTime")
    campaign_id: str | None = Field(alias="campaignId")
    template_id: int = Field(alias="templateId")
    error_msg: str | None = Field(alias="errorMsg")
    pending: bool


class GetIvr2DirEntry(BaseModel):
    exists: bool
    name: str
    unique_id: str = Field(alias="uniqueId")
    what: str
    file_type: str = Field(alias="fileType")


class GetIvr2DirEntryFiles(GetIvr2DirEntry):
    mtime: datetime | None = None
    size: int | None = None

    @field_validator("mtime", mode="before")
    def parse_mtime(cls, value: str | None) -> datetime | None:  # noqa: N805
        if value is None:
            return None
        return datetime.strptime(value, "%d/%m/%Y %H:%M")  # noqa: DTZ007


class GetIvr2DirEntryAudioFiles(GetIvr2DirEntryFiles):
    duration: float | None = None
    duration_str: str | None = Field(default=None, alias="durationStr")
    customer_did: str | None = Field(default=None, alias="customerDid")
    meta: dict | None = None
    date: str | None = None
    source: str | None = None
    phone: str | None = None
    ip: str | None = None


class GetIvr2DirEntryDir(GetIvr2DirEntry):
    ext_type: str | None = Field(default=None, alias="extType")
    ext_title: str | None = Field(default=None, alias="extTitle")


class GetIvr2Dir(BaseModel):
    ext_ini: dict = Field(alias="extIni")
    this_path: str = Field(alias="thisPath")
    parent_path: str = Field(alias="parentPath")
    dirs: list[GetIvr2DirEntryDir]
    files: list[GetIvr2DirEntryAudioFiles]
    ini: list[GetIvr2DirEntryFiles]
    messages: list[GetIvr2DirEntryAudioFiles]
    html: list[GetIvr2DirEntryFiles]
    msg_descriptions: dict = Field(alias="msgDescriptions")


class GetFile(BaseModel):
    file: GetIvr2DirEntryAudioFiles


class FileActionEntry(BaseModel):
    what: str
    target: str
    success: bool


class FileAction(BaseModel):
    reports: list[FileActionEntry]
    message: str
    success: bool
    action: Literal["copy", "move", "delete"]


class GetTextFile(BaseModel):
    contents: str
    file: GetIvr2DirEntryFiles


class CallAction(BaseModel):
    calls: list[Call]
    action: str
    calls_count: int = Field(alias="callsCount")


class GetIncomingSum(BaseModel):
    from_date: str = Field(alias="fromDate")
    to_date: str = Field(alias="toDate")
    direct: float
    transfer_in: float = Field(alias="transferIn")
    transfer_out: float = Field(alias="transferOut")


class GetSmsOutLogEntry(BaseModel):
    CallerId: str
    To: str
    Message: str
    Billing: float
    RunBy: str
    Time: str
    DeliveryReport: str


class GetSmsOutLog(BaseModel):
    rows: list[GetSmsOutLogEntry]


class TokenData(BaseModel):
    remote_ip: str = Field(alias="remoteIP")
    session_type: str = Field(alias="sessionType")
    create_time: datetime = Field(alias="createTime")
    last_request: datetime = Field(alias="lastRequest")
    double_auth_status: bool = Field(alias="doubleAuthStatus")
    validation_calls: int = Field(alias="validationCalls")
    token: str
    mfa_status: bool = Field(alias="mfaStatus")
    mfa_real_valid: bool = Field(alias="mfaRealValid")
    mfa_request_id: int | None = Field(alias="mfaRequestId")
    mfa_valid_reason: str = Field(alias="mfaValidReason")


class ValidationToken(BaseModel):
    token_data: TokenData = Field(alias="tokenData")


class GetLoginLogEntry(BaseModel):
    remote_ip: str = Field(alias="remoteIP")
    session_type: str = Field(alias="sessionType")
    action_timestamp: datetime = Field(alias="actionTimestamp")
    username: str
    successful: bool


class GetLoginLog(BaseModel):
    data: list[GetLoginLogEntry]


class GetAllSessionsEntry(BaseModel):
    id: int
    token: str
    active: bool
    selected_did: str | None = Field(alias="selectedDID")
    remote_ip: str = Field(alias="remoteIP")
    session_type: str = Field(alias="sessionType")
    create_time: datetime = Field(alias="createTime")
    last_request: datetime = Field(alias="lastRequest")
    double_auth_status: bool = Field(alias="doubleAuthStatus")
    mfa_status: bool | None = Field(alias="mfaStatus")
    mfa_real_valid: bool | None = Field(alias="mfaRealValid")
    mfa_request_id: int | None = Field(alias="mfaRequestId")
    mfa_valid_reason: str | None = Field(alias="mfaValidReason")


class GetAllSessions(BaseModel):
    data: list[GetAllSessionsEntry]
    count: int


class RunTzintuk(BaseModel):
    caller_id: str = Field(alias="callerId")
    calls_count: int = Field(alias="callsCount")
    verify_code: str | None = Field(alias="verifyCode")
    biling_per_call: float = Field(alias="bilingPerCall")
    biling: float
    errors: dict[str, str]
    calls_timeout: int = Field(alias="callsTimeout")
    campaign_id: str = Field(alias="campaignId")


class TzintukimListManagementGetListsEntry(BaseModel):
    list_name: str = Field(alias="listName")
    subscribers: int
    blocked: int
    active: int


class TzintukimListManagementGetLists(BaseModel):
    lists: list[TzintukimListManagementGetListsEntry]


class TzintukimListManagementGetListEntriesEntry1(BaseModel):
    phone: str
    name: str | None
    active: bool


class TzintukimListManagementGetListEntriesEntry2(BaseModel):
    phone: str
    name: str | None


class TzintukimListManagementGetListEntries(BaseModel):
    list_name: str = Field(alias="listName")
    count_subscribers: int = Field(alias="countSubscribers")
    counts_blocked: int = Field(alias="countsBlocked")
    counts_active: int = Field(alias="countsActive")
    enteres: list[TzintukimListManagementGetListEntriesEntry1]
    blocked: list[TzintukimListManagementGetListEntriesEntry2]
    active: list[TzintukimListManagementGetListEntriesEntry2]


class TzintukimListManagementGetLogListEntry(BaseModel):
    folder: str = Field(alias="Folder")
    customer_did: str = Field(alias="CustomerDID")
    phone: str = Field(alias="Phone")
    action_date: date = Field(alias="Date")
    action_time: time = Field(alias="Time")
    type_operation: str = Field(alias="TypeOperation")
    phone_action: str = Field(alias="PhoneAction")

    @field_validator("action_date", mode="before")
    def validate_action_date(cls, value: str) -> date:  # noqa: N805
        return datetime.strptime(value, "%d/%m/%Y").date()  # noqa: DTZ007


class TzintukimListManagementGetLogList(BaseModel):
    events: list[TzintukimListManagementGetLogListEntry]


class SendFax(BaseModel):
    caller_id: str = Field(alias="callerId")
    campaign_id: str = Field(alias="CampaignId")
    delivery_url: str = Field(alias="deliveryUrl")
    file_name_send: str = Field(alias="fileNameSend")
    calls_count: int = Field(alias="callsCount")
    biling_per_call: float = Field(alias="bilingPerCall")
    biling: float


class SendSms(BaseModel):
    message: str
    sender_id: str = Field(alias="from")
    send_count: int = Field(alias="sendCount")
    billing: float = Field(alias="Billing")
    oks: list[str]
    errors: dict[str, str]


class CreateBridgeCall(BaseModel):
    campaign_id: str = Field(alias="CampaignId")
    ok_calls: int = Field(alias="OKCalls")
    error_calls: dict[str, str] = Field(alias="ErrorCalls")
    billing: float = Field(alias="Billing")
    send_mail_in_call: bool = Field(alias="SendMailInCall")
    record_call: bool = Field(alias="RecordCall")
    customer_unit: float = Field(alias="CustomerUnit")
    caller_id: str = Field(alias="CallerId")
    phones: list[str] = Field(alias="Phones")
    send_mail_in_call_to: str | None = Field(default=None, alias="SendMailInCallTo")


class GetQueueRealTime(BaseModel):
    queue_data: QueueData = Field(alias="queueData")
    members: list[QueueRealTimeMember]
    entries: list[QueueRealTimeEntry]


class QueueData(BaseModel):
    abandoned: int = Field(alias="Abandoned")
    calls: int = Field(alias="Calls")
    completed: int = Field(alias="Completed")
    talk_time: int = Field(alias="TalkTime")
    hold_time: int = Field(alias="Holdtime")
    max: int = Field(alias="Max")
    strategy: str = Field(alias="Strategy")


class QueueRealTimeMember(BaseModel):
    agent: str
    status: str = Field(alias="Status")
    calls_taken: int = Field(alias="CallsTaken")
    last_call_unit_time: str = Field(alias="LastCallUnitTime")
    last_call: datetime | None = Field(alias="LastCall")
    last_call_ago: str | None = Field(alias="LastCallAgo")
    paused: bool = Field(alias="Paused")
    penalty: str = Field(alias="Penalty")

    @field_validator("last_call", mode="before")
    def parse_last_call(cls, value: str | None) -> datetime | None:  # noqa: N805
        if value is None:
            return None
        return datetime.strptime(value, "%m/%d/%Y, %I:%M:%S %p")  # noqa: DTZ007


class QueueRealTimeEntry(BaseModel):
    phone: str
    wait: int = Field(alias="Wait")
    wait_ago: str = Field(alias="WaitAgo")
    position: int = Field(alias="Position")
    call_id: str = Field(alias="CallId")


class GetCustomerData(BaseModel):
    main_did: str = Field(alias="mainDid")
    secondary_dids: list[SecondaryDidEntry]
    caller_ids: list[CallerIDEntry] = Field(alias="callerIds")
    name: str
    expired_units: bool = Field(alias="expiredUnits")
    units_expire_date: datetime = Field(alias="unitsExpireDate")
    sms_units_expire_date: datetime | None = Field(alias="smsUnitsExpireDate")
    email: str
    organization: str
    contact_name: str = Field(alias="contactName")
    phones: str
    invoice_name: str = Field(alias="invoiceName")
    invoice_address: str = Field(alias="invoiceAddress")
    fax: str
    access_password: str = Field(alias="accessPassword")
    units: float
    sms_units: float = Field(alias="smsUnits")
    record_password: str = Field(alias="recordPassword")
    reseller_credit_file: str = Field(alias="resellerCreditFile")
    system_site: str = Field(alias="systemSite")
    pirsum_phone_status: bool = Field(alias="pirsumPhoneStatus")
    ivr_type: str = Field(alias="ivrType")


class SecondaryDidEntry(BaseModel):
    id: int
    did: str
    usage: str | None


class CallerIDEntry(BaseModel):
    caller_id: str = Field(alias="callerId")
    expiry_date: datetime | None = Field(alias="expiryDate")


class ViewCampaignReports(BaseModel):
    campaign_data: dict = Field(alias="CampaignData")


class GetTasks(BaseModel):
    tasks: list[GetTasksEntry]


class GetTasksEntry(BaseModel):
    id: int
    description: str
    task_type: str = Field(alias="type")
    create_ts: datetime = Field(alias="createTs")
    status: str
    active: bool
    send_mail_in_end: bool = Field(alias="sendMailInEnd")
    send_mail_in_error: bool = Field(alias="sendMailInError")
    next_run: datetime = Field(alias="nextRun")


class GetTasksData(GetTasksEntry):
    create_by: str = Field(alias="createBy")
    update_ts: datetime | None = Field(alias="updateTs")
    last_run: datetime | None = Field(alias="lastRun")
    minute: int | None
    hour: int | None
    year: int | None
    day: int | None
    month: int | None
    days_of_week: list[int] | None
    action_data: dict
    check_is_kodesh: bool

    @field_validator("action_data", mode="before")
    def validate_action_data(cls, value: dict) -> dict:  # noqa: N805
        if isinstance(value, str):
            return json.loads(value)
        return value

    @field_validator("days_of_week", mode="before")
    def validate_days_of_week(cls, value: str | None) -> list[int] | None:  # noqa: N805
        if value is None:
            return None
        if isinstance(value, str):
            return [int(x) for x in value.split(",") if x.isdigit()]
        return value


class GetTasksLogs(BaseModel):
    logs: list[GetTasksLogsEntry]


class GetTasksLogsEntry(BaseModel):
    id: int
    succeeded: bool
    error_message: str | None
    ts: datetime


class CreateTask(BaseModel):
    job_id: int = Field(alias="jobId")
    action_data: CreateTaskActionData = Field(alias="ActionData")


class CreateTaskActionData(BaseModel):
    minute: int | None
    hour: int | None
    year: int | None
    day: int | None
    month: int | None
    days_of_week: list[int] | None
    action_data: dict
    description: str | None
    active: bool
    send_mail_in_end: bool = Field(alias="sendMailInEnd")
    send_mail_in_error: bool = Field(alias="sendMailInError")
    check_is_kodesh: bool = Field(alias="checkIsKodesh")

    @field_validator("days_of_week", mode="before")
    def validate_days_of_week(cls, value: str | None) -> list[int] | None:  # noqa: N805
        if value is None:
            return None
        if isinstance(value, str):
            return [int(x) for x in value.split(",") if x.isdigit()]
        return value


class SendTTS(BaseModel):
    campaign_id: str = Field(alias="CampaignId")
    ok_calls: int = Field(alias="OKCalls")
    error_calls: dict = Field(alias="ErrorCalls")
    billing: float
    units: float
    tts_rate: int = Field(alias="TTS_RATE")
    tts_voice: str = Field(alias="TTS_VOICE")


class GetCustomerSmsTransactions(BaseModel):
    rows: list[SmsTransaction]


class SmsTransaction(BaseModel):
    transaction_time: datetime = Field(alias="transactionTime")
    amount: float
    description: str
    new_balance: float = Field(alias="newBalance")
    expire_date: datetime = Field(alias="expireDate")
    who: str


class CreateSipAccount(BaseModel):
    account_id: str = Field(alias="accountID")
    account_number: int = Field(alias="accountNumber")
    password: str = Field(alias="PASS")


class GetSipAccountsInCustomer(BaseModel):
    accounts: list[GetSipAccountsInCustomerEntry]
    account_limit: int = Field(alias="accountLimit")


class GetSipAccountsInCustomerEntry(BaseModel):
    id: str
    account_number: int = Field(alias="accountNumber")
    customer_extension: int | None = Field(alias="customerExtension")
    transport: str
    caller_id: str = Field(alias="callerid")
    special_caller_id: str | None = Field(alias="specialCallerID")
    password: str
    created_date: datetime
    contacts_count: int = Field(alias="contactsCount")


class GetIVR2DirStats(BaseModel):
    folder_type: str | None = Field(alias="type")
    this_path: str = Field(alias="thisPath")
    parent_path: str = Field(alias="parentPath")
    dirs_count: int = Field(alias="dirsCount")
    files_count: int = Field(alias="filesCount")
    content_files_count: int = Field(alias="contentFilesCount")
    min_file: GetIvr2DirEntryAudioFiles | None = Field(alias="minFile")
    max_file: GetIvr2DirEntryAudioFiles | None = Field(alias="maxFile")


class CallExtensionBridging(BaseModel):
    module: str
    caller_id: str = Field(alias="callerId")
    calls_count: int = Field(alias="callsCount")
    billing_per_call: float = Field(alias="bilingPerCall")
    errors: dict[str, str]
    calls_timeout: int = Field(alias="callsTimeout")
    campaign_id: str = Field(alias="campaignId")


class SipGetContexts(BaseModel):
    contexts: list[SipGetContextsEntry]


class SipGetContextsEntry(BaseModel):
    uri: str
    user_agent: str
    via_addr: str
    via_port: int
    end_point: str = Field(alias="endpoint")
    expiration_time: datetime


class GetSipAccountsRegisteredStatus(BaseModel):
    accounts: list[GetSipAccountsRegisteredStatusEntry]


class GetSipAccountsRegisteredStatusEntry(BaseModel):
    user_name: str = Field(alias="userName")
    created_date: datetime = Field(alias="createdDate")
    registered: bool


class GetApprovedCallerIDs(BaseModel):
    call: GetApprovedCallerIDsCall
    sms: GetApprovedCallerIDsSms


class GetApprovedCallerIDsCall(BaseModel):
    main_did: str = Field(alias="mainDid")
    secondary_dids: list[str] = Field(alias="secondaryDids")
    caller_ids: list[str] = Field(alias="callerIds")


class GetApprovedCallerIDsSms(BaseModel):
    sms_id: str | None = Field(alias="smsId")
    allow_text: bool = Field(alias="allowText")


class IsCallerIDApproved(BaseModel):
    parsed_caller_id: str = Field(alias="parsedCallerId")
    is_approved: bool = Field(alias="isApproved")
    reason: str


class QueueCallBackGetQueues(BaseModel):
    callback_list: list[QueueCallBackGetQueuesEntry] = Field(alias="callbackList")


class QueueCallBackGetQueuesEntry(BaseModel):
    id: int
    path: str
    queue_path: str
    caller_id: str
    callback_times: str
    max_waiting_time: int
    max_waiting_customers: int
    waiting_customers: int
    open: bool


class QueueCallBackGetList(BaseModel):
    callback_list: list[QueueCallBackGetListEntry] = Field(alias="callbackList")


class QueueCallBackGetListEntry(BaseModel):
    id: int
    calling_number: str
    status: str
    date_time: datetime
    attempts: int
    last_attempt: str | None


class GetIncomingSms(BaseModel):
    rows: list[GetIncomingSmsEntry]


class GetIncomingSmsEntry(BaseModel):
    source: str
    destination: str
    message: str
    receive_date: datetime


class MfaSessionIsPass(BaseModel):
    is_available: bool = Field(alias="isAvailable")
    is_pass: bool = Field(alias="isPass")
    pass_reason: str | None = Field(alias="passReason")
    is_pass_in_this_session: bool = Field(alias="isPassInThisSession")


class MfaSessionGetMfaMethods(MfaSessionIsPass):
    mfa_methods: list[MfaSessionGetMfaMethodsEntry] = Field(alias="mfaMethods")


class MfaSessionGetMfaMethodsEntry(BaseModel):
    id: int = Field(alias="ID")
    status: str = Field(alias="STATUS")
    mfa_method_id: int = Field(alias="MFA_METHOD_ID")
    nike: str = Field(alias="NIKE")
    note: str = Field(alias="NOTE")
    send_type: list[str] = Field(alias="SEND_TYPE")
    value: str = Field(alias="VALUE")
    expired_date: datetime = Field(alias="EXPIRED_DATE")
    last_used: datetime = Field(alias="LAST_USED")


class MfaSessionValidMfa(BaseModel):
    mfa_valid_status: str
    mfa_valid_trys: int
    mfa_valid_left: int
    mfa_valid_message: str


class MfaSessionGetMfaTrustTokens(BaseModel):
    trust_tokens: list[MfaSessionGetMfaTrustTokensEntry] = Field(alias="trustTokens")


class MfaSessionGetMfaTrustTokensEntry(BaseModel):
    id: int
    trust_key_type: str
    create_by: str
    create_date: datetime
    update_by: str | None
    update_date: datetime | None
    last_use: datetime | None
    trust_note: str


class MfaSessionSetMfaTrustIps(BaseModel):
    ok_count: int = Field(alias="okCount")
    save: bool
    valid_new_list: list[str]
    errors: list[str]
