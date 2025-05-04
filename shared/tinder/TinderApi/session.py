import requests
from .exceptions import *
from json import dumps
import requests

class Session():
    def __init__(self, api, **args) -> None:
        self.api = api
        self.v0 = "https://tinder.com"
        self.v1 = "https://api.gotinder.com"
        self.v2 = "https://api.gotinder.com/v2"
        self.v3 = "https://api.gotinder.com/v3"
        self.session = requests.Session()
        # user_agent = args.get("user_agent") if args.get("user_agent") else "Tinder Android Version 13.15.0"
        self.session.headers = args.get("headers")
        
        self.proxies = args.get('proxies')
        self.api.debugger.Log("Initialized session for TinderApi successfully")
        self.api.debugger.Log("Session headers: "+dumps(self.session.headers))

    def get(self, endpoint: str, api_url: int, params={}, json=True, headers={}):
        """_Session get request_

        Args:
            endpoint (_string_): _Endpoint to make a request to, /profile/username for example_
            api_url (int): _Api url version\n0 = https://tinder.com\n1 = https://api.gotinder.com\n2 = https://api.gotinder.com/v2\n3 = https://api.gotinder.com/v3_
            params (dict, optional): _Any params you may need to add to the url_. Defaults to {}.
            json (bool, optional): _True if the request returns json otherwise False_. Defaults to True.
        """
        try:
            ep = self.get_api_url(api_url)+endpoint
            request = self.session.get(ep, params=params, headers=headers, proxies=self.proxies)
            if json:
                return request.json()
            else:
                return request
        except:
            raise InvalidJSONResponse("GET", ep)
            
    def post(self, endpoint, api_url, params={}, data=None, json=True, headers={}, files={}):
        data_type = type(data)
        try:
            ep = self.get_api_url(api_url)+endpoint
            if data_type == dict:
                request = self.session.post(ep, params=params, json=data, headers=headers, files=files, proxies=self.proxies)
            else:
                request = self.session.post(ep, params=params, data=data, headers=headers, files=files, proxies=self.proxies) 
            if json:
                return request.json()
            else:
                return request
        except:
            raise InvalidJSONResponse("POST", ep)
    
    def delete(self, endpoint, api_url, params={}, headers={}):
        try:
            ep = self.get_api_url(api_url)+endpoint
            request = self.session.delete(ep, params=params, headers=headers)
            return request.status_code
        except:
            raise InvalidJSONResponse("DELETE", ep)

    def put(self, endpoint, api_url, params={}, data=None, json=True, headers={}, files={}):
        data_type = type(data)
        try:
            ep = self.get_api_url(api_url)+endpoint
            if data_type == dict:
                request = self.session.put(ep, params=params, json=data, headers=headers, files=files)
            else:
                request = self.session.put(ep, params=params, data=data, headers=headers, files=files) 
            if json:
                return request.json()
            else:
                return request
        except:
            raise InvalidJSONResponse("PUT", ep)
        
    def get_api_url(self, api_url: int) -> str:
        if api_url == 0:
            return self.v0
        elif api_url == 1:
            return self.v1
        elif api_url == 2:
            return self.v2
        elif api_url == 3:
            return self.v3
        return ''
    
    def session_valid(self):
        try:
            res = self.get("/profile", 2, params=f"?locale={self.api.locale}&include=account")
            if 'data' in res:
                return res
            else:
                return False
        except Exception as e:
            return False
            