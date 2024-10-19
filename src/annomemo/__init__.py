import os
import click
import mimetypes
import json
import aiohttp
import base64

from loguru import logger
import litellm
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters as telefilters,
    CallbackContext,
)

TRANSCRIBE_PROMPT = """Transcribe the hand written notes in the attached image and present them as markdown inside a fence like so

```markdown
<Content>
```

If any words or letters are unclear just ask the user for clarification.
"""


def validate_ai_environment():
    logger.info("Checking model params")
    model_name = os.getenv("MODEL", "openai/gpt-4o")
    result = litellm.validate_environment(model_name)

    if not result["keys_in_environment"]:
        logger.error(f"Failed to validate model environment with MODEL={model_name}")
        if len(result["missing_keys"]) > 0:
            logger.error(
                f"Missing the following environment variables: {result['missing_keys']}"
            )
        exit(-1)

    if not litellm.supports_vision(model="gpt-4-vision-preview"):
        logger.error(f"Vision not supported by {model_name}")

    logger.info("AI API connection is ready")


class ImageProcessException(Exception):
    pass


async def process_image(image_url: str):
    """Process the given image and respond with the result from the model"""

    mtype, _ = mimetypes.guess_type(image_url)
    if mtype is None:
        raise ImageProcessException(f"Failed to detect mime type for file {mtype}")

    async with aiohttp.ClientSession() as client:
        img_response = await client.get(image_url)
        bytearray = await img_response.read()
        b64img = base64.b64encode(bytearray).decode("utf-8")

    logger.info(f"Sending image with mimetype {mtype}")

    message = {
        "role": "user",
        "content": [
            {"type": "text", "text": TRANSCRIBE_PROMPT},
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mtype};base64,{b64img}"},
            },
        ],
    }

    litellm.api_base = os.environ.get("OPENAI_API_BASE")

    response = await litellm.acompletion(
        model=os.getenv("MODEL", "openai/gpt-4o"),
        messages=[message],
    )

    return response.choices[0].message["content"]


async def handle_telegram_message(update: Update, context: CallbackContext):
    logger.info(f"{update}")

    if len(update.message.photo) < 1:
        await update.message.reply_text("🤖 Please send me photos to process 📷")
        return

    # find the biggest image and keep it as we want to do OCR on it
    file = max(update.message.photo, key=lambda x: x["file_size"])


    await update.message.reply_chat_action(action=ChatAction.TYPING)

    logger.info(f"Processing file {file['file_id']}")
    photo = await context.bot.get_file(file['file_id'])

    try:
        resp = await process_image(photo.file_path)
        await update.message.reply_text(resp, reply_to_message_id=update.message.id)
    except Exception as e:
        logger.error(f"{e}")
        await update.message.reply_text("🤖 " + str(e))


@click.command()
def main():
    logger.info("Starting AnnoMemo...")
    load_dotenv()
    validate_ai_environment()

    bot = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()

    bot.add_handler(MessageHandler(telefilters.ALL, handle_telegram_message))

    bot.run_polling()


if __name__ == "__main__":
    main()
