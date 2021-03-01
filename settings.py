"""Settings, such as IDs used to communicate with the wowaudit API."""

import os
from dotenv import load_dotenv

load_dotenv()


def get_env(name):
    """Try to get the env var, exit if not found."""
    value = os.getenv(name)
    if value is None:
        print(
            'Error: The environment variable ' + name +
            ' is undefined, exiting application.')
        exit()
    return value


# All below constants must be defined in .env
DISCORD_TOKEN = get_env('DISCORD_TOKEN')
DISCORD_GUILD_NAME = get_env('DISCORD_GUILD_NAME')
REMINDER_CHANNEL = get_env('REMINDER_CHANNEL')
WOWAUDIT_GUILD_ID = get_env('WOWAUDIT_GUILD_ID')
WOWAUDIT_TEAM_ID = get_env('WOWAUDIT_TEAM_ID')
WOWAUDIT_COOKIE = get_env('WOWAUDIT_COOKIE')
DISCORD_BOSS = get_env('DISCORD_BOSS')


# Number of hours before each raid to post the reminder"
REMINDER_HOURS = 48

# Map character names to discord tag, in order to ping the stragglers
DISC_MAP = {
    'Mcpickle': 'McPickle#6783',
    'Welfir': 'KasperRT#3925',
    'Boltar': 'Boltar[The Bois]#1918',
    'Hisui': 'Hisui#2710',
    'Narla': 'Rich#9973',
    'Maluminse': 'Pip#3143',
    'Ceia': 'Gevelten#0329',
}
