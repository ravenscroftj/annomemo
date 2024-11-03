import os
import click


from loguru import logger

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters as telefilters,
    CallbackContext,
)

from typing import Sequence

from .ocr import get_image_processor, ImageProcessor
from .plugins import load_plugins, BotPlugin

TRANSCRIBE_PROMPT = """Transcribe the hand written notes in the attached image and present them as markdown inside a fence like so

```markdown
<Content>
```

If any words or letters are unclear, denote them  with a '?<word>?'. For example if you were not sure whether a word is blow or blew you would transcribe it as '?blow?'
"""


class ImageProcessException(Exception):
    pass


class BotMessageHandler(MessageHandler):

    def __init__(self, image_processor: ImageProcessor, plugins: Sequence[BotPlugin] = []):
        super().__init__(telefilters.ALL, self.handle_telegram_message)
        self._image_processor = image_processor
        self.plugins = plugins

    async def handle_telegram_message(self, update: Update, context: CallbackContext):
        """Handle response to message"""
        logger.info(f"{update}")

        if update.message is None:
            logger.warning(f"No message received {update}")
            return

        try:
            telegram_whitelist = [
                int(id.strip()) for id in os.getenv("TELEGRAM_CHAT_IDS", "").split(",")
            ]
        except:
            telegram_whitelist = []

        if update.message.chat.id not in telegram_whitelist:
            logger.info("Telegram chat id not whitelisted")
            await update.message.reply_text(
                f"🤖 Sorry, I'm not allowed to process your photos. Ask admin to add chat id {
                    update.message.chat.id} to the whitelist"
            )
            return

        if len(update.message.photo) < 1:
            await update.message.reply_text("🤖 Please send me photos to process 📷")
            return

        # find the biggest image and keep it as we want to do OCR on it
        file = max(update.message.photo, key=lambda x: x["file_size"])

        await update.message.reply_chat_action(action=ChatAction.TYPING)

        logger.info(f"Processing file {file['file_id']}")
        photo = await context.bot.get_file(file["file_id"])

        try:
            resp = await self._image_processor.process_image(photo.file_path)
            await update.message.reply_text(resp, reply_to_message_id=update.message.id)
        except Exception as e:

            logger.opt(exception=e).error(
                f"Failed to process message",
            )
            await update.message.reply_text("🤖 " + str(e))


@click.command()
def main():
    logger.info("Starting AnnoMemo...")
    load_dotenv()

    if os.getenv("TELEGRAM_TOKEN") is None:
        logger.error("No telegram token provided via TELEGRAM_TOKEN env var")
        exit(-1)

    processor = get_image_processor()

    logger.info("Validating image processing approach")
    processor.validate()

    plugins = load_plugins()

    bot = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()

    bot.add_handler(BotMessageHandler(processor, plugins))

    bot.run_polling()


if __name__ == "__main__":
    main()
