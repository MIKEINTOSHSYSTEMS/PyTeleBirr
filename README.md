<p align="center">
<a href="https://github.com/telebirrapi/pytelebirr">
<img src="https://raw.githubusercontent.com/TeleBirrApi/PyTeleBirr/main/.github/images/telebirrapi.png" alt="Pytelebirr">
</a>
<br>
<b>PyTeleBirr is mostly Telebirr With Python</b>
<br>
<a href="https://github.com/telebirrapi/pytelebirr/tree/main/examples">
Examples</a>
 | 
<a href="https://telebirrapi.github.io/PyTeleBirr/">
Documentation</a>
 | 
<a href="https://t.me/PyTeleBirr">  
Channel</a>


#### Installation

`pip3 install pytelebirr`

#### Usage

````python
from pytelebirr import PyTeleBirr

phone_no = "<YOUR_PHONE_NUMBER_STARTS_FROM_9>" # Example 91234567
passwd = "<YOUR_PASSWORD>"

# To get Device id use 
from pytelebirr.utils import get_device_id
device_id = get_device_id(
    phone=phone_no,
    passwd=passwd,
    d_id="<Your Mobile Device ID>" # to get this for android users use device id app for iphone users ¯\_(ツ)_/¯
)
# after calling this function verification code will be sent via sms check 127
# Code has been sent via sms
# Enter The Code You Received : enter your code here
# and you will get this message on terminal/cmd Your Device_id :  ...


# Initialize PyTelebirr
telebirr = PyTeleBirr(
    device_id=device_id,
    phone_no=phone_no,
    passwd=passwd,
)

# get your balance
balance = telebirr.get_balance()
# this returns dict
balance['balance']
# 999999.00

# generate beautiful qr code
# now you can custom your qr code size and background color and payment amount
img_path = telebirr.generate_qrcode(
    amount=5, # 5 in birr
    size=200, # optional
    bg_color="ffffff" # color don't use #
)
# this return image path 

# refresh token tokens will expire in 86400s after login
telebirr.refresh_token()
# this will refresh token

# on payment received method you can pass callable
telebirr.on_payment(
    on_payment=lambda m: print(m)
)
# when payment received on_payment function will be called

# to check if transaction exists
# returns bool or dict
telebirr.check_tx(
    "ABCDE"
)
# if tx id exists will return dict elase false
# this method can check all telebirr transaction so be careful

# check if the tx id payment was sent to me
telebirr.is_my_tx(
    "ABCDE"
)
# returns bool if tx id was sent to me returns True else False

# scan qr code
# scan the receiver qr code and pass the content 
telebirr.scan_qr(
    "1234567890"
)
# returns dict data of user including phone number ;)

# send payment to user via qr code
telebirr.send_payment(
    amount=5,
    phone="1234567890",
    content="123456789"  # content of qr code
)
# returns dict

# get your token
telebirr.get_token()
# returns str your token

````

### Features
- Python solution.
- Send payment via qr code and phone number
- Checking balance
- Generating beautiful qr code
- you can custom your qr code 
- Checking transactions
- Waiting for payment and call function
