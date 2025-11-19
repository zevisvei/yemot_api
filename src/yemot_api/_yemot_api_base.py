from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable
from datetime import date, datetime
from typing import Any, Literal

from httpx import AsyncClient
from requests import Session

from .exceptions import YemotAPIError


class YemotBase(ABC):
    token: str
    @abstractmethod
    def close(self) -> None | Awaitable[None]: ...
    @abstractmethod
    def _get_session(self) -> Session | AsyncClient: ...
    @abstractmethod
    def _get(self, end_point: str, params: dict[str, Any] | None = None, *, default_params: bool = True) -> dict[Any, Any] | Awaitable[dict[Any, Any]]: ...
    @abstractmethod
    def _post(self, end_point: str, data: dict[str, Any] | None = None) -> dict[Any, Any] | Awaitable[dict[Any, Any]]: ...
    @abstractmethod
    def _post_multipart(self, end_point: str, files: dict[str, Any], data: dict[str, Any] | None = None) -> dict[Any, Any] | Awaitable[dict[Any, Any]]: ...
    @abstractmethod
    def __del__(self) -> None: ...

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, __class__):
            return NotImplemented
        return self.token == other.token

    def __str__(self) -> str:
        return f"{self.token}"

    def __repr__(self) -> str:
        return f"{self.token}"

    def __hash__(self) -> int:
        return hash(self.token)

    @property
    def params(self) -> dict[Literal["token"], str]:
        return {"token": self.token}

    @staticmethod
    def _check_response(json_response: dict) -> None:
        if json_response["responseStatus"] != "OK":
            raise YemotAPIError(
                json_response["responseStatus"],
                json_response.get("messageCode"),
                json_response.get("message"),
                **json_response
            )

    @staticmethod
    def _filter_params(bool_to_int_params: dict | None = None, other_params: dict | None = None) -> dict:
        params = {}
        if bool_to_int_params:
            params.update({key: int(val) for key, val in bool_to_int_params.items() if val is not None})
        if other_params:
            params.update({k: v for k, v in other_params.items() if v is not None})
        return params

    @staticmethod
    def _to_iso_date(d: str | date | None) -> str | None:
        if isinstance(d, datetime):
            return d.date().isoformat()
        if isinstance(d, date):
            return d.isoformat()
        if isinstance(d, str) and d.strip():
            return d
        return None

    @staticmethod
    def _format_datetime(dt: datetime | str | None) -> str | None:
        if isinstance(dt, str) and dt.strip():
            return dt
        if isinstance(dt, datetime):
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return None
