"""Helper functions to communicate with the wowaudit API."""

import aiohttp
import settings

BASE_URL = f'https://wowaudit.com/api/guilds/' \
            f'{settings.WOWAUDIT_GUILD_ID}/teams/{settings.WOWAUDIT_TEAM_ID}'

COOKIE_HEADER = {'cookie': settings.WOWAUDIT_COOKIE}


async def get_dashboard():
    """Get the dashboard of the raid team.

    Returns:
        Dict: JSON as pulled from wowaudit
    """
    req_str = f'{BASE_URL}/dashboard_data'

    async with aiohttp.ClientSession() as session:
        async with session.get(
            req_str,
            headers=COOKIE_HEADER
        ) as resp:
            return await resp.json()


async def get_raids():
    """Get all raids for this raidteam.

    Returns:
        Dict: JSON from API containing all raids.
    """
    req_str = f'{BASE_URL}/raids'
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            req_str,
            headers=COOKIE_HEADER,
        ) as resp:
            return await resp.json()


async def get_raid(raid_id):
    """Get the raid object from the API.

    Args:
        raid_id (String): The date of the raid, effectively the ID

    Returns:
        Dict: The raid object
    """
    req_str = f'{BASE_URL}/raids/{raid_id}'

    async with aiohttp.ClientSession() as session:
        async with session.get(
            req_str,
            headers=COOKIE_HEADER
        ) as resp:
            return await resp.json()
