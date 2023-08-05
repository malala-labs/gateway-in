class Request:
    def __init__(self, token, module, service):
        self.token = token
        self.module = module
        self.service = service

    def to_json(self):
        return self.__dict__


class WsAuth(Request):
    def __init__(self, params):
        Request.__init__(self, None, "login", "authentication")
        self.parameters = {
            "login": params.get("usr_cedro"),
            "password": params.get("psw_cedro"),
            "account": params.get("usr_oms"),
        }
