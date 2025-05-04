from shared.tinder.TinderApi.api.account import Account
from shared.tinder.TinderApi.api.misc import Misc
from shared.tinder.TinderApi.api.matches import Matches
from shared.tinder.TinderApi.api.media import Media
from shared.tinder.TinderApi.api.user import User
from shared.tinder.TinderApi.api.swipe import Swipe
from shared.tinder.TinderApi.debugger import Debugger
from shared.tinder.TinderApi.session import Session
from shared.tinder.TinderApi.utils import Utils


class Tinder:
    def __init__(self, debug=False, **args) -> None:
        self.debugger = Debugger(debug=True) if debug else Debugger()
        self.locale = args.get("locale") if args.get("locale") else "en"
        self.s = Session(self, **args)
        self.next_page_token = ""
        self.contact_types = ["snapchat", "instagram"]
        self.util = Utils(self)
        self.media = Media(self)
        self.misc = Misc(self)
        self.matches = Matches(self)
        self.user = User(self)
        self.account = Account(self)
        self.swipe = Swipe(self)

    def is_suspiscious(self):
        res = self.s.get("/healthcheck/auth", 1)
        if res["data"]["ok"]:
            return True
        else:
            return False
