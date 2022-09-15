class Response:
    def __init__(self, method, url, body, status, reason, headers):
        self.method = method
        self.url = url
        self.body = body
        self.status = status
        self.reason = reason
        self.headers = headers

    def __str__(self):
        return f'Response[{self.status}, {self.url}]'

    def __repr__(self):
        return str(self)
