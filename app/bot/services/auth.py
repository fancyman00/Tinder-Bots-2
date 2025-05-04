from annotated_types import T
from bot.exceptions import BotAuthException
from bot.schemas.auth import AuthBase, AuthCancel, UpdateOTP
from bot.database.crud import BotCRUD
from bot.database.models.bot import Bot
from base.infrastructure.client import Client


class AuthService[BotType: Bot, CodeType, CrudType: BotCRUD, ClientType: Client]:
    def __init__(self, crud: CrudType, client: ClientType):
        self.crud = crud
        self.Client: ClientType = client

    async def is_authorized(self, bot_id: int):
        bot: BotType = await self.crud.is_exist(bot_id)
        return bot.is_auth

    async def is_otp_requested(self, bot_id: int):
        bot: BotType = await self.crud.is_exist(bot_id)
        return bot.otp_requested
        
    async def request_authorize(self, bot_id: int, state=True):
        try:
            bot: BotType = await self.crud.is_exist(bot_id)
            if state:
                if not bot.otp_requested:
                    async with self.Client(bot_id, bot.proxy) as client:
                        await client.request_authorize(bot)
                    await self.crud.update(item_id=bot_id, data=UpdateOTP(otp_requested=True))
                else:
                    raise BotAuthException("Authorize already requested!")
            else:
                if bot.otp_requested or bot.is_auth:
                    await self.crud.update(item_id=bot_id, data=AuthCancel(otp_requested=False, is_auth=False))
                else:
                    raise BotAuthException("Authorization not requested!")
        except Exception as e:
            raise e

    async def confirm_authorize(self, bot_id: int, code: CodeType):
        try:
            bot: BotType = await self.crud.is_exist(bot_id)
            if bot.otp_requested:
                async with self.Client(bot_id, bot.proxy) as client:
                    await client.confirm_authorize(bot, code)
                await self.crud.update(item_id=bot_id, data=AuthBase(otp_requested=True, is_auth=True))
            else:
                raise BotAuthException("Request authorization!")
        except Exception as e:
            raise e
