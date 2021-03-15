"""Helper functions to communicate with the wowaudit API."""

import aiohttp

def base_url(settings):
    return f'https://wowaudit.com/api/guilds/' \
            f'{settings.WOWAUDIT_GUILD_ID}/teams/{settings.WOWAUDIT_TEAM_ID}'


async def get_dashboard(settings):
    """Get the dashboard of the raid team.

    Returns:
        Dict: JSON as pulled from wowaudit
    """
    req_str = f'{base_url(settings)}/dashboard_data'

    async with aiohttp.ClientSession() as session:
        async with session.get(
            req_str,
            headers={'cookie': settings.WOWAUDIT_COOKIE}
        ) as resp:
            json = await resp.json()
            if "error" in json:
                raise Exception("Unauthorized")
            return json


async def get_raids(settings):
    """Get all raids for this raidteam.

    Returns:
        Dict: JSON from API containing all raids.
    """
    req_str = f'{base_url(settings)}/raids'
    async with aiohttp.ClientSession() as session:
        async with session.get(
            req_str,
            headers={'cookie': settings.WOWAUDIT_COOKIE},
        ) as resp:
            json = await resp.json()
            if "error" in json:
                raise Exception("Unauthorized")
            return json

async def get_raid(settings, raid_id):
    """Get the raid object from the API.

    Args:
        raid_id (String): The date of the raid, effectively the ID

    Returns:
        Dict: The raid object
    """
    req_str = f'{base_url(settings)}/raids/{raid_id}'

    async with aiohttp.ClientSession() as session:
        async with session.get(
            req_str,
            headers={'cookie': settings.WOWAUDIT_COOKIE}
        ) as resp:
            json = await resp.json()
            if "error" in json:
                raise Exception("Unauthorized")
            return json


def get_raid_link(settings, raid_id):
    return f'https://wowaudit.com/{settings.REGION}/{settings.REALM_NAME}/{settings.GUILD_NAME}/mythic/raids/{raid_id}'
