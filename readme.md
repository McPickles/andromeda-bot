# Andromeda Bot

The andromeda bot is a discord bot named after the Andromeda Guild on Stormrage-EU. Currently its sole purpose is to annoy raiders who haven't signed up for raids by pinging them in discord repeatedly. The bot requires that the guild uses wowaudit.com to handle raid signups.

## Dependencies

- `pip install discord.py`
- `pip install aiohttp`
- `pip install python-dotenv`

## Env variables

```
DISCORD_TOKEN=DISCORDBOT_TOKEN
DISCORD_GUILD_NAME=DISCORD SERVER NAME
REMINDER_CHANNEL=DISCORD CHANNEL NAME FOR REMINDERS
WOWAUDIT_GUILD_ID=15072
WOWAUDIT_TEAM_ID=16446
WOWAUDIT_COOKIE=BLATANT COPY OF COOKIES FOR WOWAUDIT
DISCORD_BOSS=Something#Number
```
