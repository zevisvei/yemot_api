from typing import Any


class YemotAPIError(Exception):
    def __init__(
            self,
            response_status: str,
            message_code: str | None | int = None,
            message: str | None = None,
            /,
            **kwargs: dict[str, Any]
    ) -> None:
        self.response_status = response_status
        self.message_code = message_code or "error code not provided"
        self.message = message or "error message not provided"

        error_message = (
            f"Yemot API Error: "
            f"message_code={self.message_code!r}, "
            f"message={self.message!r}, "
            f"response_status={self.response_status!r}"
        )
        for key, value in kwargs.items():
            if key in {"responseStatus", "messageCode", "message"}:
                continue
            error_message += f", {key}={value!r}"
            setattr(self, key, value)
        super().__init__(error_message)


class YemotApiResponseError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
