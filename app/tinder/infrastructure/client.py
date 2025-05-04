import asyncio
from datetime import datetime
import json
from typing import List, Tuple
from app.bot.schemas.auth import OtpConfirm
from app.tinder.database.models.bot import TinderBot
from app.tinder.infrastructure.schemas import LikeResponse, Match, Message, SwipeUser
from shared.tinder.TinderApi.tinder import Tinder
from shared.tinder.run import (
    debug_response,
    get_photos_from_folder,
    get_sms_activate_number,
    setup_additional_profile_settings,
    try_api_call,
    upload_photos,
)
from shared.tinder.sms_activate import poll_sms_code
from shared.tinder.tinder_client import TinderClient as TinderAuthClient
from thaifriendly.infrastructure.exc import AuthException
from base.infrastructure.client import Client
from loguru import logger


class TinderClient(Client):
    def __init__(self, bot_id: int, proxy: str = None):
        super().__init__(
            use_default_client=False,
            proxy=proxy,
            identity=f"tinder:{bot_id}",
            params=["headers", "profile", "session_info", "credentials"],
        )
        self.bot_id = bot_id
        self.auth_client = TinderAuthClient(
            userAgent="Tinder/14.21.0 (iPhone; iOS 14.2.0; Scale/2.00)",
            platform="ios",
            tinderVersion="14.21.0",
            appVersion="5546",
            osVersion=140000200000,
            language="en-US",
            proxy=self.proxy,
        )
        self.tinder = None

    async def load_session(self) -> bool:
        try:
            await super().load_session()
            if session_info := self.session["session_info"]:
                self.auth_client = TinderAuthClient.fromObject(session_info)
                self.tinder = Tinder(debug=True, headers=self.auth_client._getHeaders_POST_JSON(), proxies=self.proxies)
            else:
                return False
            health_check = self.auth_client.healthCheckAuth()
            return health_check['data']['ok']
        except Exception as e:
            logger.error(f"Session load failed: {e}")

    async def request_authorize(self, bot: TinderBot) -> bool:
        try:
            buckets_response = self.auth_client.sendBuckets()
            if not buckets_response:
                raise Exception("Failed to initialize session")
            await asyncio.sleep(2)

            login_response = self.auth_client.authLogin(bot.phone_number)
            if not login_response:
                raise Exception("No response from server")
            if "error" in login_response:
                raise Exception(f"Login error: {login_response['error']}")
            self.session["session_info"] = self.auth_client.toObject()
            await self.save_session()
        except Exception as e:
            await self.clear_session()
            logger.error(f"Authorization request failed: {e}")
            raise e

    async def confirm_authorize(
        self, bot: TinderBot, code: OtpConfirm
    ) -> Tuple[bool, str]:
        try:
            photos = get_photos_from_folder(
                f"C:/Users/fancy/Documents/WORK/Tinder-Bots/storage/tinder/{bot.id}"
            )
            if not photos:
                raise Exception(
                    "No photos found in the photos directory! Please add some photos and try again."
                )
            otp_response = self.auth_client.verifyOtp(bot.phone_number, code.code)
            if "error" not in otp_response:
                email_response = self.auth_client.useEmail(bot.email)
                if "error" not in email_response:
                    dismiss_response = self.auth_client.dismissSocialConnectionList()
                    logger.debug(
                        "Dismiss response:", json.dumps(dismiss_response, indent=2)
                    )
                    auth_response = self.auth_client.getAuthToken()
                    logger.debug(
                        "Auth token response:", json.dumps(auth_response, indent=2)
                    )
                    if "error" in auth_response:
                        raise Exception("No success when auth")
                else:
                    raise Exception("No success when auth")
            else:
                raise Exception("No success when auth")
            await asyncio.sleep(2)
            onboarding_response = self.auth_client.startOnboarding()
            if not onboarding_response:
                raise Exception("Failed to start onboarding process")
            await asyncio.sleep(2)

            info_response = self.auth_client.onboardingSuper(
                bot.name, bot.dob, int(bot.gender), [int(bot.lookingfor)]
            )
            if not info_response:
                raise Exception("Failed to set basic information")
            await asyncio.sleep(2)

            setup_additional_profile_settings(self.auth_client)
            await asyncio.sleep(2)

            upload_photos(self.auth_client, photos)
            await asyncio.sleep(2)

            complete_response = self.auth_client.endOnboarding()
            logger.debug(
                "Registration complete response:",
                json.dumps(
                    debug_response(
                        complete_response, self.auth_client.last_status_code
                    ),
                    indent=2,
                ),
            )

            if self.auth_client.last_status_code != 200:
                if self.auth_client.processCaptcha():
                    logger.debug("Challenge resolved successfully!")
                else:
                    raise Exception("Failed to resolve challenge")

            try:
                await asyncio.sleep(3)
                try_api_call(
                    self.auth_client,
                    lambda: self.auth_client.updateLocation(bot.latitude, bot.longitude),
                    "Updating location",
                )
                await asyncio.sleep(1)
                try_api_call(
                    self.auth_client,
                    lambda: self.auth_client.locInit(),
                    "Initializing location services",
                )
                await asyncio.sleep(1)
                try_api_call(
                    self.auth_client,
                    lambda: self.auth_client.updateLocalization(bot.latitude, bot.longitude),
                    "Updating localization",
                )
            except Exception as e:
                logger.debug(f"Warning: Could not set location: {str(e)}")

            try:
                self.session["session_info"] = self.auth_client.toObject()
            except Exception as e:
                logger.debug(f"Warning: Could not save session information: {str(e)}")
            self.session["credentials"] = {
                "user_id": self.auth_client.userId,
                "email": bot.email,
                "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "proxy_used": self.proxy,
                "ip_used": self.auth_client.checkIp(),
            }
            self.session["headers"] = self.auth_client._getHeaders_POST_JSON()
        except Exception as e:
            await self.clear_session()
            logger.info(f"Confirmation error {str(e)}")
            raise e
        
    async def auto_authorize(self, bot: TinderBot):
        SMS_API_KEY = ""
        photos = get_photos_from_folder(
                f"C:/Users/fancy/Documents/WORK/Tinder-Bots/storage/tinder/{bot.id}"
            )
        if not photos:
            raise Exception(
                "No photos found in the photos directory! Please add some photos and try again."
            )
        sms_data = await get_sms_activate_number(SMS_API_KEY)
        if not sms_data:
            raise Exception("Error in get sms_activate")
        phone_number = sms_data["phone_number"]
        activation_id = sms_data["activation_id"]
        logger.debug(f"Using phone number: {phone_number} for authentication")
        
        login_response = self.auth_client.authLogin(phone_number)
        if not login_response:
            raise Exception("No response from server")
        if 'error' in login_response:
            raise Exception(f"Login error: {login_response['error']}")
        otp = await poll_sms_code(SMS_API_KEY, activation_id)
        if not otp:
            raise Exception("Failed to obtain OTP code")

        logger.debug(f"Verifying OTP: {otp}")
        otp_response = self.auth_client.verifyOtp(phone_number, otp)
        if 'error' not in otp_response:
            logger.debug("Phone verification successful!")
            email_response = self.auth_client.useEmail(bot.email)
            logger.debug("Email registration response:", json.dumps(email_response, indent=2))
            if 'error' not in email_response:
                self.auth_client.dismissSocialConnectionList()
                logger.debug("Getting authentication token...")
                auth_response = self.auth_client.getAuthToken()
                logger.debug("Auth token response:", json.dumps(auth_response, indent=2))
                if 'error' in auth_response:
                    raise Exception("Error in auth response")
            else:
                raise Exception("Error in email response")
        else:
            raise Exception("Authentication step failed.")
        onboarding_response = self.auth_client.startOnboarding()
        if not onboarding_response:
            raise Exception("Failed to start onboarding process")
        await asyncio.sleep(2)

        info_response = self.auth_client.onboardingSuper(
            bot.name, bot.dob, int(bot.gender), [int(bot.lookingfor)]
        )
        if not info_response:
            raise Exception("Failed to set basic information")
        await asyncio.sleep(2)

        setup_additional_profile_settings(self.auth_client)
        await asyncio.sleep(2)

        upload_photos(self.auth_client, photos)
        await asyncio.sleep(2)

        complete_response = self.auth_client.endOnboarding()
        logger.debug(
            "Registration complete response:",
            json.dumps(
                debug_response(
                    complete_response, self.auth_client.last_status_code
                ),
                indent=2,
            ),
        )

        if self.auth_client.last_status_code != 200:
            if self.auth_client.processCaptcha():
                logger.debug("Challenge resolved successfully!")
            else:
                raise Exception("Failed to resolve challenge")

        try:
            await asyncio.sleep(3)
            ip = self.auth_client.checkIp()
            lat, lng = self.auth_client.getLocation(ip)
            try_api_call(
                self.auth_client,
                lambda: self.auth_client.updateLocation(lat, lng),
                "Updating location",
            )
            await asyncio.sleep(1)
            try_api_call(
                self.auth_client,
                lambda: self.auth_client.locInit(),
                "Initializing location services",
            )
            await asyncio.sleep(1)
            try_api_call(
                self.auth_client,
                lambda: self.auth_client.updateLocalization(lat, lng),
                "Updating localization",
            )
        except Exception as e:
            logger.debug(f"Warning: Could not set location automatically: {str(e)}")

        try:
            self.session["session_info"] = self.auth_client.toObject()
        except Exception as e:
            logger.debug(f"Warning: Could not save session information: {str(e)}")
        self.session["credentials"] = {
            "user_id": self.auth_client.userId,
            "email": bot.email,
            "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "proxy_used": self.proxy,
            "ip_used": self.auth_client.checkIp(),
        }
        self.session["headers"] = self.auth_client._getHeaders_GET_JSON()
        
    async def send_like(self, username: str) -> LikeResponse:
        try:
            return LikeResponse(**self.tinder.swipe.like_user(username))
        except AuthException:
            raise
        except Exception as e:
            raise

    async def get_users_for_interaction(self) -> List[SwipeUser]:
        try:
            users = self.tinder.swipe.get_users()
            return [SwipeUser(**user) for user in users]
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            return []

    async def get_matches(self) -> List[Match]:
        try:
            return [Match(**match) for match in self.tinder.matches.get_all_matches()]
        except AuthException:
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
        except Exception as e:
            logger.error(f"Failed to get matches: {e}", exc_info=True)
            raise

    async def get_conversations(self, username: str) -> List[Message]:
        try:
            return Match(**self.tinder.matches.get_match(username)).messages
        except Exception as e:
            logger.error(f"Failed to get conversations")
            return []

    async def send_message(self, username: str, message: str) -> Tuple[bool, str, int]:
        try:
            self.tinder.matches.send_message(username, message)
        except AuthException as e:
            raise e
