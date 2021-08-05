from typing import Callable, Union, List
from .errors import CredentialError, TokenExpired, QRExpiredError
from .utils import password_fixer
import json
import os
import threading
import requests
import websocket


class PyTeleBirr:
    def __init__(
            self,
            phone_no: Union[int, str],
            passwd: Union[int, str],
            device_id: str
    ):
        if len(str(passwd)) < 6:
            raise CredentialError(
                "Password Must Be 6 Digit"
            )
        self._headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Host': 'app.ethiomobilemoney.et:2121',
            'Connection': 'Keep-Alive',
        }
        self._qr_header = {
            'authority': 'api.qrcode-monkey.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.164 Safari/537.36',
            'content-type': 'text/plain;charset=UTF-8',
            'accept': '*/*',
            'origin': 'https://www.qrcode-monkey.com',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'referer': 'https://www.qrcode-monkey.com/',
        }
        self._passwd = passwd
        self._phone = phone_no
        self._device_id = device_id
        self._tele_url = "https://app.ethiomobilemoney.et:2121/{}"
        self._r = requests.Session()
        self._base64_pass = password_fixer(self._passwd)
        self._headers['Content-Length'] = str(len(self._base64_pass))
        data = json.dumps({
            "code": None,
            "mid": str(self._phone),
            "password": self._base64_pass,
            "sid": self._device_id,
            "language": "en"
        })
        _res = self._r.post(
            self._tele_url.format("service-information/safelogin"),
            data=data,
            headers=self._headers
        )
        if _res.json()['code'] != 200:
            raise CredentialError(
                "[ Error ] : Password, Phone Number or Device id is incorrect"
            )
        self._token = _res.json()['data']['token']
        self._header = {
            'amm-token': self._token,
            'Content-Type': 'application/json; charset=utf-8',
            'Host': 'app.ethiomobilemoney.et:2121',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }

    def get_balance(self) -> object:
        url = self._tele_url.format(
            "service-transaction/getBalance"
        )
        res = self._r.post(
            url,
            data='{}',
            headers=self._header
        )
        if res.json().get("code") in [401]:
            raise TokenExpired(
                "[ Error ] : Token Expired"
            )
        return res.json()['data']

    def generate_qrcode(
            self,
            amount: Union[str, int] = '',
            size: Union[str, int] = 350,
            bg_color: str = "ffffff",
            logo: str = "e8cb9ae2340c568713010178b6834ad9edced49f.png"
    ) -> str:
        url = self._tele_url.format(
            "service-transfe/produceC2CQRCode"
        )

        res = self._r.post(
            url,
            data=json.dumps(
                {
                    "money": amount,
                    "content": ""
                }
            ),
            headers=self._header
        )
        if res.json().get("code") in [401]:
            raise TokenExpired(
                "[ Error ] : Token Expired"
            )

        _response = requests.get(
            'https://api.qrcode-monkey.com//qr/custom?download=true&file=png&data=' + str(
                res.json()['data'][
                    'content']) + f'&size={size}&config=%7B%22body%22%3A%22mosaic%22%2C%22eye%22%3A%22frame1%22%2C'
                                  '%22eyeBall '
                                  '%22%3A%22ball15%22%2C%22erf1%22%3A%5B%22fh%22%5D%2C%22erf2%22%3A%5B%5D%2C%22erf3'
                                  '%22%3A '
                                  '%5B%22fh%22%2C%22fv%22%5D%2C%22brf1%22%3A%5B%5D%2C%22brf2%22%3A%5B%5D%2C%22brf3%22'
                                  '%3A '
                                  f'%5B%5D%2C%22bodyColor%22%3A%22%23000000%22%2C%22bgColor%22%3A%22%23{bg_color}%22%2C'
                                  '%22eye1Color%22%3A%22%23000000%22%2C%22eye2Color%22%3A%22%23000000%22%2C%22eye3Color'
                                  '%22%3A%22%23000000%22%2C%22eyeBall1Color%22%3A%22%23000000%22%2C%22eyeBall2Color'
                                  '%22%3A '
                                  '%22%23000000%22%2C%22eyeBall3Color%22%3A%22%23000000%22%2C%22gradientColor1%22%3A%22'
                                  '%23CC3873%22%2C%22gradientColor2%22%3A%22%235302BD%22%2C%22gradientType%22%3A'
                                  '%22linear '
                                  '%22%2C%22gradientOnEyes%22%3A%22true%22%2C%22logo%22%3A'
                                  f'%22{logo}%22%2C%22logoMode%22%3A%22clean%22'
                                  '%7D',
            headers=self._qr_header
        )
        if os.path.exists("qr"):
            with open("qr/qr.png", "wb") as f:
                f.write(_response.content)
        else:
            os.mkdir("qr")
            with open("qr/qr.png", "wb") as f:
                f.write(_response.content)
        return "qr/qr.png"

    def refresh_token(self):
        """
        tokens are valid for
        refresh token
        :return:
        """
        _data = json.dumps(
            {
                "code": None,
                "mid": str(self._phone),
                "password": self._base64_pass,
                "sid": self._device_id,
                "language": "en"
            }
        )
        _res = self._r.post(
            self._tele_url.format(
                "service-information/safelogin"
            ),
            data=_data,
            headers=self._header
        )
        if _res.json().get("code") in [401, 1000] or _res.status_code != 200:
            raise TokenExpired(
                "[ Error ] : Password, Phone Number or Device id is incorrect"
            )
        self._token = _res.json()['data']['token']
        print("[ Token Refreshed ]")

    def on_payment(
            self,
            on_payment: Callable,
            on_error: Callable = lambda a: print("Socket error"),
            on_open: Callable = lambda a: print("Socket Connected")
    ) -> None:
        """
        when payment received on_msg will be called

        notice: this method only works when sending payments via qr code

        for phone number payment or ussd payment use by tx id
        """

        def _on_message(_, msg):
            on_payment(msg)

        def _on_closed():
            print("[ Socket Restarted ]")
            self.on_payment(on_payment)

        _ws = websocket.WebSocketApp(
            self._tele_url.format(
                f"websocket?token={self._token}"
            ).replace("https", "wss"),
            on_open=on_open,
            on_message=_on_message,
            on_error=on_error,
            on_close=_on_closed,
            header={
                'Origin': 'http://localhost',
                'Sec-WebSocket-Key': 'aZwQ6W5X+KKAu9jzEdw8Mw==',
                'Host': 'app.ethiomobilemoney.et:2121',
                'User-Agent': 'okhttp/3.12.11'
            }
        )
        print("[ Thread Started ]")
        _tr = threading.Thread(
            target=_ws.run_forever,
            args=()
        )
        _tr.daemon = True
        _tr.start()

    def check_tx(
            self,
            tx_id: str
    ) -> Union[bool, dict]:
        """
        Checks if transaction id is valid
        """
        _url = self._tele_url.format(
            "service-transaction/cusTransactionRecordDetail"
        )
        _res = self._r.post(
            _url,
            data=json.dumps(
                {
                    "receiptNumber": tx_id
                }
            ),
            headers=self._header
        )
        if _res.json().get("code") in [401]:
            raise TokenExpired(
                "[ Error ] : Token Expired"
            )
        _exists = _res.json()
        if _exists.get("code") in [1000, 401]:
            return False
        else:
            return _exists

    def is_my_tx(
            self,
            tx_id: str
    ) -> bool:
        """
        since the api can see all transactions this function
        checks if transaction is send to receiver

        """
        _res = self._r.post(
            self._tele_url.format(
                "service-transaction/cusFourTransactionRecord"
            ),
            data=json.dumps(
                {
                    "startDateTime": "20210622",
                    "endDateTime": "",
                    "type": "1"
                }
            ),
            headers=self._header
        )
        if _res.json().get("code") in [401]:
            raise TokenExpired(
                "[ Error ] : Token Expired"
            )
        _exists = _res.json()
        for _tx in _exists:
            if type(_tx) == list:
                for _t in _tx:
                    if _t.get("receiptNumber") == tx_id:
                        if _t.get("resTransactionType") == "Transfer":
                            if "+" in _t.get("resAmount"):
                                return True
        return False

    def get_packages(
            self
    ) -> List[dict]:
        """
        get all available packages
        :returns: lists of dict
        """
        _res = self._r.post(
            self._tele_url.format(
                "service-topup/productSettings"
            ),
            headers=self._header,
            data=json.dumps(
                {
                    "category": "PACKAGE"
                }
            )
        )
        if _res.json().get("code") in [401]:
            raise TokenExpired(
                "[ Error ] : Token Expired"
            )
        return _res.json()['data']

    def scan_qr(
            self,
            content: Union[str, int] = None
    ):
        """
        get the user data you are sending for
        you can get the receiver phone number by qr code :0
        scan the qr code and pass the content to content param
        :param content: receiver content number scan qr code to get this
        :return: dict
        """
        _res = self._r.post(
            self._tele_url.format(
                'service-transfe/scanReceiveC2CQRCode'
            ),
            headers=self._header,
            data=json.dumps(
                {
                    "content": str(content)
                }
            )
        )
        if _res.json().get("code") in [401]:
            raise TokenExpired(
                "[ Error ] : Token Expired"
            )
        if _res.json()['data']:
            return _res.json()['data']
        else:
            raise QRExpiredError(
                "[ ERROR ] QR expired"
            )

    def _get_umc_session_id(
            self,
            money: Union[str, int],
            phone: Union[str, int],
            content: Union[str, int]
    ) -> dict:
        _data = json.dumps(
            {"money": str(money), "msisdn": str(phone), "pin": password_fixer(self._passwd), "content": str(content)})
        print(_data)
        self._header['Content-Length'] = str(len(_data))
        _res = self._r.post(
            self._tele_url.format(
                'service-transfe/getTransferInfo'
            ),
            headers=self._header,
            data=_data
        )
        if _res.json().get("code") in [401]:
            raise TokenExpired(
                "[ Error ] : Token Expired"
            )
        print(_res.text)
        return _res.json()['data']

    def send_payment(
            self,
            amount: Union[str, int],
            phone: Union[str, int],
            content: Union[str, int]
    ):
        umc_id = self._get_umc_session_id(
            phone=phone,
            money=amount,
            content=content
        )['umcSessionId']
        print(umc_id)
        _res = self._r.post(
            self._tele_url.format(
                'service-transfe/syncTransferC2C'
            ),
            headers=self._header,
            data=json.dumps(
                {
                    "confirmationAction": "1",
                    "umcSessionId": umc_id,
                    "flag": "",
                    "mid": phone
                }
            )
        )
        if _res.json().get("code") in [401]:
            raise TokenExpired(
                "[ Error ] : Token Expired"
            )
        print(_res.text)
        return _res.json()['data']

    def get_token(self):
        return self._token
