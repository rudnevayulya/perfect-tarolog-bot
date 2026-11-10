# Perfect Tarolog Bot

Telegram tarot bot starter in Russian. It includes a 78-card deck, one-card / three-card / seven-card horseshoe spreads, random upright or reversed orientation, and interactive card selection.

## Deploy to Google Cloud Run

This project uses Telegram webhooks (not long-polling) and includes a Dockerfile for Cloud Run.

### Before you start

- A Google account
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- A Google Cloud project with billing enabled

Cloud Run has a monthly free usage tier, but Google requires a billing account. Usage beyond the free tier, and some related services used during builds, can incur charges. Review [Cloud Run pricing](https://cloud.google.com/run/pricing) and configure a budget alert before deploying.

### Deploy in two stages

1. Open Google Cloud Console and select or create a project.
2. Open Cloud Run and choose to deploy a service from a GitHub repository / source repository.
3. Connect this repository: `rudnevayulya/perfect-tarolog-bot`.
4. Select the `main` branch and the repository's `Dockerfile`.
5. Set the service to allow unauthenticated/public access. Telegram must be able to send webhook requests to it.
6. Configure these environment variables / secrets:
   - `TELEGRAM_BOT_TOKEN`: the token from @BotFather. Store it as a secret; never commit it to GitHub.
   - `WEBHOOK_SECRET`: a random string of 32-64 letters and numbers. Do not use spaces.
   - Do not set `WEBHOOK_URL` on the first deployment.
7. Deploy. Copy the HTTPS service URL shown by Cloud Run.
8. Edit the service and add `WEBHOOK_URL` with that exact URL, without a trailing slash, for example `https://your-service-xxxxx-ew.a.run.app`.
9. Save / deploy the new revision. The bot will register its Telegram webhook at `WEBHOOK_URL/telegram`.
10. Open your bot in Telegram and send `/start`.

### Important

- Keep `TELEGRAM_BOT_TOKEN` and `WEBHOOK_SECRET` private.
- The repository may be public, so never put secrets in source files or commits.
- Do not enable a minimum instance count for the first test; it can create ongoing charges.
- The first deployment may take several minutes.
- The bot currently stores active readings in memory. If Cloud Run scales the instance to zero or restarts it, an in-progress reading can be lost.
- This starter version uses built-in reflection prompts; it does not yet call a paid AI service.

Tarot content is for reflection and entertainment, not factual prediction or professional advice.
