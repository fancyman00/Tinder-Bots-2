class AuthException(Exception):
    def __init__(self, value):
        self.value = value
        super().__init__(f"AuthException: {value}")