# PyTeleBirr API
> Pytelebirr is mostly Telebirr with python

# Recent changes

>
# Methods
These are the currently available PyTeleBirr methods

## PyTelebirr
Class initialization

Field | Type | Description
--- | --- | ---
phone_no | str,int | Your Telebirr Phone Number
passwd | str,int | Your Telebirr Password
device_id | str | Your telebirr device id when you first login with the app it will be sent via sms

### _Example_
``` python
...
from pytelebirr import PyTeleBirr

telebirr = PyTeleBirr(
    phone_no="<YOUR_PHONE>",
    passwd="<YOUR_PASSWORD>",
    device_id="<YOUR_DEVICE_ID>"
)
...
```


## get_balance()
Get Your Balance
### _Example_
``` python
...
from pytelebirr import PyTeleBirr

trelebirr = PyTeleBirr(...)
telebirr.get_balance()
"""
returns: dict
{
    "balance": "9999999.00"
    "currency": "ETB"
}   
"""
...
```

## generate_qrcode()
Generate Beautifull qr code

Field | Type | Description
--- | --- | ---
amount (Optional) | int,str | amount of money you are receiving

### _Example_
``` python
...
from pytelebirr import PyTeleBirr

trelebirr = PyTeleBirr(...)
telebirr.generate_qrcode()

# returns str path of image
# img/qrcode.png
...
```

## refresh_token
Refresh jwt token
> tokens will expire in 86400s after login

### _Example_
``` python
....
from pytelebirr import PyTeleBirr

trelebirr = PyTeleBirr(...)
telebirr.refresh_token()
...
```

## on_payment
Triggers function when payment received

Field | Type | Description
--- | --- | ---
on_payment | Callable | Function to call when payment received

### _Example_
``` python
...
from pytelebirr import PyTeleBirr

trelebirr = PyTeleBirr(...)

telebirr.on_payment(
    on_payment= lambda m: print(m)
)

#returns dict 
{
    "amount": "+9999",
    "currency": "ETB",
    "transactionFrom": "qwertyuiop",
    "transactionTime": "123456789",
    "transactionType": "transfer"
 }
...
```

> ### Warning!
> This function only works for qr code payments only

## check_tx
Check if transaction exists

Field | Type | Description
--- | --- | ---
tx_id | str | the transaction id

### _Example_
``` python
...
from pytelebirr import PyTeleBirr

trelebirr = PyTeleBirr(...)

telebirr.check_tx(
    "ABCDE"
)
# if tx id exists will return dict elase false
# this method can check all telebirr transaction so be careful
{
    "receiptNumber": "qwerty",
    "resFinalizedTime": "2020/01/01 01:01:01",
    "resTransactionType": "transfer",
    "resAmount": "999.00",
    "resCurrency": "ETB",
    "transactionFrom": "qwertyuiop"
    #...
}
...
```


## change_stream
Change audio stream without reconnection

Field | Type | Description
--- | --- | ---
tx_id | str | the transaction id

### _Example_
``` python
...
from pytelebirr import PyTeleBirr

trelebirr = PyTeleBirr(...)

telebirr.is_my_tx(
    "ABCDE"
)
# returns bool 
# if tx id was sent to user returns True else False

...
```
## scan_qr
Check if qr code is valid

Field | Type | Description
--- | --- | ---
content | str,int | qr code content

### _Example_
``` python
...
from pytelebirr import PyTeleBirr

trelebirr = PyTeleBirr(...)

telebirr.scan_qr(
    "1234567890"
)
# 
...
```

## send_payment
send payment to user via qr code

### _Example_
``` python
...
from pytelebirr import PyTeleBirr

trelebirr = PyTeleBirr(...)
telebirr.send_payment(
    amount=5,
    phone="1234567890",
    content="123456789" # scan qr code and pass content
)
# returns dict
...
```

# Exceptions

## TokenExpired
This error occurs when token expired use refresh_token to fix

## CredentialError
This error occurs when phone number,password or device id is incorrect
