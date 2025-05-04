from typing import Awaitable, Callable, List
from datetime import datetime
import random
import asyncio
from loguru import logger
from redis import asyncio as aioredis
from app.match.schemas.match import MatchCreate
from bot.schemas.bot import UpdateGender
from match.dependencies import get_match_crud
from thaifriendly.database.crud import ThaifrinedlyBotCRUD
from thaifriendly.database.models.bot import ThaifriendlyBot
from thaifriendly.infrastructure.client import ThaiFriendlyClient
from thaifriendly.infrastructure.exc import AuthException
from thaifriendly.infrastructure.schemas import UserMatch, UserMessage, UserPlay
from base.infrastructure.automation import Automation

class ThaiFriendlyAutomation(ThaiFriendlyClient, Automation):
    def __init__(self, bot_id: int, api_key: str, asisstant_id: str, redis: aioredis.Redis, callback: Callable[[int], Awaitable[None]]):
        ThaiFriendlyClient.__init__(self, bot_id)
        Automation.__init__(self, bot_id, api_key, asisstant_id, redis, callback)
        self._running = False
        self.bot_crud = ThaifrinedlyBotCRUD()
        self.tasks = [self.run_messaging_automation, self.run_likes_automation]
        
    async def pre_start(self):
        try:
            if not await self.load_session():
                raise AuthException
            profile = await self.get_profile()
            await self.bot_crud.update(
                item_id=self.bot_id,
                data=UpdateGender(
                    gender=profile.gender
                ),
            )
        except Exception:
            raise

    async def run_likes_automation(self):
        self._running = True
        bot: ThaifriendlyBot = await self.bot_crud.get(self.bot_id)
        try:
            while self._running:
                try:
                    batch_size = random.randint(25, 50)
                    cooldown = random.randint(1800, 3600)

                    users = await self.get_users_for_interaction(
                        gender="f" if bot.lookingfor == "Woman" else "m"
                    )
                    filtered = self._filter_users(users)

                    if not filtered:
                        await asyncio.sleep(cooldown)
                        continue

                    like_targets = random.sample(
                        filtered, min(batch_size, len(filtered))
                    )

                    successful_likes = 0
                    for user in like_targets:
                        if not self._running:
                            break

                        try:
                            if await self.send_like(user.name):
                                self.last_activity = datetime.now()
                                successful_likes += 1
                            await asyncio.sleep(random.uniform(2, 3))
                        except AuthException as e:
                            raise   
                        except Exception as e:
                            logger.error(
                                f"Error liking {user.name}: {str(e)}", exc_info=True
                            )

                    logger.success(
                        f"Batch completed. Successful likes: {successful_likes}/{len(like_targets)}"
                    )

                except Exception as batch_error:
                    logger.error(
                        f"Batch processing error: {str(batch_error)}", exc_info=True
                    )
                await asyncio.sleep(cooldown)
        except AuthException as e:
            logger.critical(f"CRITICAL AUTH ERROR FOR BOT {self.bot_id}")
            raise
        except asyncio.CancelledError:
            logger.warning("Likes automation was cancelled")
        except Exception as global_error:
            logger.critical(
                f"Critical error in likes automation: {str(global_error)}",
                exc_info=True,
            )
        finally:
            self._running = False
            logger.success("Likes automation stopped")

    async def run_messaging_automation(self, check_interval: int = 0):
        self._running = True

        try:
            while self._running:
                try:
                    conversations = await self.get_matches()
                    await self.save_matches(conversations)
                except AuthException as e:
                    raise
                except Exception as e:
                    logger.error(
                        f"Failed to check matches for bot {self.bot_id}: {str(e)}"
                    )
                    await asyncio.sleep(60)
                    continue

                if conversations:
                    try:
                        await self._process_matches(conversations)
                        logger.success(
                            f"Processed {len(conversations)} matches for bot {self.bot_id}"
                        )
                    except AuthException as e:
                        raise 
                    except Exception as e:
                        logger.error(
                            f"Failed to process matches for bot {self.bot_id}: {str(e)}"
                        )
                await asyncio.sleep(check_interval)
        except AuthException as e:
            logger.critical(f"CRITICAL AUTH ERROR FOR BOT {self.bot_id}")
            raise
        except asyncio.CancelledError:
            logger.warning("Messaging automation cancelled")
        except Exception as fatal_e:
            logger.critical(f"Fatal error: {str(fatal_e)}")
        finally:
            self._running = False
            logger.success("Messaging automation stopped")

    def _filter_users(self, users: List[UserPlay]) -> List[UserPlay]:
        return [u for u in users if self._is_valid_user(u)]

    def _is_valid_user(self, user: UserPlay) -> bool:
        return user.name not in self.session["liked_users"]

    async def save_matches(self, matches: List[UserMatch]):
        match_manager = await get_match_crud()
        try:
            bot: ThaifriendlyBot = await self.bot_crud.get(self.bot_id)
            if not bot:
                logger.error(f"Bot {self.bot_id} not found in database")
                return
        except Exception as e:
            logger.critical(f"Failed to fetch bot {self.bot_id}: {str(e)}")
            return
        for match in matches:
            try:
                try:
                    if await match_manager.get_bot_match(match_id=match.username):
                        continue
                except Exception as e:
                    logger.error(f"Match check failed for {match.username}: {str(e)}")
                    continue
                try:
                    await match_manager.add(
                        data=MatchCreate(
                            bot_id=self.bot_id,
                            match_id=match.username,
                            name=match.username,
                            gender=match.gender,
                            city=match.city,
                            age=match.age,
                            time=match.time,
                        )
                    )
                except Exception as e:
                    logger.error(f"Failed to add match {match.username}: {str(e)}")
                    continue
            except Exception as e:
                raise

    async def _process_matches(self, matches: List[UserMatch]):
        try:
            matches = sorted(matches, key=lambda x: int(x.time), reverse=True)
            logger.debug(
                f"Starting processing {len(matches)} matches for bot {self.bot_id}"
            )

            try:
                bot: ThaifriendlyBot = await self.bot_crud.get(self.bot_id)
                if not bot:
                    logger.error(f"Bot {self.bot_id} not found in database")
                    return
            except Exception as e:
                logger.critical(f"Failed to fetch bot {self.bot_id}: {str(e)}")
                return

            for match in matches:
                try:
                    try:
                        conversation = await self.get_conversations(match.username)
                        if not conversation:
                            logger.warning(
                                f"No conversation found for {match.username}"
                            )
                            continue
                    except Exception as e:
                        logger.error(
                            f"Conversation fetch failed for {match.username}: {str(e)}"
                        )
                        continue

                    response = None
                    try:
                        if conversation[-1].them:
                            response = await self._generate_response(
                                conversation,
                                match.username,
                                instructions=bot.instructions,
                                link=bot.link,
                            )
                            logger.debug(f"Generated response: {response}")
                    except Exception as e:
                        logger.error(
                            f"Response generation failed for {match.username}: {str(e)}"
                        )
                        continue

                    try:
                        if response:
                            ok, api_response, timeout = await self.send_message(
                                match.username, response
                            )

                            if ok:
                                logger.success(f"Message sent to {match.username}")
                                self.last_activity = datetime.now()
                            else:
                                logger.error(
                                    f"Message failed for {match.username}: {api_response}"
                                )
                            await asyncio.sleep(timeout)
                    except AuthException as e:
                        raise e
                    except IndexError:
                        logger.warning(f"Empty conversation for {match.username}")
                    except Exception as e:
                        logger.error(
                            f"Message sending failed for {match.username}: {str(e)}"
                        )
                except AuthException as e:
                    raise e
                except Exception as e:
                    logger.error(
                        f"Critical error processing match {match.username}: {str(e)}"
                    )
                    continue
        except AuthException as e:
            raise
        except Exception as e:
            logger.critical(f"Global processing error for bot {self.bot_id}: {str(e)}")
            raise

    async def stop(self):
        self._running = False
        await self.save_session()

    async def _generate_response(
        self,
        messages: List[UserMessage],
        username: str,
        instructions: str,
        link: str,
    ) -> str:
        try:
            thread_id = await self.openai_handler.get_thread(self.bot_id, username)
            if not thread_id:
                thread_id = await self.openai_handler.create_thread()
                await self.openai_handler.save_thread(self.bot_id, username, thread_id)

            for msg in messages:
                role = "assistant" if msg.them == 0 else "user"
                await self.openai_handler.add_message(thread_id, msg.text, role)
            additional_instuctions = (
                str(instructions or "") + "\n" + f"Telegram Link - {link}"
            )
            await self.openai_handler.run_assistant(
                self.assistant_id, thread_id, additional_instuctions
            )
            oai_messages = await self.openai_handler.get_messages(thread_id)
            assistant_messages = [
                msg for msg in oai_messages if msg["role"] == "assistant"
            ]

            await self.openai_handler.save_thread(self.bot_id, username, thread_id)
            return assistant_messages[-1]["content"] if assistant_messages else None

        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            await self.openai_handler.delete_thread(self.bot_id, username)
            return "Sorry, i am bussy now"
