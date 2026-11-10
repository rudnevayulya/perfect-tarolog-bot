# Perfect Tarolog Bot

Telegram tarot bot starter in Russian. It includes a 78-card deck, one-card / three-card / seven-card horseshoe spreads, random upright or reversed orientation, and interactive card selection.

## Requirements

- Python 3.10+
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

## Run locally or on a host

1. Install dependencies:

   `pip install -r requirements.txt`

2. Set the token as an environment variable named `TELEGRAM_BOT_TOKEN`.
   - macOS/Linux: `export TELEGRAM_BOT_TOKEN="your-token"`
   - Windows PowerShell: `$env:TELEGRAM_BOT_TOKEN="your-token"`
   - On a hosting platform, add it in the platform's Secrets / Environment Variables settings.

3. Start the bot:

   `python bot.py`

4. Open your Telegram bot and send `/start`.

## Commands

- `/start` — open the spread menu
- `/cancel` — cancel the current spread

## Security

**Never commit your Telegram token to this repository or send it in chat.** The repository is public. Keep the token only in the hosting provider's encrypted Secrets / environment variables. If a token is ever exposed, revoke it with @BotFather and generate a new one.

## Current limitations

- No paid AI integration is configured.
- Interpretations are concise built-in reflection prompts, not generated personalized readings.
- Active spread state is kept in memory and is lost if the process restarts.
- This is a starter version; test it before inviting other users.

Tarot content is for reflection and entertainment. It cannot verify health, safety, whereabouts, or predict another person's fate.
