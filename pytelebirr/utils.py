import random
from typing import Union
from base64 import b64encode
import requests as r
import hashlib
import json
from base64 import b16decode as l
from .errors import CredentialError


def password_fixer(
        password: Union[int, str]
):
    last_n = list(str(password)[-2:])
    last_n.reverse()
    return b64encode(
        (str(random.randint(1, 9)) + str(password)[:-2] + str("".join(last_n)) + str(random.randint(1, 9))).encode()
    ).decode()


def get_device_id(
        d_id: str,
        phone: Union[str, int],
        passwd: Union[str, int]
):
    """
    Warning: Use this function only once
    use the returned value as device_id on PyTeleBirr

    :param d_id: your android device id
    :param phone: your phone number
    :param passwd: your telebirr password
    :return: str
    """
    _headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Host': 'app.ethiomobilemoney.et:2121',
        'Connection': 'Keep-Alive',
        "Device-ID": d_id
    }
    _tele_url = "https://app.ethiomobilemoney.et:2121/{}"
    _hashed = hashlib.md5(d_id.encode()).hexdigest()
    print("Your Device_id : ", _hashed)
    res = r.post(
        _tele_url.format(l("736572766963652D696E666F726D6174696F6E2F6D53564353656E64").decode()),
        headers=_headers,
        data=json.dumps(
            {
                "msisdn": phone,
                "bizType": 3
            }
        )
    )
    if res.json()['code'] == 200:
        print("Code has been sent via sms")
        sms_code = input("Enter The Code You Received : ")
        data = json.dumps({
            "code": str(sms_code),
            "mid": str(phone),
            "password": password_fixer(passwd),
            "sid": str(_hashed),
            "language": "en"
        })
        res = r.post(
            _tele_url.format("service-information/safelogin"),
            data=data,
            headers=_headers
        )
        if res.status_code != 200:
            raise CredentialError(
                "[ Error ] : Password, Phone Number or Device id is incorrect"
            )
        else:
            return _hashed

