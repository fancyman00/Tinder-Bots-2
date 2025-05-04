from fastapi import HTTPException
from functools import wraps

def handle_exceptions(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        try:
            return await f(*args, **kwargs)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    return decorated_function

class BotNotFound(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        if args:
            self.bot_id = args[0]
        else:
            self.bot_id = None

    def __str__(self):
        return f"Bot with id '{self.bot_id}' not found"
    
class BotAuthException(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        return f"Exception in bot authorization: {self.message}"