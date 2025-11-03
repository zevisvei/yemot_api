import re
from collections.abc import Iterable
from datetime import date, datetime
from enum import StrEnum
from typing import Literal, overload

from .exceptions import YemotApiResponseError


def _none_to_str[T](value: T | None) -> str | T:
    return "" if value is None else value


def _false_to_str(value: bool | Literal["no"] | None) -> str:
    return "no" if (value is False or value == "no") else ""


def _true_to_str(value: bool | Literal["yes"] | None) -> str:
    return "yes" if (value is True or value == "yes") else ""


def _remove_extra_commas(value: str) -> str:
    return value.rstrip(",")


def _remove_invalid_chars(text: str) -> str:
    invalid_chars_regex = r'[.\-"\'&|]'
    return re.sub(invalid_chars_regex, '', text)


def join(*args: str) -> str:
    if len(args) == 1:
        return args[0]
    if len(args) < 2:
        raise ValueError
    result = args[0]
    for idx, v in enumerate(args[1:]):
        prev_value = args[idx]
        if not prev_value.startswith(("music_on_hold", "id_list_message")):
            message = "שרשור פעולות תקף רק בmusic_on_hold ו id_list_message"
            raise YemotApiResponseError(message)
        result += f"&{v}"
    return result


def go_to_folder(folder_path: str) -> str:
    result = f"go_to_folder={folder_path}"
    return _remove_extra_commas(result)


def hangup() -> str:
    return "go_to_folder=hangup"


def go_to_folder_and_play(folder_path: str, file_path: str, play_point: int = 0) -> str:
    result = f"go_to_folder_and_play={folder_path},{file_path},{play_point}"
    return _remove_extra_commas(result)


class CreditCard:
    def __init__(self, billing_sum: int | None = None, credit_card_max_tashloumim: int | None = None, credit_card_currency: Literal[1, 2] | None = 1, credit_card_name_stt: bool | Literal["NameStt"] | None = None, credit_card_name_stt_record_no_ask: bool | Literal["NoAsk"] | None = None, go_back: bool | Literal["GoBack"] | None = None) -> None:
        self.billing_sum = billing_sum
        self.credit_card_max_tashloumim = credit_card_max_tashloumim
        self.credit_card_currency = credit_card_currency
        self.credit_card_name_stt = "NameStt" if credit_card_name_stt else None
        self.credit_card_name_stt_record_no_ask = "NoAsk" if credit_card_name_stt_record_no_ask else None
        self.go_back = "GoBack" if go_back else None

    def _response(
        self,
        credit_card_type: str,
        credit_card_register_number: str | int | None = None,
        credit_card_pelecard_type: str | None = None,
        credit_card_user_name: str | None = None,
        credit_card_terminal_number: int | str | None = None,
        credit_card_password: str | None = None,
        response: str | None = None,
        credit_card_enter_phone: bool | Literal["EnterPhone"] | None = None,
        credit_card_create_token: Literal["CreateToken", "CreateTokenOnly"] | None = None,
    ) -> str:
        if credit_card_enter_phone:
            credit_card_enter_phone = "EnterPhone"
        result = f"credit_card={credit_card_type},{_none_to_str(self.billing_sum)},{_none_to_str(credit_card_register_number)},{_none_to_str(self.credit_card_max_tashloumim)},{_none_to_str(self.credit_card_currency)},{_none_to_str(credit_card_pelecard_type)},{_none_to_str(credit_card_user_name)},{_none_to_str(credit_card_terminal_number), },{_none_to_str(credit_card_password)},{_none_to_str(response)},{_none_to_str(credit_card_enter_phone)},{_none_to_str(self.credit_card_name_stt)},{_none_to_str(self.credit_card_name_stt_record_no_ask)},{_none_to_str(credit_card_create_token)},{_none_to_str(self.go_back)}"
        return _remove_extra_commas(result)

    def tranzila(self, credit_card_user_name: str, credit_card_password: str, credit_card_register_number: str | None = None) -> str:
        credit_card_type = "tranzila"
        return self._response(credit_card_type, credit_card_register_number, credit_card_user_name=credit_card_user_name, credit_card_password=credit_card_password)

    def credit_guard(self, credit_card_user_name: str, credit_card_terminal_number: int, credit_card_password: str) -> str:
        credit_card_type = "credit_guard"
        return self._response(credit_card_type, credit_card_user_name=credit_card_user_name, credit_card_register_number=credit_card_terminal_number, credit_card_password=credit_card_password)

    def kesherhk(self, credit_card_register_number: int, credit_card_terminal_number: str, credit_card_password: str) -> str:
        credit_card_type = "kesherhk"
        return self._response(credit_card_type, credit_card_register_number, credit_card_terminal_number=credit_card_terminal_number, credit_card_password=credit_card_password)

    def nedarim_plus(self, credit_card_terminal_number: int, credit_card_enter_phone: bool | None = None) -> str:
        credit_card_type = "nedarim_plus"
        return self._response(credit_card_type, credit_card_terminal_number=credit_card_terminal_number, credit_card_enter_phone=credit_card_enter_phone)

    def cardcom(self, credit_card_user_name: str, credit_card_terminal_number: int, credit_card_register_number: int = 555) -> str:
        credit_card_type = "cardcom"
        return self._response(credit_card_type, credit_card_register_number, credit_card_user_name=credit_card_user_name, credit_card_terminal_number=credit_card_terminal_number)

    def pelecard(self, credit_card_user_name: str, credit_card_terminal_number: int, credit_card_password: str, credit_card_register_number: int = 555, credit_card_pelecard_type: Literal["DebitRegularType", "DebitCreditType", "DebitPaymntsType"] | None = None) -> str:
        credit_card_type = "pelecard"
        return self._response(credit_card_type, credit_card_register_number, credit_card_pelecard_type=credit_card_pelecard_type, credit_card_user_name=credit_card_user_name, credit_card_terminal_number=credit_card_terminal_number, credit_card_password=credit_card_password)

    def asakim(self, credit_card_user_name: str, credit_card_terminal_number: int) -> str:
        credit_card_type = "asakim"
        return self._response(credit_card_type, credit_card_user_name=credit_card_user_name, credit_card_terminal_number=credit_card_terminal_number)

    def icredit(self, credit_card_user_name: str) -> str:
        credit_card_type = "icredit"
        return self._response(credit_card_type, credit_card_user_name=credit_card_user_name)

    def yaad_pay(self, credit_card_terminal_number: int, credit_card_password: str) -> str:
        credit_card_type = "yaad_pay"
        return self._response(credit_card_type, credit_card_terminal_number=credit_card_terminal_number, credit_card_password=credit_card_password)

    def icount(self, credit_card_user_name: str, credit_card_terminal_number: int, credit_card_password: str) -> str:
        credit_card_type = "icount"
        return self._response(credit_card_type, credit_card_user_name=credit_card_user_name, credit_card_terminal_number=credit_card_terminal_number, credit_card_password=credit_card_password)


def routing_yemot(phone_number: str) -> str:
    result = f"routing_yemot={phone_number}"
    return _remove_extra_commas(result)


@overload
def routing(
    routing_to_phone: list[str],
    routing_start: int | None = None,
    routing_multiple: Literal[False] | None = None,
    routing_multiple_numbers: None = None,
    routing_your_id: str | None = None,
    routing_record: bool | Literal["no"] | None = None,
    routing_end_time: int | None = None,
    routing_end_goto: str | None = None,
    music_on_hold: str | None = None,
    routing_answer_play: bool | Literal["yes"] | None = None,
    routing_answer_tfr: bool | Literal["yes"] | None = None,
    routing_answer_tfr_hangup_goto: str | None = None,
    routing_email_address: str | None = None,
    routing_email_name: str | None = None
) -> str: ...


@overload
def routing(
    routing_to_phone: list[str],
    routing_start: int | None = None,
    routing_multiple: Literal[True] = True,
    routing_multiple_numbers: list[int] = [],
    routing_your_id: str | None = None,
    routing_record: bool | Literal["no"] | None = None,
    routing_end_time: int | None = None,
    routing_end_goto: str | None = None,
    music_on_hold: str | None = None,
    routing_answer_play: bool | Literal["yes"] | None = None,
    routing_answer_tfr: bool | Literal["yes"] | None = None,
    routing_answer_tfr_hangup_goto: str | None = None,
    routing_email_address: str | None = None,
    routing_email_name: str | None = None
) -> str: ...


def routing(
    routing_to_phone: list[str],
    routing_start: int | None = None,
    routing_multiple: bool = False,
    routing_multiple_numbers: list[int] | None = None,
    routing_your_id: str | None = None,
    routing_record: bool | Literal["no"] | None = None,
    routing_end_time: int | None = None,
    routing_end_goto: str | None = None,
    music_on_hold: str | None = None,
    routing_answer_play: bool | Literal["yes"] | None = None,
    routing_answer_tfr: bool | Literal["yes"] | None = None,
    routing_answer_tfr_hangup_goto: str | None = None,
    routing_email_address: str | None = None,
    routing_email_name: str | None = None
) -> str:
    result = f"routing={'.'.join(routing_to_phone)},{_none_to_str(routing_start)},,{_true_to_str(routing_multiple)},{'.'.join(map(str, routing_multiple_numbers)) if routing_multiple_numbers else ''},{_none_to_str(routing_your_id)},{_false_to_str(routing_record)},,{_none_to_str(routing_end_time)},{_none_to_str(routing_end_goto)},{_none_to_str(music_on_hold)},{_true_to_str(routing_answer_play)},{_true_to_str(routing_answer_tfr)},{_none_to_str(routing_answer_tfr_hangup_goto)},{_none_to_str(routing_email_address)},{_none_to_str(routing_email_name)}"
    return _remove_extra_commas(result)


def music_on_hold(music_name: str, time: int | None = None) -> str:
    result = f"music_on_hold={music_name}{f',{time}' if time is not None else ''}"
    return _remove_extra_commas(result)


class IdListMessageType(StrEnum):
    File = "f"
    Digits = "d"
    Number = "n"
    Alpha = "a"
    Text = "t"
    Speech = "s"
    SystemMessage = "m"
    GoToFolder = "g"
    Noop = "noop"
    Date = "date"
    DateH = "dateH"


def id_list_message(play: IdListMessageType, value: str) -> str:
    result = f"id_list_message={play}-{value}"
    return _remove_extra_commas(result)


def id_list_message_file(value: str) -> str:
    result = f"id_list_message=f-{value}"
    return _remove_extra_commas(result)


def id_list_message_digits(value: int) -> str:
    result = f"id_list_message=d-{value}"
    return _remove_extra_commas(result)


def id_list_message_number(value: int) -> str:
    result = f"id_list_message=n-{value}"
    return _remove_extra_commas(result)


def id_list_message_alpha(value: str) -> str:
    result = f"id_list_message=a-{value}"
    return _remove_extra_commas(result)


def id_list_message_text(value: str, remove_invalid: bool = True) -> str:
    if remove_invalid:
        value = _remove_invalid_chars(value)
    elif re.search(r'[.\-"\'&|]', value):
        message = "הטקסט מכיל תווים לא חוקיים: . - \" ' & |"
        raise YemotApiResponseError(message)
    result = f"id_list_message=t-{value}"
    return _remove_extra_commas(result)


def id_list_message_speech(file_path: str) -> str:
    result = f"id_list_message=s-{file_path}"
    return _remove_extra_commas(result)


def id_list_message_system_message(value: str) -> str:
    result = f"id_list_message=m-{value}"
    return _remove_extra_commas(result)


def id_list_message_go_to_folder(value: str) -> str:
    result = f"id_list_message=g-{value}"
    return _remove_extra_commas(result)


def id_list_message_noop() -> str:
    result = "id_list_message=noop"
    return _remove_extra_commas(result)


def id_list_message_date(value: str | date) -> str:
    if isinstance(value, datetime):
        value = value.date()
    if isinstance(value, date):
        value = value.strftime("%d/%m/%Y")
    result = f"id_list_message=date-{value}"
    return _remove_extra_commas(result)


def id_list_message_date_h(value: str | date) -> str:
    if isinstance(value, datetime):
        value = value.date()
    if isinstance(value, date):
        value = value.strftime("%d/%m/%Y")
    result = f"id_list_message=dateH-{value}"
    return _remove_extra_commas(result)


@overload
def id_list_message_zmanim(value: str, time_zone: str, time_diff: Literal["+", "-"], time_delay: str) -> str: ...
@overload
def id_list_message_zmanim(value: str, time_zone: str) -> str: ...


def id_list_message_zmanim(value: str, time_zone: str, time_diff: Literal["+", "-"] | None = None, time_delay: str | None = None) -> str:
    result = f"id_list_message=z-{value},{time_zone},{time_diff},{time_delay}"
    return _remove_extra_commas(result)


class PlayConfirmType(StrEnum):
    NO = "NO"
    Number = "Number"
    Digits = "Digits"
    Price = "Price"
    Time = "Time"
    Date = "Date"
    HebrewDate = "HebrewDate"
    TeudatZehut = "TeudatZehut"
    Phone = "Phone"
    Alpha = "Alpha"
    HebrewKeyboard = "HebrewKeyboard"
    EnglishKeyboard = "EnglishKeyboard"
    EmailKeyboard = "EmailKeyboard"
    DigitsKeyboard = "DigitsKeyboard"
    File = "File"
    TTS = "TTS"


def read_text(
    message_type: IdListMessageType,
    message_value: str,
    param_name: str,
    send_prev_values: bool = False,
    max_digits: int | None = None,
    min_digits: int | None = None,
    timeout: int | None = None,
    play_confirm_type: PlayConfirmType | None = None,
    block_asterisk: bool = False,
    block_zero: bool = False,
    replacment: tuple[str, str] | None = None,
    allowed_values: Iterable[str | int] | None = None,
    timout_empty_times: int | None = None,
    replace_none: str | None = None,
    allow_keyboard_language_change: bool = True,
    conform: bool = True
) -> str:
    dict_replace = {
        PlayConfirmType.Time: {"max": 4, "min": 4},
        PlayConfirmType.Date: {"max": 8, "min": 8},
        PlayConfirmType.HebrewDate: {"max": 8, "min": 8},
        PlayConfirmType.TeudatZehut: {"max": 9, "min": 8},
        PlayConfirmType.Phone: {"max": 10, "min": 9}
    }
    if play_confirm_type and (in_dict := dict_replace.get(play_confirm_type)) is not None:
        if max_digits is None:
            max_digits = in_dict["max"]
        if min_digits is None:
            min_digits = in_dict["min"]

    result = f"read={message_type}-{message_value}={param_name},{_true_to_str(send_prev_values)},,{_none_to_str(max_digits)},{_none_to_str(min_digits)},{_none_to_str(timeout)},{_none_to_str(play_confirm_type)},{_true_to_str(block_asterisk)},{_true_to_str(block_zero)},{f"{replacment[0]}{replacment[1]}" if replacment else ""},{"".join(map(str, allowed_values)) if allowed_values else ""},{_none_to_str(timout_empty_times)},{_none_to_str(replace_none)},{"InsertLettersTypeChangeNo" if allow_keyboard_language_change is False else ""},{_false_to_str(conform)}"
    return _remove_extra_commas(result)


def read_record(
    message_type: IdListMessageType,
    message_value: str,
    param_name: str,
    send_prev_values: bool = False,
    file_dir: str | None = None,
    file_name: str | None = None,
    conform: bool = True,
    save_hangup: bool = False,
    marge_file: bool = False,
    max_len: int | None = None,
    min_len: int | None = None
) -> str:
    result = f"read={message_type}-{message_value}={param_name},{_true_to_str(send_prev_values)},record,{_none_to_str(file_dir)},{_none_to_str(file_name)},{_false_to_str(conform)},{_true_to_str(save_hangup)},{_true_to_str(marge_file)},{_none_to_str(max_len)},{_none_to_str(min_len)}"
    return _remove_extra_commas(result)


def read_voice(
    message_type: IdListMessageType,
    message_value: str,
    param_name: str,
    send_prev_values: bool = False,
    lang: str | None = None,
    allow_keybord: bool = True,
    max_digits: int | None = None,
    record: bool = False,
    max_len: int | None = None,
    min_len: int | None = None
) -> str:
    result = f"read={message_type}-{message_value}={param_name},{_true_to_str(send_prev_values)},voice,{_none_to_str(lang)},{_false_to_str(allow_keybord)},{_none_to_str(max_digits)},{"record" if record else ""},{_none_to_str(max_len)},{_none_to_str(min_len)}"
    return _remove_extra_commas(result)
