import json
from datetime import date, datetime
from types import TracebackType
from typing import Any, Literal, Self, overload
from uuid import uuid4

import requests

from . import input_types, types
from ._yemot_api_base import YemotBase
from .exceptions import YemotAPIError

__all__ = [
    "Yemot"
]


class Yemot(YemotBase):
    BASE_URL = "https://www.call2all.co.il/ym/api/"

    def __init__(
            self,
            token: str
    ) -> None:
        self.token = token
        self._session: requests.Session | None = None

    def close(self) -> None:
        if self._session:
            self._session.close()
            self._session = None

    def _get_session(self) -> requests.Session:
        if self._session is None:
            self._session = requests.Session()
        return self._session

    def _get(self, end_point: str, params: dict[str, Any] | None = None, *, default_params: bool = True) -> dict[Any, Any]:
        if params is None:
            params = {}
        url = f"{self.BASE_URL}{end_point}"
        if default_params:
            params.update(self.params)
        client = self._get_session()
        response = client.get(url, params=params)
        json_response = response.json()
        self._check_response(json_response)
        return json_response

    def _post(self, end_point: str, data: dict[str, Any] | None = None) -> dict[Any, Any]:
        if data is None:
            data = {}
        url = f"{self.BASE_URL}{end_point}"
        data.update(self.params)
        client = self._get_session()
        response = client.post(url, json=data)
        json_response = response.json()
        self._check_response(json_response)
        return json_response

    def _post_multipart(self, end_point: str, files: dict[str, Any], data: dict[str, Any] | None = None) -> dict[Any, Any]:
        if data is None:
            data = {}
        url = f"{self.BASE_URL}{end_point}"
        data.update(self.params)
        client = self._get_session()
        response = client.post(url, files=files, data=data)
        json_response = response.json()
        self._check_response(json_response)
        return json_response

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None) -> None:
        if self._session:
            self._session.close()

    def __del__(self) -> None:
        if self._session:
            self._session.close()

    def login(self, user_name: str, password: str) -> str:
        """https://f2.freeivr.co.il/post/24253 ."""
        end_point = "Login"
        params = {
            "username": user_name,
            "password": password
        }
        response = self._get(end_point, params, default_params=False)
        token = response["token"]
        self.token = token
        return token

    def logout(self) -> bool:
        """https://f2.freeivr.co.il/post/24259 ."""
        end_point = "Logout"
        params = {
            "token": self.token
        }
        response = self._get(end_point, params, default_params=False)
        return response["responseStatus"] == "OK"

    def get_session(self) -> types.GetSession:
        """https://f2.freeivr.co.il/post/24262 ."""
        end_point = "GetSession"
        response = self._get(end_point)
        return types.GetSession(**response)

    def set_password(self, new_password: str, password: str) -> bool:
        """https://f2.freeivr.co.il/post/24341 ."""
        end_point = "SetPassword"
        params = {
            "newPassword": new_password,
            "password": password
        }
        response = self._get(end_point, params)
        return response["responseStatus"] == "OK"

    def set_customer_details(
        self,
        name: str | None = None,
        email: str | None = None,
        organization: str | None = None,
        contact_name: str | None = None,
        phones: str | None = None,
        invoice_name: str | None = None,
        invoice_address: str | None = None,
        fax: str | None = None,
        access_password: str | int | None = None,
        record_password: str | int | None = None
    ) -> bool:
        """https://f2.freeivr.co.il/post/24922 ."""
        end_point = "SetCustomerDetails"
        params = {
            "name": name,
            "email": email,
            "organization": organization,
            "contactName": contact_name,
            "phones": phones,
            "invoiceName": invoice_name,
            "invoiceAddress": invoice_address,
            "fax": fax,
            "accessPassword": access_password,
            "recordPassword": record_password
        }
        response = self._get(end_point, params)
        return response["responseStatus"] == "OK"

    def get_transactions(
        self,
        from_: str | None = None,
        limit: int | None = None,
        filter_: str | None = None
    ) -> types.GetTransactions:
        """https://f2.freeivr.co.il/post/24944 ."""
        end_point = "GetTransactions"
        params = {
            "from": from_,
            "limit": limit,
            "filter": filter_
        }
        response = self._get(end_point, params)
        return types.GetTransactions(**response)

    def transfer_units(self, destination: str, amount: int) -> types.TransferUnits:
        """https://f2.freeivr.co.il/post/25135 ."""
        end_point = "TransferUnits"
        params = {
            "destination": destination,
            "amount": amount
        }
        response = self._post(end_point, params)
        return types.TransferUnits(**response)

    def get_incoming_calls(self) -> types.GetIncomingCalls:
        """https://f2.freeivr.co.il/post/25141 ."""
        end_point = "GetIncomingCalls"
        response = self._get(end_point, self.params)
        return types.GetIncomingCalls(**response)

    def upload_file(
        self,
        path: str,
        blob: bytes,
        file_name: str,
        base_path: str = "ivr2:",
        convert_audio: bool | None = None,
        auto_numbering: bool | None = None,
        tts: bool | None = None
    ) -> types.UploadFile:
        """https://f2.freeivr.co.il/post/32031 ."""
        total_size = len(blob)
        chunk_size = 49 * 1024 * 1024
        chunks = [blob[offset:offset + chunk_size] for offset in range(0, total_size, chunk_size)]
        if len(chunks) == 1:
            return self._upload_small_file(path, blob, file_name, base_path, convert_audio, auto_numbering=auto_numbering, tts=tts)
        return self._upload_large_file(path, chunks, file_name, total_size, base_path, convert_audio=convert_audio, auto_numbering=auto_numbering, tts=tts)

    def _upload_small_file(
        self,
        path: str,
        blob: bytes,
        file_name: str,
        base_path: str,
        convert_audio: bool | None = None,
        auto_numbering: bool | None = None,
        tts: bool | None = None
    ) -> types.UploadFile:
        data = {
            "path": f"{base_path}{path}",
        }
        if convert_audio is not None:
            data["convertAudio"] = int(convert_audio)
        if auto_numbering is not None:
            data["autoNumbering"] = "true" if auto_numbering is True else "false" if auto_numbering is False else None
        if tts is not None:
            data["tts"] = int(tts)
        files = {"file": (file_name, blob)}
        response = self._post_multipart("UploadFile", files=files, data=data)
        return types.UploadFile(**response)

    def _upload_large_file(
        self,
        path: str,
        chunks: list[bytes],
        file_name: str,
        content_size: int,
        base_path: str,
        convert_audio: bool | None = None,
        auto_numbering: bool | None = None,
        tts: bool | None = None
    ) -> types.UploadFile:
        end_point = "UploadFile"
        qquuid = str(uuid4())
        offset = 0
        for index, chunk in enumerate(chunks):
            data = {
                "path": f"{base_path}{path}",
                "qquuid": qquuid,
                "uploader": "yemot-admin",
                "qqfilename": file_name,
                "qqtotalfilesize": content_size,
                "qqtotalparts": len(chunks),
                "qqchunksize": len(chunk),
                "qqpartbyteoffset": offset,
                "qqpartindex": index,
            }
            if convert_audio is not None:
                data["convertAudio"] = int(convert_audio)
            if auto_numbering is not None:
                data["autoNumbering"] = "true" if auto_numbering is True else "false" if auto_numbering is False else None
            if tts is not None:
                data["tts"] = int(tts)
            # data.update(self.params)
            files = {
                "qqfile": chunk,
            }
            url = f"{self.BASE_URL}{end_point}"
            data.update(self.params)
            client = self._get_session()
            response = client.post(url, files=files, data=data).json()
            if "success" not in response or not response["success"]:
                raise YemotAPIError("error", None, response.get("error", "Unknown error"))
            offset += len(chunk)

        data = {
            "path": f"{base_path}{path}",
            "uploader": "yemot-admin",
            "qquuid": qquuid,
            "qqfilename": file_name,
            "qqtotalfilesize": content_size,
            "qqtotalparts": len(chunks),
        }
        if convert_audio is not None:
            data["convertAudio"] = int(convert_audio)
        if auto_numbering is not None:
            data["autoNumbering"] = "true" if auto_numbering is True else "false" if auto_numbering is False else None
        if tts is not None:
            data["tts"] = int(tts)
        data.update(self.params)
        client = self._get_session()
        response = client.post(f"{self.BASE_URL}UploadFile?done", data=data).json()
        return types.UploadFile(**response)

    def download_file(self, path: str, base_path: str = "ivr2:/") -> bytes:
        """https://f2.freeivr.co.il/post/32032 ."""
        params = {
            "path": f"{base_path}{path}"
        }
        params.update(self.params)
        url = f"{self.BASE_URL}DownloadFile"
        client = self._get_session()
        response = client.get(url, params=params)
        content_type = response.headers.get("Content-Type")
        if content_type == "application/octet-stream":
            return response.content
        if content_type == "application/json; charset=utf-8":
            json_error = response.json()
            self._check_response(json_error)
        raise YemotAPIError(
            "ERROR",
            404,
            response.text
        )

    def get_templates(self) -> types.GetTemplates:
        """https://f2.freeivr.co.il/post/32033 ."""
        end_point = "GetTemplates"
        response = self._get(end_point=end_point)
        return types.GetTemplates(**response)

    def update_template(
        self,
        template_id: int,
        description: str | None = None,
        caller_id: str | None = None,
        incoming_policy: Literal["OPEN", "BLACKLIST", "WHITELIST", "BLOCKED"] | None = None,
        customer_default: Literal[1] | None = None,
        max_active_channels: int | None = None,
        max_bridged_channels: int | None = None,
        originate_timeout: float | None = None,
        vm_detect: bool | None = None,
        filter_enabled: bool | None = None,
        max_dial_attempts: int | None = None,
        redial_wait: float | None = None,
        redial_policy: Literal["NONE", "CONGESTIONS", "FAILED"] | None = None,
        yemot_context: Literal["SIMPLE", "REPEAT", "MESSAGE", "VOICEMAIL", "BRIDGE"] | None = None,
        bridge_to: str | None = None,
        play_private_msg: bool | None = None,
        remove_request: Literal["SILENT", "WITH_MESSAGE"] | None = None
    ) -> types.GetTemplates:
        """https://f2.freeivr.co.il/post/32034 ."""
        end_point = "UpdateTemplate"
        bool_to_int = {
            "vmDetect": vm_detect,
            "filterEnabled": filter_enabled,
            "playPrivateMsg": play_private_msg,
        }
        other_params = {
            "templateId": template_id,
            "description": description,
            "callerId": caller_id,
            "incomingPolicy": incoming_policy,
            "customerDefault": customer_default,
            "maxActiveChannels": max_active_channels,
            "maxBridgedChannels": max_bridged_channels,
            "originateTimeout": originate_timeout,
            "maxDialAttempts": max_dial_attempts,
            "redialWait": redial_wait,
            "redialPolicy": redial_policy,
            "yemotContext": yemot_context,
            "bridgeTo": bridge_to,
            "removeRequest": remove_request,
        }
        params = self._filter_params(bool_to_int, other_params)
        response = self._post(end_point, params)
        return types.GetTemplates(**response)

    def create_template(self, description: str) -> int:
        """https://f2.freeivr.co.il/post/32037 ."""
        end_point = "CreateTemplate"
        params = {
            "description": description
        }
        response = self._get(end_point=end_point, params=params)
        return response["templateId"]

    def delete_template(self, template_id: int | str) -> bool:
        """https://f2.freeivr.co.il/post/32038 ."""
        end_point = "DeleteTemplate"
        params = {
            "templateId": template_id
        }
        response = self._get(end_point=end_point, params=params)
        return response["responseStatus"] == "OK"

    def get_template_entries(self, template_id: str | int) -> types.GetTemplateEntries:
        """https://f2.freeivr.co.il/post/32039 ."""
        end_point = "GetTemplateEntries"
        params = {
            "templateId": template_id
        }
        response = self._get(end_point, params)
        return types.GetTemplateEntries(**response)

    def update_template_entry(
        self,
        template_id: int,
        row_id: int,
        phone: str,
        name: str | None = None,
        more_info: str | None = None,
        *,
        blocked: bool | None = None
    ) -> bool:
        """https://f2.freeivr.co.il/post/32040 ."""
        end_point = "UpdateTemplateEntry"
        bool_to_int = {
            "blocked": blocked
        }
        other_params = {
            "templateId": template_id,
            "rowid": row_id,
            "phone": phone,
            "name": name,
            "moreinfo": more_info
        }
        params = self._filter_params(bool_to_int_params=bool_to_int, other_params=other_params)
        response = self._get(end_point=end_point, params=params)
        return response["responseStatus"] == "OK"

    def update_template_entries(self, template_id: int, row_ids: list[int], action: input_types.UpdateTemplateEntries) -> bool:
        """https://f2.freeivr.co.il/post/32041 ."""
        end_point = "UpdateTemplateEntries"
        params = {
            "templateId": template_id,
            "rowids": "-".join(map(str, row_ids)),
            "action": action
        }
        response = self._post(end_point=end_point, data=params)
        return response["responseStatus"] == "OK"

    def clear_template_entries(self, template_id: int) -> bool:
        """https://f2.freeivr.co.il/post/32042 ."""
        end_point = "ClearTemplateEntries"
        params = {
            "templateId": template_id
        }
        response = self._get(end_point=end_point, params=params)
        return response["responseStatus"] == "OK"

    def upload_phone_list(
        self,
        data: list[str],
        template_id: int,
        name_columns: int = 1,
        default_prefix: Literal["02", "03", "04", "08", "09", "077", "072", "073"] | None = None,
        delimiter: str = ",",
        update_type: input_types.UploadPhoneList = input_types.UploadPhoneList.UPDATE,
        *,
        blocked: bool = False
    ) -> types.UploadPhoneList:
        """https://f2.freeivr.co.il/post/32043 ."""
        end_point = "UploadPhoneList"
        bool_to_int_params = {"blocked": blocked}
        other_params = {
            "templateId": template_id,
            "data": "\n".join(data),
            "nameColumns": name_columns,
            "defaultPrefix": default_prefix,
            "delimiter": delimiter,
            "updateType": update_type
        }
        payload = self._filter_params(bool_to_int_params, other_params)
        response = self._post(end_point=end_point, data=payload)
        return types.UploadPhoneList(**response)

    def run_campaign(
            self,
            template_id: int | None = None,
            caller_id: str | None = None,
            phones: list[str] | dict[str, input_types.RunCampaignPhonesDict] | None = None,
            *,
            tts_mode: bool | None = None,
            with_sms: bool | None = None
    ) -> types.RunCampaign:
        """https://f2.freeivr.co.il/post/32044 ."""
        end_point = "RunCampaign"
        phones_param = None
        if phones is not None:
            phones_param = phones if isinstance(phones, dict) else ":".join(phones)
        bool_to_int = {
            "ttsMode": tts_mode,
            "withSms": with_sms
        }
        other_params = {
            "callerId": caller_id,
            "phones": phones_param,
            "templateId": template_id
        }
        params = self._filter_params(bool_to_int, other_params)
        response = self._post(end_point=end_point, data=params)
        return types.RunCampaign(**response)

    def get_campaign_status(
        self,
        campaign_id: str,
        entries: input_types.CampaignStatusEntries | None = None,
        min_range: int | None = None,
        max_range: int | None = None,
        all_entries: bool | None = None
    ) -> types.CampaignStatus:
        """https://f2.freeivr.co.il/post/32045 ."""
        end_point = "GetCampaignStatus"
        if all_entries is True:
            range_param = ":"
        elif min_range is not None or max_range is not None:
            range_param = f"{min_range}:{max_range}"
        else:
            range_param = None
        other_params = {
            "campaignId": campaign_id,
            "entries": entries,
            "range": range_param
        }
        params = self._filter_params(other_params=other_params)
        response = self._get(end_point=end_point, params=params)
        return types.CampaignStatus(**response)

    def download_campaign_report(self, campaign_id: str) -> str:
        """https://f2.freeivr.co.il/post/32046 ."""
        end_point = "DownloadCampaignReport"
        params = {
            "campaignId": campaign_id
        }
        params.update(self.params)
        client = self._get_session()
        response = client.get(f"{self.BASE_URL}{end_point}", params=params)
        if response.status_code == 200:
            if response.headers.get("Content-Type") == "application/json; charset=utf-8":
                json_error = response.json()
                self._check_response(json_error)
            return response.text
        raise YemotAPIError("ERROR", response.status_code, response.text)

    def get_active_campaigns(self) -> types.GetActiveCampaigns:
        """https://f2.freeivr.co.il/post/32047 ."""
        end_point = "GetActiveCampaigns"
        response = self._get(end_point=end_point)
        return types.GetActiveCampaigns(**response)

    @overload
    def campaign_action(
        self,
        campaign_id: str,
        action: Literal[input_types.CampaignAction.ADD, input_types.CampaignAction.BLOCK, input_types.CampaignAction.HANGUP],
        value: list[str] | dict[str, str | input_types.RunCampaignPhonesDict]
    ) -> types.CampaignAction:
        ...

    @overload
    def campaign_action(self, campaign_id: str, action: Literal[input_types.CampaignAction.STOP]) -> types.CampaignAction:
        ...

    @overload
    def campaign_action(
        self,
        campaign_id: str,
        action: Literal[input_types.CampaignAction.SET_PAUSED],
        value: bool
    ) -> types.CampaignAction:
        ...

    @overload
    def campaign_action(
        self,
        campaign_id: str,
        action: Literal[input_types.CampaignAction.SET_MAX_ACTIVE_CHANNELS, input_types.CampaignAction.SET_MAX_BRIDGED_CHANNELS],
        value: int
    ) -> types.CampaignAction:
        ...

    def campaign_action(
        self,
        campaign_id: str,
        action: input_types.CampaignAction,
        value: list[str] | dict[str, str | input_types.RunCampaignPhonesDict] | bool | int | None = None
    ) -> types.CampaignAction:
        """https://f2.freeivr.co.il/post/32048 ."""
        end_point = "CampaignAction"
        bool_to_int_params = {}

        if action == input_types.CampaignAction.SET_PAUSED and isinstance(value, bool):
            bool_to_int_params["value"] = value
            param_value = None
        elif action in [input_types.CampaignAction.ADD, input_types.CampaignAction.BLOCK, input_types.CampaignAction.HANGUP] and not isinstance(value, dict):
            param_value = ":".join(value)  # pyright: ignore[reportArgumentType, reportCallIssue]
        else:
            param_value = value
        other_params = {
            "campaignId": campaign_id,
            "action": action,
            "value": param_value
        }
        params = self._filter_params(bool_to_int_params, other_params)
        response = self._post(end_point=end_point, data=params)
        return types.CampaignAction(**response)

    def schedule_campaign(self, template_id: int, time: str) -> types.ScheduleCampaign:
        """https://f2.freeivr.co.il/post/32049 ."""
        end_point = "ScheduleCampaign"
        params = {
            "templateId": template_id,
            "time": time
        }
        response = self._post(end_point, params)
        return types.ScheduleCampaign(**response)

    def get_scheduled_campaigns(
            self,
            type_: Literal["PENDING", "SUCCESSFUL", "FAILED"],
            order: Literal["asc", "desc"],
            from_: int | None = None,
            limit: int | None = None
    ) -> types.GetScheduledCampaigns:
        """https://f2.freeivr.co.il/post/32050 ."""
        end_point = "GetScheduledCampaigns"
        other_params = {
            "type": type_,
            "order": order,
            "from": from_,
            "limit": limit
        }
        params = self._filter_params(other_params=other_params)
        response = self._get(end_point=end_point, params=params)
        return types.GetScheduledCampaigns(**response)

    def delete_scheduled_campaign(self, sche_did: int) -> bool:
        """https://f2.freeivr.co.il/post/32051 ."""
        end_point = "DeleteScheduledCampaign"
        params = {
            "schedId": sche_did
        }
        response = self._get(end_point=end_point, params=params)
        return response["responseStatus"] == "OK"

    def get_ivr2_dir(
        self,
        path: str,
        files_from: int = 0,
        files_limit: int | None = None,
        order_by: input_types.GetIvr2DirOrderBy = input_types.GetIvr2DirOrderBy.NAME,
        order_dir: Literal["asc", "desc"] | None = None
    ) -> types.GetIvr2Dir:
        """https://f2.freeivr.co.il/post/32052 ."""
        end_point = "GetIVR2Dir"
        other_params = {
            "path": path,
            "filesFrom": files_from,
            "filesLimit": files_limit,
            "orderBy": order_by,
            "orderDir": order_dir
        }
        params = self._filter_params(other_params=other_params)
        response = self._get(end_point, params)
        return types.GetIvr2Dir(**response)

    def get_file(self, what: str, base_path: str = "ivr2:") -> types.GetFile:
        """https://f2.freeivr.co.il/post/32053 ."""
        end_point = "GetFile"
        params = {
            "what": f"{base_path}{what}"
        }
        response = self._get(end_point, params)
        return types.GetFile(**response)

    @overload
    def file_action(self, action: Literal[input_types.FileAction.DELETE], source_path: str, *, base_path: str = "ivr2:") -> types.FileAction:
        ...

    @overload
    def file_action(self, action: Literal[input_types.FileAction.COPY, input_types.FileAction.MOVE], source_path: str, target: str, *, base_path: str = "ivr2:") -> types.FileAction:
        ...

    def file_action(self, action: input_types.FileAction, source_path: str, target: str | None = None, *, base_path: str = "ivr2:") -> types.FileAction:
        """https://f2.freeivr.co.il/post/32054 ."""
        end_point = "FileAction"
        params = {
            "action": action,
            "what": f"{base_path}{source_path}"
        }
        if action in [input_types.FileAction.COPY, input_types.FileAction.MOVE]:
            params["target"] = f"{base_path}{target}"
        response = self._post(end_point, data=params)
        return types.FileAction(**response)

    def get_text_file(self, path: str, base_path: str = "ivr2:/") -> types.GetTextFile:
        """https://f2.freeivr.co.il/post/32055 ."""
        end_point = "GetTextFile"
        params = {
            "what": f"{base_path}{path}",
        }
        response = self._get(end_point, params)
        return types.GetTextFile(**response)

    def upload_text_file(self, path: str, text: str, base_path: str = "ivr2:/") -> bool:
        """https://f2.freeivr.co.il/post/32056 ."""
        end_point = "UploadTextFile"
        params = {
            "what": f"{base_path}{path}",
            "contents": text
        }
        response = self._post(end_point, params)
        return response["responseStatus"] == "OK"

    def update_extension(self, path: str | int, base_path: str = "ivr2:/", **settings: str) -> bool:
        """https://f2.freeivr.co.il/post/32060 ."""
        end_point = "UpdateExtension"
        params = {
            "path": f"{base_path}{path}"
        }
        settings.update(params)
        response = self._post(end_point, settings)
        return response["responseStatus"] == "OK"

    @overload
    def call_action(
        self,
        ids: list[str],
        action: Literal[
            input_types.CallAction.MOVE_CALL_TO,
            input_types.CallAction.ADD_TO_CONF_ROOM_DATA,
            input_types.CallAction.REMOVE_FROM_CONF_ROOM_DATA,
            input_types.CallAction.CONF_ROOM_NEW_GOTO,
            input_types.CallAction.SET_LANG
        ],
        value: str
    ) -> types.CallAction:
        ...

    @overload
    def call_action(
        self,
        ids: list[str],
        action: Literal[
            input_types.CallAction.REMOVE_USER_FROM_CONF_ROOM,
            input_types.CallAction.MUTE_USER_CONF_ROOM,
            input_types.CallAction.UN_MUTE_USER_CONF_ROOM,
            input_types.CallAction.LOWER_HAND_CONF_ROOM,
            input_types.CallAction.RAISE_HAND_CONF_ROOM
        ]
    ) -> types.CallAction:
        ...

    def call_action(self, ids: list[str], action: input_types.CallAction, value: str = "") -> types.CallAction:
        """https://f2.freeivr.co.il/post/52054 ."""
        end_point = "CallAction"
        params = {
            "ids": ":".join(ids),
            "action": f"{action}{value}"
        }
        response = self._post(end_point, params)
        return types.CallAction(**response)

    def get_incoming_sum(self, from_date: str | date | None = None, to_date: str | date | None = None) -> types.GetIncomingSum:
        """https://f2.freeivr.co.il/post/53911 ."""
        end_point = "GetIncomingSum"
        other_params = {
            "from": self._to_iso_date(from_date),
            "to": self._to_iso_date(to_date)
        }
        params = self._filter_params(other_params=other_params)
        response = self._get(end_point, params)
        return types.GetIncomingSum(**response)

    def get_sms_out_log(self, limit: int | None = None) -> types.GetSmsOutLog:
        """https://f2.freeivr.co.il/post/63910 ."""
        end_point = "GetSmsOutLog"
        params = {}
        if limit is not None:
            params["limit"] = limit
        response = self._get(end_point, params)
        return types.GetSmsOutLog(**response)

    def validation_token(self) -> types.ValidationToken:
        """https://f2.freeivr.co.il/post/64050 ."""
        end_point = "ValidationToken"
        response = self._get(end_point)
        return types.ValidationToken(**response)

    @overload
    def double_auth(self, action: Literal[input_types.DoubleAuthAction.SEND_CODE]) -> str: ...
    @overload
    def double_auth(self, action: Literal[input_types.DoubleAuthAction.VERIFY_CODE], code: str) -> bool: ...

    def double_auth(self, action: input_types.DoubleAuthAction, code: str | None = None) -> str | bool:
        """https://f2.freeivr.co.il/post/64050 ."""
        end_point = "DoubleAuth"
        params = {
            "action": action
        }
        if code is not None:
            params["code"] = code
        response = self._get(end_point, params)
        if action == input_types.DoubleAuthAction.SEND_CODE:
            return response["LastNumberToSend"]
        return response["responseStatus"] == "OK"

    def get_login_log(self, limit: int | None = None, user_name: str | None = None) -> types.GetLoginLog:
        """https://f2.freeivr.co.il/post/64050 ."""
        end_point = "GetLoginLog"
        other_params = {
            "limit": limit,
            "username": user_name
        }
        params = self._filter_params(other_params=other_params)
        response = self._get(end_point, params)
        return types.GetLoginLog(**response)

    def get_all_sessions(self, limit: int | None = None) -> types.GetAllSessions:
        """https://f2.freeivr.co.il/post/64050 ."""
        end_point = "GetAllSessions"
        params = {"limit": limit} if limit is not None else {}
        response = self._get(end_point, params)
        return types.GetAllSessions(**response)

    def kill_session(self, session_id: int) -> bool:
        """https://f2.freeivr.co.il/post/64050 ."""
        end_point = "KillSession"
        params = {
            "SessionId": session_id
        }
        response = self._get(end_point, params)
        return response["responseStatus"] == "OK"

    def kill_all_sessions(self) -> bool:
        """https://f2.freeivr.co.il/post/64050 ."""
        end_point = "KillAllSessions"
        response = self._get(end_point)
        return response["responseStatus"] == "OK"

    @overload
    def run_tzintuk(self, method: Literal[input_types.RunTzintukMethod.OTHER], phones: list[str] | input_types.RunTzintukInput1 | input_types.RunTzintukInput2, caller_id: str | None = None, tzintuk_time_out: int | None = None) -> types.RunTzintuk: ...
    @overload
    def run_tzintuk(self, method: Literal[input_types.RunTzintukMethod.TPL], phones: int, caller_id: str | None = None, tzintuk_time_out: int | None = None) -> types.RunTzintuk: ...
    @overload
    def run_tzintuk(self, method: Literal[input_types.RunTzintukMethod.TZL], phones: list[str], caller_id: str | None = None, tzintuk_time_out: int | None = None) -> types.RunTzintuk: ...

    def run_tzintuk(
        self,
        method: input_types.RunTzintukMethod,
        phones: list[str] | int | input_types.RunTzintukInput1 | input_types.RunTzintukInput2,
        caller_id: str | None = None,
        tzintuk_time_out: int | None = None
    ) -> types.RunTzintuk:
        """https://f2.freeivr.co.il/post/64941 ."""
        end_point = "RunTzintuk"
        other_params = {
            "callerId": caller_id,
            "TzintukTimeOut": tzintuk_time_out
        }
        params = self._filter_params(other_params=other_params)
        if method == input_types.RunTzintukMethod.OTHER:
            phones_param = {"phones": phones}
        elif method == input_types.RunTzintukMethod.TPL:
            phones_param = {"phones": f"tpl:{phones}"}
        elif method == input_types.RunTzintukMethod.TZL:
            phones_param = {"phones": "tzl:", "tzintukLists": phones}
        params.update(phones_param)
        response = self._post(end_point, data=params)
        return types.RunTzintuk(**response)

    @overload
    def tzintukim_list_management(self, action: Literal[input_types.TzintukimListManagementAction.GET_LISTS]) -> types.TzintukimListManagementGetLists: ...
    @overload
    def tzintukim_list_management(self, action: Literal[input_types.TzintukimListManagementAction.GET_LIST_ENTRIES], tzintukim_list: str) -> types.TzintukimListManagementGetListEntries: ...
    @overload
    def tzintukim_list_management(self, action: Literal[input_types.TzintukimListManagementAction.GET_LOG_LIST], tzintukim_list: str) -> types.TzintukimListManagementGetLogList: ...
    @overload
    def tzintukim_list_management(self, action: Literal[input_types.TzintukimListManagementAction.RESET_LIST], tzintukim_list: str) -> bool: ...

    def tzintukim_list_management(self, action: input_types.TzintukimListManagementAction, tzintukim_list: str | None = None) -> types.TzintukimListManagementGetLists | types.TzintukimListManagementGetListEntries | types.TzintukimListManagementGetLogList | bool:
        """https://f2.freeivr.co.il/post/65034 ."""
        end_point = "TzintukimListManagement"
        params = {
            "action": action,
        }
        if action != input_types.TzintukimListManagementAction.GET_LISTS:
            params["TzintukimList"] = tzintukim_list  # pyright: ignore[reportArgumentType]
        response = self._get(end_point, params)
        if action == input_types.TzintukimListManagementAction.GET_LISTS:
            return types.TzintukimListManagementGetLists(**response)
        if action == input_types.TzintukimListManagementAction.GET_LIST_ENTRIES:
            return types.TzintukimListManagementGetListEntries(**response)
        if action == input_types.TzintukimListManagementAction.GET_LOG_LIST:
            return types.TzintukimListManagementGetLogList(**response)
        return response["responseStatus"] == "OK"

    def send_fax(
        self,
        pdf_file: str | bytes,
        phone: str,
        caller_id: str | None = None,
        delivery_url: str | None = None
    ) -> types.SendFax:
        """https://f2.freeivr.co.il/post/66266 ."""
        end_point = "SendFax"
        other_params = {
            "phone": phone,
            "callerId": caller_id,
            "deliveryUrl": delivery_url
        }
        params = self._filter_params(other_params=other_params)
        if isinstance(pdf_file, bytes):
            files = {
                "fileToUpload": ("fax.pdf", pdf_file, "application/pdf")
            }
            params["pdfFile"] = "UPLOAD"
            # response = self._session.post(f"{self.BASE_URL}{end_point}", data=params, files=files).json()
            response = self._post_multipart(end_point, data=params, files=files)
            # self._check_response(response)
        elif isinstance(pdf_file, str):
            params["pdfFile"] = pdf_file
            response = self._post(end_point, data=params)
        else:
            raise TypeError("pdf_file must be str or bytes")  # noqa: EM101, TRY003
        return types.SendFax(**response)

    def check_if_file_exists(self, path: str, base_path: str = "ivr2:/") -> bool:
        """https://f2.freeivr.co.il/post/69817 ."""
        end_point = "CheckIfFileExists"
        params = {
            "path": f"{base_path}{path}"
        }
        return self._get(end_point, params)["fileExists"]

    def send_sms(self, message: str, phones: list[str] | str, sender_id: str | None = None, send_flash_message: bool = False) -> types.SendSms:
        """https://f2.freeivr.co.il/post/71577 ."""
        end_point = "SendSms"
        other_params = {
            "message": message,
            "phones": ":".join(phones) if isinstance(phones, list) else phones,
            "from": sender_id,
        }
        bool_to_int = {
            "sendFlashMessage": send_flash_message
        }
        params = self._filter_params(bool_to_int, other_params)
        response = self._post(end_point, data=params)
        return types.SendSms(**response)

    @overload
    def create_bridge_call(
        self,
        bridge_phones: str,
        phones: str,
        caller_id: str | None = None,
        dial_sip: bool | None = None,
        dial_sip_extension: Literal[False] | None = None,
        account_number: int | None = None,
        sip_extension: None = None,
        record_call: bool | None = None,
        send_mail_in_call: bool | None = None,
        send_mail_in_call_to: str | None = None
    ) -> types.CreateBridgeCall:
        ...

    @overload
    def create_bridge_call(
        self,
        bridge_phones: str,
        phones: str,
        caller_id: str | None = None,
        dial_sip: bool | None = None,
        dial_sip_extension: Literal[True] = True,
        account_number: int | None = None,
        sip_extension: int = 1,
        record_call: bool | None = None,
        send_mail_in_call: bool | None = None,
        send_mail_in_call_to: str | None = None
    ) -> types.CreateBridgeCall:
        ...

    def create_bridge_call(
        self,
        bridge_phones: str,
        phones: str,
        caller_id: str | None = None,
        dial_sip: bool | None = None,
        dial_sip_extension: bool | None = None,
        account_number: int | None = None,
        sip_extension: int | None = None,
        record_call: bool | None = None,
        send_mail_in_call: bool | None = None,
        send_mail_in_call_to: str | None = None
    ) -> types.CreateBridgeCall:
        """https://f2.freeivr.co.il/post/72304 ."""
        end_point = "CreateBridgeCall"
        other_params = {
            "callerId": caller_id,
            "Phones": phones,
            "BridgePhones": bridge_phones,
            "AccountNumber": account_number,
            "SipExtension": sip_extension,
            "SendMailInCallTo": send_mail_in_call_to

        }
        bool_to_int_params = {
            "DialSip": dial_sip,
            "DialSipExtension": dial_sip_extension,
            "RecordCall": record_call,
            "SendMailInCall": send_mail_in_call

        }
        params = self._filter_params(bool_to_int_params, other_params)
        response = self._post(end_point, params)
        return types.CreateBridgeCall(**response)

    def get_queue_real_time(self, queue_path: str) -> types.GetQueueRealTime:
        """https://f2.freeivr.co.il/post/72362 ."""
        end_point = "GetQueueRealTime"
        params = {
            "queuePath": queue_path
        }
        response = self._get(end_point, params)
        return types.GetQueueRealTime(**response)

    def get_customer_data(self) -> types.GetCustomerData:
        """https://f2.freeivr.co.il/post/74300 ."""
        end_point = "GetCustomerData"
        response = self._get(end_point)
        return types.GetCustomerData(**response)

    def view_campaign_reports(self, campaign_id: str, json: bool | None = None) -> types.ViewCampaignReports:
        """https://f2.freeivr.co.il/post/75408 ."""
        end_point = "ViewCampaignReports"
        params = self._filter_params(other_params={"CampaignId": campaign_id}, bool_to_int_params={"json": json})
        response = self._get(end_point, params)
        raise NotImplementedError
        return types.ViewCampaignReports(**response)

    @overload
    def validation_callerId(self, action: Literal[input_types.ValidationCallerIdAction.SEND], *, caller_id: str, valid_type: input_types.ValidationCallerIdValidType) -> str: ...
    @overload
    def validation_callerId(self, action: Literal[input_types.ValidationCallerIdAction.VALID], *, re_id: str, code: str) -> bool: ...

    def validation_callerId(
        self,
        action: input_types.ValidationCallerIdAction,
        *,
        caller_id: str | None = None,
        valid_type: input_types.ValidationCallerIdValidType | None = None,
        re_id: str | None = None,
        code: str | None = None
    ):
        """https://f2.freeivr.co.il/post/77455 ."""
        end_point = "ValidationCallerId"
        other_params = {
            "action": action,
            "callerId": caller_id,
            "validType": valid_type,
            "reId": re_id,
            "code": code
        }
        params = self._filter_params(other_params=other_params)
        response = self._get(end_point, params)
        if action == input_types.ValidationCallerIdAction.SEND:
            return response["reqId"]
        if action == input_types.ValidationCallerIdAction.VALID:
            return response["responseStatus"] == "OK"
        raise ValueError

    def get_tasks(self, limit: int | None = None) -> types.GetTasks:
        """https://f2.freeivr.co.il/post/78443 ."""
        end_point = "GetTasks"
        params = {"limit": limit} if limit is not None else {}
        response = self._get(end_point, params=params)
        return types.GetTasks(**response)

    def get_tasks_data(self, task_id: int) -> types.GetTasksData:
        """https://f2.freeivr.co.il/post/78443 ."""
        end_point = "GetTasksData"
        params = {"TaskId": task_id}
        response = self._get(end_point, params=params)
        return types.GetTasksData(**response)

    def get_tasks_logs(self, task_id: int) -> types.GetTasksLogs:
        """https://f2.freeivr.co.il/post/78443 ."""
        end_point = "GetTasksLogs"
        params = {"TaskId": task_id}
        response = self._get(end_point, params=params)
        return types.GetTasksLogs(**response)

    @overload
    def create_task(
        self,
        task_type: Literal[input_types.CreateTaskType.SEND_SMS],
        active: bool,
        *,
        caller_id: str,
        sms_list: str,
        sms_message: str,
        description: str | None = None,
        minute: int | None = None,
        hour: int | None = None,
        year: int | None = None,
        day: int | None = None,
        month: int | None = None,
        check_is_kodesh: bool | None = None,
        mail_in_end: bool | None = None,
        mail_in_error: bool | None = None,
        if_any_day: bool | None = None,
        active_days: list[int] | None = None
    ) -> types.CreateTask:
        ...

    @overload
    def create_task(
        self,
        task_type: Literal[input_types.CreateTaskType.RUN_TZINTUK],
        active: bool,
        *,
        caller_id: str,
        to_list: str,
        type_list: Literal["tzl", "tpl"],
        description: str | None = None,
        minute: int | None = None,
        hour: int | None = None,
        year: int | None = None,
        day: int | None = None,
        month: int | None = None,
        check_is_kodesh: bool | None = None,
        mail_in_end: bool | None = None,
        mail_in_error: bool | None = None,
        if_any_day: bool | None = None,
        active_days: list[int] | None = None
    ) -> types.CreateTask:
        ...

    @overload
    def create_task(
        self,
        task_type: Literal[input_types.CreateTaskType.MOVE_ON_FILE],
        active: bool,
        *,
        folder: str,
        target: str,
        base_path: str = "ivr2:/",
        move_file_type: Literal["maxFile", "minFile"] | None = None,
        block_move_if_new_file_in_minutes: int | None = None,
        description: str | None = None,
        minute: int | None = None,
        hour: int | None = None,
        year: int | None = None,
        day: int | None = None,
        month: int | None = None,
        check_is_kodesh: bool | None = None,
        mail_in_end: bool | None = None,
        mail_in_error: bool | None = None,
        if_any_day: bool | None = None,
        active_days: list[int] | None = None
    ) -> types.CreateTask:
        ...

    def create_task(
        self,
        task_type: input_types.CreateTaskType,
        active: bool | None = None,
        *,
        caller_id: str | None = None,
        to_list: str | None = None,
        sms_list: str | None = None,
        type_list: Literal["tzl", "tpl"] | None = None,
        sms_message: str | None = None,
        folder: str | None = None,
        target: str | None = None,
        base_path: str = "ivr2:/",
        move_file_type: Literal["maxFile", "minFile"] | None = None,
        block_move_if_new_file_in_minutes: int | None = None,
        description: str | None = None,
        minute: int | None = None,
        hour: int | None = None,
        year: int | None = None,
        day: int | None = None,
        month: int | None = None,
        check_is_kodesh: bool | None = None,
        mail_in_end: bool | None = None,
        mail_in_error: bool | None = None,
        if_any_day: bool | None = None,
        active_days: list[int] | None = None
    ) -> types.CreateTask:
        """https://f2.freeivr.co.il/post/78443 ."""
        end_point = "CreateTask"
        other_params = {
            "taskType": task_type,
            "description": description,
            "minute": minute,
            "hour": hour,
            "year": year,
            "day": day,
            "month": month
        }
        days = {str(i): int(i in active_days) for i in range(7) if active_days is not None}
        other_params["days"] = json.dumps(days) if days else None
        bool_to_int_params = {
            "active": active,
            "checkIsKodesh": check_is_kodesh,
            "mailInEnd": mail_in_end,
            "mailInError": mail_in_error,
            "ifAnyDay": if_any_day
        }
        if task_type == input_types.CreateTaskType.RUN_TZINTUK:
            other_params["callerId"] = caller_id
            other_params["toList"] = to_list
            other_params["typeList"] = type_list
        elif task_type == input_types.CreateTaskType.SEND_SMS:
            other_params["callerId"] = caller_id
            other_params["smsList"] = sms_list
            other_params["smsMessage"] = sms_message
        elif task_type == input_types.CreateTaskType.MOVE_ON_FILE:
            other_params["folder"] = f"{base_path}{folder}"
            other_params["target"] = f"{base_path}{target}"
            other_params["moveFileType"] = move_file_type
            other_params["blockMoveIfNewFileInMinutes"] = block_move_if_new_file_in_minutes
        params = self._filter_params(bool_to_int_params, other_params)
        response = self._post(end_point, params)
        return types.CreateTask(**response)

    def update_task(
        self,
        task_id: int,
        active: bool | None = None,
        description: str | None = None,
        minute: int | None = None,
        hour: int | None = None,
        year: int | None = None,
        day: int | None = None,
        month: int | None = None,
        check_is_kodesh: bool | None = None,
        mail_in_end: bool | None = None,
        mail_in_error: bool | None = None,
        if_any_day: bool | None = None,
        active_days: list[int] | None = None
    ) -> bool:
        """https://f2.freeivr.co.il/post/78443 ."""
        end_point = "UpdateTask"
        other_params = {
            "TaskId": task_id,
            "description": description,
            "minute": minute,
            "hour": hour,
            "year": year,
            "day": day,
            "month": month
        }
        days = {str(i): int(i in active_days) for i in range(7) if active_days is not None}
        other_params["days"] = json.dumps(days) if days else None
        bool_to_int_params = {
            "active": active,
            "checkIsKodesh": check_is_kodesh,
            "mailInEnd": mail_in_end,
            "mailInError": mail_in_error,
            "ifAnyDay": if_any_day
        }
        params = self._filter_params(bool_to_int_params, other_params)
        response = self._post(end_point, params)
        return response["responseStatus"] == "OK"

    def delete_task(self, task_id: int) -> bool:
        """https://f2.freeivr.co.il/post/78443 ."""
        end_point = "DeleteTask"
        params = {
            "TaskId": task_id
        }
        response = self._post(end_point, params)
        return response["responseStatus"] == "OK"

    def send_tts(
            self,
            phones: list[str] | str,
            tts_message: str,
            tts_voice: str | None = None,
            caller_id: str | None = None,
            callback_url: str | None = None,
            repeat_file: int | None = None,
            tts_rate: int | None = None,
            send_mail: bool | None = None
    ) -> types.SendTTS:
        """https://f2.freeivr.co.il/post/82888 ."""
        end_point = "SendTTS"
        other_params = {
            "phones": ":".join(phones) if isinstance(phones, list) else phones,
            "ttsMessage": tts_message,
            "ttsVoice": tts_voice,
            "callerId": caller_id,
            "callbackUrl": callback_url,
            "repeatFile": repeat_file,
            "ttsRate": tts_rate
        }
        bool_to_int_params = {
            "SendMail": send_mail
        }
        params = self._filter_params(bool_to_int_params, other_params)
        response = self._post(end_point, params)
        return types.SendTTS(**response)

    @overload
    def render_ymgr_file(
        self,
        path: str,
        convert_type: Literal["json"],
        base_path: str = "ivr2:/",
        suffix: str = ".ymgr",
        not_load_lang: bool | None = None,
        render_language: str | None = None
    ) -> list[dict]:
        ...

    @overload
    def render_ymgr_file(
        self,
        path: str,
        convert_type: Literal["csv", "html"],
        base_path: str = "ivr2:/",
        suffix: str = ".ymgr",
        not_load_lang: bool | None = None,
        render_language: str | None = None
    ) -> str:
        ...

    def render_ymgr_file(
        self,
        path: str,
        convert_type: Literal["json", "csv", "html"],
        base_path: str = "ivr2:/",
        suffix: str = ".ymgr",
        not_load_lang: bool | None = None,
        render_language: str | None = None
    ) -> str | list[dict]:
        """https://f2.freeivr.co.il/post/84092 ."""
        end_point = "RenderYMGRFile"
        other_params = {
            "wath": f"{base_path}{path}{suffix}",
            "convertType": convert_type,
            "renderLanguage": render_language
        }
        bool_to_int_params = {
            "notLoadLang": not_load_lang
        }
        params = self._filter_params(bool_to_int_params, other_params)
        if convert_type == "json":
            response = self._get(end_point, params)
            return response["data"]
        params.update(self.params)
        client = self._get_session()
        response = client.get(f"{self.BASE_URL}{end_point}", params=params)
        content_type = response.headers.get("Content-Type")
        if content_type == "application/json; charset=utf-8":
            json_error = response.json()
            self._check_response(json_error)
        return response.text

    def get_customer_sms_transactions(self) -> types.GetCustomerSmsTransactions:
        """https://f2.freeivr.co.il/post/86565 ."""
        end_point = "GetCustomerSmsTransactions"
        response = self._get(end_point)
        return types.GetCustomerSmsTransactions(**response)

    def check_if_folder_exists(self, path: str | int, base_path: str = "ivr2:/") -> bool:
        """https://f2.freeivr.co.il/post/89322 ."""
        end_point = "CheckIfFolderExists"
        params = {
            "path": f"{base_path}{path}"
        }
        client = self._get_session()
        response = client.get(f"{self.BASE_URL}{end_point}", params={**self.params, **params}).json()
        if "folderExists" in response:
            return response["folderExists"]
        raise YemotAPIError(response["responseStatus"], **response)

    def create_sip_account(self, ext_number: int | None = None) -> types.CreateSipAccount:
        """https://f2.freeivr.co.il/post/91611 ."""
        end_point = "CreateSipAccount"
        other_params = {
            "extNumber": ext_number
        }
        params = self._filter_params(other_params=other_params)
        response = self._post(end_point, params)
        return types.CreateSipAccount(**response)

    def get_sip_accounts_in_customer(self) -> types.GetSipAccountsInCustomer:
        """https://f2.freeivr.co.il/post/91611 ."""
        end_point = "GetSipAccountsInCustomer"
        response = self._get(end_point)
        return types.GetSipAccountsInCustomer(**response)

    def sip_to_wss(self, account_number: int | None = None) -> bool:
        """https://f2.freeivr.co.il/post/91611 ."""
        end_point = "SipToWSS"
        other_params = {
            "accountNumber": account_number
        }
        params = self._filter_params(other_params=other_params)
        response = self._post(end_point, params)
        return response["responseStatus"] == "OK"

    def sip_to_udp(self, account_number: int | None = None) -> bool:
        """https://f2.freeivr.co.il/post/91611 ."""
        end_point = "SipToUDP"
        other_params = {
            "accountNumber": account_number
        }
        params = self._filter_params(other_params=other_params)
        response = self._post(end_point, params)
        return response["responseStatus"] == "OK"

    def edit_caller_id_in_sip_account(self, account_number: int, caller_id: str) -> bool:
        """https://f2.freeivr.co.il/post/91611 ."""
        end_point = "EditCallerIdInSipAccount"
        params = {
            "accountNumber": account_number,
            "callerId": caller_id
        }
        response = self._post(end_point, params)
        return response["responseStatus"] == "OK"

    def delete_sip_account(self, account_number: int | list[int]) -> bool:
        """https://f2.freeivr.co.il/post/91611 ."""
        end_point = "DeleteSipAccount"
        params = {
            "accountNumber": account_number
        }
        response = self._post(end_point, params)
        return response["responseStatus"] == "OK"

    def sip_extension_management(
        self,
        sip_extension_management: input_types.SipExtensionManagementAction,
        account_number: int | None = None,
        ext_number: int | None = None
    ) -> int | None:
        """https://f2.freeivr.co.il/post/91611 ."""
        raise NotImplementedError
        end_point = "SipExtensionManagement"
        other_params = {
            "SipExtensionManagement": sip_extension_management,
            "accountNumber": account_number,
            "extNumber": ext_number
        }
        params = self._filter_params(other_params=other_params)
        print(params)
        response = self._post(end_point, params)  # eroor message='bad action', response_status='Exception'
        return response["extNumber"]

    def set_secondary_did_usage_description(self, secondary_did_id: int, new_usage: str) -> bool:
        """https://f2.freeivr.co.il/post/91702 ."""
        end_point = "SetSecondaryDIDUsageDescription"
        params = {
            "secondaryDidId": secondary_did_id,
            "newUsage": new_usage
        }
        response = self._post(end_point, params)
        return response["status"]

    def get_ivr2_dir_stats(self, path: str) -> types.GetIVR2DirStats:
        """https://f2.freeivr.co.il/post/92233 ."""
        end_point = "GetIVR2DirStats"
        params = {
            "path": f"{path}"
        }
        response = self._get(end_point, params)
        return types.GetIVR2DirStats(**response)

    @overload
    def queue_management(
        self,
        queue_path: str,
        action: Literal[input_types.QueueManagementAction.KICK],
        *,
        call_ids: list[str],
        go_to: str | None = None
    ) -> dict:
        ...

    @overload
    def queue_management(
        self,
        queue_path: str,
        action: Literal[input_types.QueueManagementAction.PAUSE, input_types.QueueManagementAction.UNPAUSE],
        *,
        agent: str
    ) -> bool:
        ...

    def queue_management(
        self,
        queue_path: str,
        action: input_types.QueueManagementAction,
        *,
        call_ids: list[str] | None = None,
        agent: str | None = None,
        go_to: str | None = None
    ):
        """https://f2.freeivr.co.il/post/99072 ."""
        end_point = "QueueManagement"
        other_params = {
            "queuePath": queue_path,
            "callIds": call_ids,
            "action": action,
            "agent": agent
        }
        if action == input_types.QueueManagementAction.KICK and go_to is not None:
            other_params["moreData"] = f"GOTO:{go_to}"
        params = self._filter_params(other_params=other_params)
        response = self._post(end_point, params)
        if action == input_types.QueueManagementAction.KICK:
            return response["status"]
        return response["responseStatus"] == "OK"

    def pirsum_phone_management(self, action: input_types.PirsumPhoneManagementAction) -> bool:
        """https://f2.freeivr.co.il/post/106325 ."""
        end_point = "PirsumPhoneManagement"
        params = {
            "action": action
        }
        response = self._post(end_point, params)
        if action == input_types.PirsumPhoneManagementAction.GET_REGISTRATION_STATUS:
            return response["registrationStatus"]
        return response["results"] == "OK"

    @overload
    def call_extension_bridging(self, method: Literal[input_types.RunTzintukMethod.OTHER], phones: list[str] | input_types.RunTzintukInput1 | input_types.RunTzintukInput2, ivr_path: str, caller_id: str | None = None, calls_time_out: int | None = None, base_path: str = "ivr2:/") -> types.CallExtensionBridging:
        ...

    @overload
    def call_extension_bridging(self, method: Literal[input_types.RunTzintukMethod.TPL], phones: int, ivr_path: str, caller_id: str | None = None, calls_time_out: int | None = None, base_path: str = "ivr2:/") -> types.CallExtensionBridging:
        ...

    @overload
    def call_extension_bridging(self, method: Literal[input_types.RunTzintukMethod.TZL], phones: list[str], ivr_path: str, caller_id: str | None = None, calls_time_out: int | None = None, base_path: str = "ivr2:/") -> types.CallExtensionBridging:
        ...

    def call_extension_bridging(
        self,
        method: input_types.RunTzintukMethod,
        phones: list[str] | int | input_types.RunTzintukInput1 | input_types.RunTzintukInput2,
        ivr_path: str,
        caller_id: str | None = None,
        calls_time_out: int | None = None,
        base_path: str = "ivr2:/"
    ) -> types.CallExtensionBridging:
        """https://f2.freeivr.co.il/post/110020 ."""
        end_point = "CallExtensionBridging"
        other_params = {
            "ivrPath": f"{base_path}{ivr_path}",
            "callerId": caller_id,
            "callsTimeOut": calls_time_out
        }
        params = self._filter_params(other_params=other_params)
        if method == input_types.RunTzintukMethod.OTHER:
            phones_param = {"phones": phones}
        elif method == input_types.RunTzintukMethod.TPL:
            phones_param = {"phones": f"tpl:{phones}"}
        elif method == input_types.RunTzintukMethod.TZL:
            phones_param = {"phones": "tzl:", "tzintukLists": phones}
        params.update(phones_param)
        response = self._post(end_point, params)
        return types.CallExtensionBridging(**response)

    def sip_get_contexts(self, account_number: int | None = None) -> types.SipGetContexts:
        """https://f2.freeivr.co.il/post/125413 ."""
        end_point = "SipGetContexts"
        params = self._filter_params(other_params={"accountNumber": account_number})
        response = self._get(end_point, params)
        return types.SipGetContexts(**response)

    def get_sip_accounts_registered_status(self) -> types.GetSipAccountsRegisteredStatus:
        """https://f2.freeivr.co.il/post/125630 ."""
        end_point = "GetSipAccountsRegisteredStatus"
        response = self._get(end_point)
        return types.GetSipAccountsRegisteredStatus(**response)

    def get_approved_caller_ids(self) -> types.GetApprovedCallerIDs:
        """https://f2.freeivr.co.il/post/135629 ."""
        end_point = "GetApprovedCallerIDs"
        response = self._get(end_point)
        return types.GetApprovedCallerIDs(**response)

    def is_caller_id_approved(self, caller_id: str, service_type: Literal["sms", "call"] | None = None) -> types.IsCallerIDApproved:
        """https://f2.freeivr.co.il/post/135691 ."""
        end_point = "IsCallerIDApproved"
        other_params = {
            "callerId": caller_id,
            "serviceType": service_type
        }
        params = self._filter_params(other_params=other_params)
        response = self._get(end_point, params)
        return types.IsCallerIDApproved(**response)

    @overload
    def queue_call_back(self, action: Literal[input_types.QueueCallBackAction.GET_QUEUES]) -> types.QueueCallBackGetQueues:
        ...

    @overload
    def queue_call_back(self, action: Literal[input_types.QueueCallBackAction.GET_LIST], id: int) -> types.QueueCallBackGetList:
        ...

    @overload
    def queue_call_back(self, action: Literal[input_types.QueueCallBackAction.REMOVE_NUMBER], id: int) -> bool:
        ...

    def queue_call_back(self, action: input_types.QueueCallBackAction, id: int | None = None) -> types.QueueCallBackGetQueues | types.QueueCallBackGetList | bool:
        """https://f2.freeivr.co.il/post/144279 ."""
        end_point = "QueueCallBack"
        other_params = {
            "action": action,
            "id": id
        }
        params = self._filter_params(other_params=other_params)
        response = self._get(end_point, params)
        if action == input_types.QueueCallBackAction.GET_QUEUES:
            return types.QueueCallBackGetQueues(**response)
        if action == input_types.QueueCallBackAction.GET_LIST:
            return types.QueueCallBackGetList(**response)
        return response["responseStatus"] == "OK"

    def get_incoming_sms(self, limit: int | None = None, start_date: datetime | str | None = None, end_date: datetime | str | None = None) -> types.GetIncomingSms:
        """https://f2.freeivr.co.il/post/145861 ."""
        end_point = "GetIncomingSms"
        other_params = {
            "limit": limit,
            "startDate": self._format_datetime(start_date),
            "endDate": self._format_datetime(end_date)
        }
        params = self._filter_params(other_params=other_params)
        response = self._get(end_point, params)
        return types.GetIncomingSms(**response)

    @overload
    def mfa_session(self, action: Literal[input_types.MfaSessionAction.IS_PASS, input_types.MfaSessionAction.TRY]) -> types.MfaSessionIsPass: ...
    @overload
    def mfa_session(self, action: Literal[input_types.MfaSessionAction.GET_MFA_METHODS]) -> types.MfaSessionGetMfaMethods: ...
    @overload
    def mfa_session(self, action: Literal[input_types.MfaSessionAction.SEND_MFA, input_types.MfaSessionAction.REVALIDATE_METHOD], *, mfa_id: int, mfa_send_type: str, lang: str | None = None, auto_otp_hostname: str | None = None) -> bool: ...
    @overload
    def mfa_session(self, action: Literal[input_types.MfaSessionAction.VALID_MFA], *, mfa_code: str, mfa_remember_me: bool | None = None, mfa_remember_note: str | None = None) -> types.MfaSessionValidMfa: ...
    @overload
    def mfa_session(self, action: Literal[input_types.MfaSessionAction.ADD_METHOD], *, mfa_new_type: Literal["EMAIL", "PHONE"], mta_new_value: str, mfa_new_valid_note: str | None = None, new_expired_date: datetime | str | None = None) -> str: ...
    @overload
    def mfa_session(self, action: Literal[input_types.MfaSessionAction.VALID_METHOD], *, mfa_id: int, mfa_code: str) -> types.MfaSessionValidMfa: ...
    @overload
    def mfa_session(self, action: Literal[input_types.MfaSessionAction.DELETE_METHOD], *, mfa_id: int) -> bool: ...
    @overload
    def mfa_session(self, action: Literal[input_types.MfaSessionAction.GET_MFA_TRUST_TOKENS]) -> types.MfaSessionGetMfaTrustTokens: ...
    @overload
    def mfa_session(self, action: Literal[input_types.MfaSessionAction.DELETE_TRUST_TOKEN], *, trust_token_id: str) -> bool: ...
    @overload
    def mfa_session(self, action: Literal[input_types.MfaSessionAction.GET_MFA_TRUST_IPS]) -> list[str]: ...
    @overload
    def mfa_session(self, action: Literal[input_types.MfaSessionAction.SET_MFA_TRUST_IPS], *, trust_ips: list[str]) -> types.MfaSessionSetMfaTrustIps: ...

    def mfa_session(
        self,
        action: input_types.MfaSessionAction,
        *,
        mfa_id: int | None = None,
        mfa_send_type: str | None = None,
        lang: str | None = None,
        auto_otp_hostname: str | None = None,
        mfa_code: str | None = None,
        mfa_remember_me: bool | None = None,
        mfa_remember_note: str | None = None,
        mfa_new_type: Literal["EMAIL", "PHONE"] | None = None,
        mta_new_value: str | None = None,
        mfa_new_valid_note: str | None = None,
        new_expired_date: datetime | str | None = None,
        trust_token_id: str | None = None,
        trust_ips: list[str] | None = None
    ) -> types.MfaSessionIsPass | types.MfaSessionGetMfaMethods | bool | types.MfaSessionValidMfa | str | types.MfaSessionGetMfaTrustTokens | list[str] | types.MfaSessionSetMfaTrustIps:
        """https://f2.freeivr.co.il/post/159985 ."""
        end_point = "MFASession"
        other_params = {
            "action": action,
            "mfaId": mfa_id,
            "mfaSendType": mfa_send_type,
            "lang": lang,
            "autoOtpHostname": auto_otp_hostname,
            "mfaCode": mfa_code,
            "mfaRememberMe": mfa_remember_me,
            "mfaRememberNote": mfa_remember_note,
            "mfaNewType": mfa_new_type,
            "mtaNewValue": mta_new_value,
            "mfaNewValidNote": mfa_new_valid_note,
            "newExpiredDate": self._format_datetime(new_expired_date),
            "trustTokenId": trust_token_id,
            "trustIps": trust_ips
        }
        params = self._filter_params(other_params=other_params)
        response = self._post(end_point, params)
        if action in [input_types.MfaSessionAction.IS_PASS, input_types.MfaSessionAction.TRY, input_types.MfaSessionAction.GET_MFA_METHODS]:
            return types.MfaSessionIsPass(**response)
        if action in [input_types.MfaSessionAction.SEND_MFA, input_types.MfaSessionAction.REVALIDATE_METHOD, input_types.MfaSessionAction.DELETE_METHOD, input_types.MfaSessionAction.DELETE_TRUST_TOKEN]:
            return response["responseStatus"] == "OK"
        if action in [input_types.MfaSessionAction.VALID_MFA, input_types.MfaSessionAction.VALID_METHOD]:
            return types.MfaSessionValidMfa(**response)
        if action == input_types.MfaSessionAction.ADD_METHOD:
            return response["methodId"]
        if action == input_types.MfaSessionAction.GET_MFA_TRUST_TOKENS:
            return types.MfaSessionGetMfaTrustTokens(**response)
        if action == input_types.MfaSessionAction.GET_MFA_TRUST_IPS:
            return response["trustIps"]
        if action == input_types.MfaSessionAction.SET_MFA_TRUST_IPS:
            return types.MfaSessionSetMfaTrustIps(**response)
        raise ValueError
