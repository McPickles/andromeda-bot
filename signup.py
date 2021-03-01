"""Entry point of the app."""
import wowaudit_helper
import datetime
import settings
import aiohttp
import asyncio

import discord


class AndromedaClient(discord.Client):
    """Subclassing discord client to implement custom functionality."""

    def __init__(self):
        """Init subclass."""
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.loop.create_task(self.reminder_scheduler())

    async def get_stragglers(self, raid_id):
        """Get a list of unsigned people."""
        raid = await wowaudit_helper.get_raid(settings, raid_id)
        signups = raid['signups']
        stragglers = []
        for signup in signups:
            # Signups default to late if not set
            if (signup['status'] == 'absent' or signup['status'] == 'late') and signup['comment'] is None:
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
        raids = await wowaudit_helper.get_raids(settings)
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
        try:

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

                await self.remind(next_raid['date'], next_raid['id'])
                # We can get the next raid directly from wowaudit
                next_raid = await self._get_next_raid()

        # This should probably be better implemented, seeing this catches all crashes
        except TypeError as e:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            await self.bossboi.send(f'Errored `reminder_scheduler`, cookie might be dead. Reply to me with the cookie _only_. I will await 1 min, until I check again.\n```\nError: {message}\n```')
        except aiohttp.ClientConnectorError as e:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            await self.bossboi.send(f'Errored `reminder_scheduler`, cannot connect to wowaudit. Trying again in 1 min.\n```\nError: {message}\n```')
        except Exception as e:
            # General error-handling for sending all errors to bossboi
            template = "An exception of type {0} occurred. Retrying stuff in 1 min. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            await self.bossboi.send(f'```\n{message}\n```')
        finally:
            await asyncio.sleep(60)
            self.loop.create_task(self.reminder_scheduler())

    def tag_user(self, tag):
        user = self.get_member_by_tag(tag)
        if not user:
            return tag
        return "<@!" + str(user.id) + ">"

    async def on_message(self, message):
        global settings
        # Check if alive, easily
        if(message.content == "ping"):
            await message.channel.send('pong')
        # Only allow messaging from bossboi for updating cookie
        elif(message.author.name + "#" + message.author.discriminator == settings.DISCORD_BOSS):
            settings.WOWAUDIT_COOKIE = message.content
            try:
                # Test if new cookie works
                await wowaudit_helper.get_raids(settings)
                await self.bossboi.send(f'Updated cookie to `{settings.WOWAUDIT_COOKIE}`')
            except Exception as e:
                await self.bossboi.send(f'Cookie value doesnt work.\n```\n{e}\n```')


    async def remind(self, raid_date, raid_id):
        """Post the reminder by pinging all non-signers."""
        stragglers = await self.get_stragglers(raid_date)
        straggler_string = ''
        for s in stragglers:
            disc_name = s
            # Add the ping if we found them in the discord map
            if s in settings.DISC_MAP:
                # Add character-name as well, just in case
                disc_name = f'{self.tag_user(settings.DISC_MAP[s])} ({s})'
                await self.send_individual_message(settings.DISC_MAP[s], raid_id)
            straggler_string += disc_name + ', '

        straggler_string += 'please sign up for upcoming raid!'
        await self.reminder_channel.send(straggler_string)

    # Send message to individual member, for even more following
    async def send_individual_message(self, tag, raid_id):
        user = self.get_member_by_tag(tag)
        if not user:
            return
        await user.send(f'I cannot see you have signed up for the raid.\nPlease update your signup on https://wowaudit.com/eu/stormrage/andromeda/main/raids/{str(raid_id)}, or notify one of the officers :slight_smile:')

    def get_member_by_tag(self, tag):
        return next((x for x in self.guild.members if x.name + "#" + x.discriminator == tag), None)

    async def on_ready(self):
        """On bot connection."""
        for guild in client.guilds:
            if guild.name == settings.DISCORD_GUILD_NAME:
                for channel in guild.text_channels:
                    if channel.name == settings.REMINDER_CHANNEL:
                        self.guild = guild
                        self.reminder_channel = channel
                        self.bossboi = self.get_member_by_tag(settings.DISCORD_BOSS)
                        break
                break
        print(
            f'Connected to: {self.guild.name}'
        )

client = AndromedaClient()
client.run(settings.DISCORD_TOKEN)
