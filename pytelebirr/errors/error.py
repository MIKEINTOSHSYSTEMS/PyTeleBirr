# error Exceptions

class CredentialError(Exception):
    pass


class TokenExpired(Exception):
    pass


class QRExpiredError(Exception):
    pass
