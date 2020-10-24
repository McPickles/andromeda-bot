"""Entry point of the app."""
import wowaudit_helper
import datetime
import settings
import asyncio

import discord


class AndromedaClient(discord.Client):
    """Subclassing discord client to implement custom functionality."""

    def __init__(self):
        """Init subclass."""
        super().__init__()
        self.loop.create_task(self.reminder_scheduler())

    async def get_stragglers(self, raid_id):
        """Get a list of unsigned people."""
        raid = await wowaudit_helper.get_raid(raid_id)
        signups = raid['signups']
        stragglers = []
        for signup in signups:
            if signup['status'] == 'absent' and signup['comment'] is None:
                stragglers.append(signup['character']['name'])

        return stragglers

    async def _get_reminder_time(self, raid):
        """Get the exact time to remind for a raid."""
        raid_date = datetime.datetime.strptime(raid['date'], '%Y-%m-%d')
        raid_start_time = datetime.datetime.strptime(
            raid['start_time'], '%H:%M')
        full_start_date = datetime.datetime(
            raid_date.year,
            raid_date.month,
            raid_date.day,
            raid_start_time.hour,
            raid_start_time.minute
        )
        reminder_time = full_start_date - datetime.timedelta(
            hours=settings.REMINDER_HOURS)
        return reminder_time

    async def _get_next_raid(self):
        """Get the next raid to be reminded."""
        raids = await wowaudit_helper.get_raids()
        now = datetime.datetime.now()
        for r in raids:
            # When should this raid be reminded?
            reminder_target = await self._get_reminder_time(r)
            # Not interested if this is in the past
            if reminder_target < now:
                continue
            else:
                return r

        return None

    async def reminder_scheduler(self):
        """Loop that calls the remind function before every raid."""
        await self.wait_until_ready()
        # First raid we search to find
        next_raid = await self._get_next_raid()
        while not self.is_closed():
            # If there are no raids we wait for 10 mins and check again
            if next_raid is None:
                await asyncio.sleep(600)
                next_raid = await self._get_next_raid()
                # Reloop to check again for NoneType
                continue

            reminder_target = await self._get_reminder_time(next_raid)
            # Get the number of seconds until we should remind 'em
            delay = (reminder_target - datetime.datetime.now()).total_seconds()
            await asyncio.sleep(delay)

            await self.remind(next_raid['date'])

            # We can get the next raid directly from wowaudit
            next_raid = await wowaudit_helper.get_raid(next_raid['nextRaid'])

    async def remind(self, raid_id):
        """Post the reminder by pinging all non-signers."""
        stragglers = await self.get_stragglers(raid_id)
        straggler_string = ''
        for s in stragglers:
            disc_name = s
            # Add the ping if we found them in the discord map
            if s in settings.DISC_MAP:
                disc_name = '@' + settings.DISC_MAP[s]
            straggler_string += disc_name + ', '

        straggler_string += 'Please sign up for upcoming raid!'
        await self.reminder_channel.send(straggler_string)

    async def on_ready(self):
        """On bot connection."""
        for guild in client.guilds:
            if guild.name == settings.DISCORD_GUILD_NAME:
                for channel in guild.text_channels:
                    if channel.name == settings.REMINDER_CHANNEL:
                        self.reminder_channel = channel
                        break
                break
        print(
            f'Connected to: {guild.name}'
        )


client = AndromedaClient()
client.run(settings.DISCORD_TOKEN)
