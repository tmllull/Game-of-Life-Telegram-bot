import datetime
import os

import telegram
import utils.logger as logger
from clients.ai_controller import AIController
from database.database import SessionLocal
from telegram import Bot, Update
from utils.config import Config

config = Config()
ai_controller = AIController()
db = SessionLocal()


class MyUtils:
    """_summary_"""

    def __init__(self):
        pass
        self.bot = Bot(config.TELEGRAM_TOKEN)
        # if config.AI_SERVICE == "openai":
        #     self._ai_service = open_ai
        # elif config.AI_SERVICE == "azure":
        #     self._ai_service = azure_openai
        # else:
        #     self._ai_service = None
        # self.chat_id = self.TELEGRAM_CHAT_ID

    def check_valid_chat(self, update: Update) -> bool:
        try:
            username = update.message.from_user.username
            user_id = update.message.from_user.id
            chat_id = update.message.chat_id
            if chat_id < 0:
                if chat_id != int(config.TELEGRAM_CHAT_ID):
                    return False
                return True
            return False
        except Exception as e:
            logger.info("Error checking valid chat: " + str(e))

    async def send_message(self, msg=None, pre_prompt=None, prompt=None):
        if pre_prompt and prompt is not None and ai_controller.has_service:
            try:
                logger.info("Generating text by AI...")
                msg = await ai_controller.generate_text(pre_prompt, prompt)
                logger.info("Generated text by AI: " + str(msg))
            except Exception as e:
                logger.info("Error generating text by AI: " + str(e))
                # msg = msg
        # else:
        #     logger.info("Sending default message...")

        async with self.bot:
            msg = self.format_text_for_md2(msg)
            await self.bot.send_message(
                chat_id=config.TELEGRAM_CHAT_ID,
                text=msg,
                parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
            )

    def format_text_for_md2(self, text):
        text = (
            text.replace(".", "\.")
            .replace("!", "\!")
            .replace("-", "\-")
            .replace("+", "\+")
            .replace("=", "\=")
            .replace("(", "\(")
            .replace(")", "\)")
            .replace("[", "\[")
            .replace("]", "\]")
        )
        return text

    def get_date(self) -> datetime.date:
        return datetime.datetime.now().date()
