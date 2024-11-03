# AnnoMemo

A simple utility that OCRs your handwritten and printed notes using OpenAI compatible VLMs.

## Installation

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/).

## Configuration

Set up a `.env` file based on the `.env.example` file. The variables needed are as follows:

- `MODEL` - The model to use for OCRing, this should be a valid LiteLLM Model ID with the provider prefix e.g. `openai/gpt-4o`
- `OPENAI_API_KEY` - Your OpenAI API key. If you are using a non-OAI service or a proxy (like litellm), then pass your litellm token here.
- `OPENAI_API_BASE` - (optional) if you are using an openai compatible service like litellm, pass the URL here e.g. `https://litellm.example.com`
- `TELEGRAM_CHAT_IDS` - comma-separated list of chat ids that are allowed to interact with your bot. To get this ID, start the bot with this variable empty and it will respond with the chat ID. Then add your chat ID and restart the app.
- `TELEGRAM_TOKEN` - your bot's telegram token. Use [the official telegram docs](https://core.telegram.org/bots/tutorial#obtain-your-bot-token) to obtain your token.
- `MEMOS_URL` - (optional), enable [memos](https://www.usememos.com/) integration by passing the URL for your self-hosted memos server.
- `MEMOS_TOKEN` - (optional), if memos is enabled, pass an authentication token to allow the bot to add memos.
- `MEMOS_TAG` - (optional) if memos is enabled and you want to tag your notes with a specific tag, pass it here.
