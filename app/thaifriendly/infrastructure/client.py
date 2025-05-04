import asyncio
import json
import httpx
from typing import List, Optional, Tuple
from urllib.parse import urlencode, urljoin, urlparse, parse_qs
from app.bot.schemas.auth import OtpConfirm
from thaifriendly.infrastructure.exc import AuthException
from app.thaifriendly.infrastructure.schemas import UserPlay, UserProfile
from app.thaifriendly.database.models.bot import ThaifriendlyBot
from base.infrastructure.client import Client
from redis import asyncio as aioredis
from loguru import logger
from config import settings
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class ThaiFriendlyClient(Client):
    BASE_URL = "https://www.thaifriendly.com"
    AUTH_PARAMS = ["a", "u", "uid", "tgz"]
    RETRY_CONFIG = {
        "stop": stop_after_attempt(3),
        "wait": wait_exponential(multiplier=1, min=1, max=5),
        "retry": retry_if_exception_type((httpx.NetworkError, httpx.TimeoutException)),
        "reraise": True
    }

    def __init__(self, bot_id: int, proxy: str):
        super().__init__(
            use_default_client=False,
            proxy=proxy,
            identity=f"thaifriendly:{bot_id}",
            params=["cookies", "likes", "activity", "profile"],
        )
        self.bot_id = bot_id
        self._redis_pool = None
        self._client = None

    @property
    async def redis(self) -> aioredis.Redis:
        """Lazy-loaded Redis connection pool"""
        if not self._redis_pool or await self._redis_pool.ping() is False:
            self._redis_pool = aioredis.Redis(
                host=settings.REDIS.HOST,
                port=settings.REDIS.PORT,
                username=settings.REDIS.USER,
                password=settings.REDIS.PASS,
                db=settings.THAIFRIENDLY.COOKIES_REDIS_DB,
                socket_timeout=5,
                decode_responses=True
            )
        return self._redis_pool

    async def load_session(self) -> bool:
        """Load session with enhanced error handling"""
        try:
            await super().load_session()
            if not self.session.get("profile"):
                logger.warning("No profile found in session")
                return False
            return True
        except (aioredis.RedisError, json.JSONDecodeError) as e:
            logger.error("Session load failed: {error}", error=str(e))
            return False

    def _build_auth_query(self) -> str:
        """Generate authenticated query parameters"""
        profile = self.session.get("profile", {})
        return urlencode({k: profile.get(k) for k in self.AUTH_PARAMS if profile.get(k)})

    def _add_auth_to_url(self, url: str) -> str:
        """Add authentication parameters to URL efficiently"""
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        query.update({k: [v] for k, v in parse_qs(self._build_auth_query()).items()})
        return parsed._replace(query=urlencode(query, doseq=True)).geturl()

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with connection pooling"""
        if not self._client:
            self._client = httpx.AsyncClient(
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/json",
                },
                timeout=30,
                follow_redirects=True
            )
        return self._client

    @retry(**RETRY_CONFIG)
    async def _request(
        self,
        method: str,
        path: str,
        data: Optional[dict] = None,
        **kwargs
    ) -> httpx.Response:
        """Enhanced request handler with retry logic"""
        client = await self._get_client()
        url = self._add_auth_to_url(urljoin(self.BASE_URL, path))
        
        try:
            response = await client.request(
                method=method,
                url=url,
                data=data,
                cookies=self.session.get("cookies", {}),
                **kwargs
            )
            response.raise_for_status()
            
            if any(err in response.text.lower() for err in ["badtoken", "verifyprofile"]):
                raise AuthException("Authentication expired or invalid")

            return response
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error {status}: {msg}", status=e.response.status_code, msg=e.response.text)
            raise
        finally:
            if method != "GET":
                await client.aclose()
                self._client = None

    async def request_authorize(self, bot: ThaifriendlyBot) -> bool:
        """Handle authorization request with validation"""
        payload = {
            "z": "emailcodesend",
            "usernameoremail": bot.email,
            "signup": "1"
        }
        try:
            response = await self._request("POST", "/nt/app.php", data=payload)
            return response.json().get("success", False)
        except httpx.RequestError as e:
            logger.error("Network error during authorization: {error}", error=str(e))
            return False

    async def confirm_authorize(self, bot: ThaifriendlyBot, code: OtpConfirm) -> Tuple[bool, str]:
        """Handle authorization confirmation with session management"""
        payload = {
            "z": "emailcodeconfirm",
            "usernameoremail": bot.email,
            "emailcode": code.code,
        }
        try:
            response = await self._request("POST", "/nt/app.php", data=payload)
            response_data = response.json()
            
            if not response_data.get("success"):
                raise AuthException(response_data.get("error", "Unknown error"))
            
            self.session.update({
                "profile": response_data,
                "cookies": dict(response.cookies)
            })
            await self.save_session()
            return True, "Authorization successful"
            
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON response: {text}", text=response.text)
            return False, "Invalid server response"

    async def send_like(self, username: str) -> bool:
        """Send like with optimized response handling"""
        try:
            response = await self._request(
                "GET", 
                f"/nt/app.php?i=showinterest&up={username}&sip=1"
            )
            return "interest sent!" in response.text.lower()
        except httpx.HTTPError as e:
            logger.error("Like failed for {user}: {error}", user=username, error=str(e))
            return False

    async def get_users_for_interaction(self, gender="f") -> List[UserPlay]:
        """Fetch users with pagination support"""
        params = {
            "searchparams[gender]": gender,
            "searchparams[online]": "on",
            "searchparams[photo]": "on",
            "type": "browseAll",
            "i": "browsenew"
        }
        try:
            response = await self._request(
                "GET", 
                "/nt/app.php?" + urlencode(params, doseq=True)
            )
            return [UserPlay(**user) for user in response.json().get("results", [])]
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("Invalid user data format: {error}", error=str(e))
            return []

    async def get_profile(self) -> UserProfile:
        """Fetch profile with cached results"""
        try:
            response = await self._request("GET", "/nt/app.php?i=editmyprofilenew")
            return UserProfile(**response.json())
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("Invalid profile data: {error}", error=str(e))
            raise AuthException("Invalid profile response") from e

    async def close(self):
        """Cleanup resources"""
        if self._client:
            await self._client.aclose()
        if self._redis_pool:
            await self._redis_pool.close()