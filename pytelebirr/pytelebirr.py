import asyncio
import json
import os
import random
import threading
import requests
import websocket
from base64 import b64encode
from types import SimpleNamespace
from typing import Callable, Union
from .errors import PasswordError, TokenExpired

headers = {
    'user-agent': '(Android/8.1.0) (com.ethiotelecom.pytelebirr) UniApp/0.28.0 480x888',
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': '114',
    'Host': 'app.ethiomobilemoney.et:2121',
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip',
}


class PyTeleBirr:
    def __init__(self, phone_no: Union[int, str], passwd: Union[int, str], device_id: str):
        if len(str(passwd)) < 6:
            raise PasswordError("Password Must Be 6 Digit")
        self.passwd = passwd
        self.phone = phone_no
        self.device_id = device_id
        self.tele_url = "https://app.ethiomobilemoney.et:2121/{}"
        self.r = requests
        last_n = list(str(passwd)[-2:])
        last_n.reverse()
        rr = str(random.randint(1, 9)) + str(self.passwd)[:-2] + str("".join(last_n)) + str(random.randint(1, 9))
        headers['Content-Length'] = str(len(b64encode(rr.encode()).decode()))
        self.base64_pass = b64encode(rr.encode()).decode()
        data = json.dumps({
            "code": None,
            "mid": str(self.phone),
            "password": self.base64_pass,
            "sid": self.device_id,
            "language": "en"
        })
        res = self.r.post(self.tele_url.format("service-information/safelogin"), data=data, headers=headers)
        if res.status_code != 200:
            raise TokenExpired("Password, Phone Number or Device id is incorrect")
        print(res.json())
        self.token = res.json()['data']['token']

    def get_balance(self):
        url = self.tele_url.format("service-transaction/getBalance")
        header = {
            'amm-token': self.token
        }
        res = self.r.post(url, data='{}', headers=header)
        if res.json().get("code") in [401]:
            raise TokenExpired("Token Expired")
        print(res.json())
        return json.loads(json.dumps(res.json()['data']), object_hook=lambda d: SimpleNamespace(**d))

    def generate_qrcode(
            self,
            amount: [str, int] = ''
    ) -> str:
        url = self.tele_url.format(
            "service-transfe/produceC2CQRCode"
        )
        header = {
            'amm-token': self.token,
            "Content-Type": "application/json; charset=utf-8",
            "Host": "app.ethiomobilemoney.et:2121"
        }
        res = self.r.post(
            url,
            data=json.dumps({"money": amount, "content": ""}),
            headers=header
        )
        print(res.json())
        if res.json().get("code") in [401]:
            raise TokenExpired("Token Expired")
        header = {
            'authority': 'api.qrcode-monkey.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.164 Safari/537.36',
            'content-type': 'text/plain;charset=UTF-8',
            'accept': '*/*',
            'sec-gpc': '1',
            'origin': 'https://www.qrcode-monkey.com',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.qrcode-monkey.com/',
            'accept-language': 'en-US,en;q=0.9',
        }
        response = requests.get('https://api.qrcode-monkey.com//qr/custom?download=true&file=png&data=' + str(
            res.json()['data'][
                'content']) + '&size=350&config=%7B%22body%22%3A%22mosaic%22%2C%22eye%22%3A%22frame1%22%2C%22eyeBall%22%3A%22ball15%22%2C%22erf1%22%3A%5B%22fh%22%5D%2C%22erf2%22%3A%5B%5D%2C%22erf3%22%3A%5B%22fh%22%2C%22fv%22%5D%2C%22brf1%22%3A%5B%5D%2C%22brf2%22%3A%5B%5D%2C%22brf3%22%3A%5B%5D%2C%22bodyColor%22%3A%22%23000000%22%2C%22bgColor%22%3A%22%23FFFFFF%22%2C%22eye1Color%22%3A%22%23000000%22%2C%22eye2Color%22%3A%22%23000000%22%2C%22eye3Color%22%3A%22%23000000%22%2C%22eyeBall1Color%22%3A%22%23000000%22%2C%22eyeBall2Color%22%3A%22%23000000%22%2C%22eyeBall3Color%22%3A%22%23000000%22%2C%22gradientColor1%22%3A%22%23CC3873%22%2C%22gradientColor2%22%3A%22%235302BD%22%2C%22gradientType%22%3A%22linear%22%2C%22gradientOnEyes%22%3A%22true%22%2C%22logo%22%3A%22e8cb9ae2340c568713010178b6834ad9edced49f.png%22%2C%22logoMode%22%3A%22clean%22%7D',
                                headers=header)
        if os.path.exists("qr"):
            with open("qr/qr.png", "wb") as f:
                f.write(response.content)
        else:
            os.mkdir("qr")
            with open("qr/qr.png", "wb") as f:
                f.write(response.content)
        return "qr/qr.png"

    def refresh_token(self):
        data = json.dumps({
            "code": None,
            "mid": str(self.phone),
            "password": self.base64_pass,
            "sid": self.device_id,
            "language": "en"
        })
        res = self.r.post(self.tele_url.format("service-information/safelogin"), data=data, headers=headers)
        if res.json().get("code") in [401, 1000] or res.status_code != 200:
            raise TokenExpired("Password, Phone Number or Device id is incorrect")
        self.token = res.json()['data']['token']

    def on_payment(
            self,
            on_msg: Callable,
            on_error: Callable = lambda a: print("Socket error"),
            on_open: Callable = lambda a: print("Socket Connected")
    ) -> None:
        print("thread started")

        def on_message(_, msg):
            loop = asyncio.new_event_loop()
            m = '{"code":200,"data":{"amount":"+1","currency":"ETB","transactionFrom":"yohanes feleke sahilu",' \
                '"transactionTime":"20210720185841","transactionType":"transfer"},"message":"操作成功",' \
                '"operationNumber":"1417510745919426561"} '
            loop.run_until_complete(on_msg(msg))

        # on_message("kk", "jj")

        def on_closed():
            print("restarted socket")
            self.on_payment(on_msg)

        ws = websocket.WebSocketApp(
            self.tele_url.format(f"websocket?token={self.token}").replace("https", "wss"),
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_closed,
            header={
                'Origin': 'http://localhost',
                'Sec-WebSocket-Key': 'aZwQ6W5X+KKAu9jzEdw8Mw==',
                'Host': 'app.ethiomobilemoney.et:2121',
                'User-Agent': 'okhttp/3.12.11'
            }
        )

        tr = threading.Thread(target=ws.run_forever, args=())
        tr.daemon = True
        tr.start()

    def check_tx(self, tx_id):
        url = self.tele_url.format(
            "service-transaction/cusTransactionRecordDetail"
        )
        header = {
            'amm-token': self.token,
            "Content-Type": "application/json; charset=utf-8",
            "Host": "app.ethiomobilemoney.et:2121"
        }
        res = self.r.post(
            url,
            data=json.dumps({"receiptNumber": tx_id}),
            headers=header
        )
        if res.json().get("code") in [401]:
            raise TokenExpired("Token Expired")
        print(res.json())
        exists = res.json()
        if exists.get("code") in [1000, 401]:
            return False
        else:
            return exists

    def is_my_tx(self, tx_id: str) -> bool:
        url = self.tele_url.format(
            "service-transaction/cusFourTransactionRecord"
        )
        header = {
            'amm-token': self.token,
            "Content-Type": "application/json; charset=utf-8",
            "Host": "app.ethiomobilemoney.et:2121"
        }
        res = self.r.post(
            url,
            data=json.dumps({"startDateTime": "20210622", "endDateTime": "", "type": "1"}),
            headers=header
        )
        if res.json().get("code") in [401]:
            raise TokenExpired("Token Expired")
        print(res.json())
        exists = res.json()
        for tx in exists:
            if type(tx) == list:
                for t in tx:
                    if t.get("receiptNumber") == tx_id:
                        if t.get("resTransactionType") == "Transfer":
                            if "+" in t.get("resAmount"):
                                return True
        return False
