import discord
from mcstatus import JavaServer
import asyncio
import os
from keep_alive import keep_alive

class Bot:
    def run_bot(self):
        intents = discord.Intents.default()
        intents.message_content = True
        client = discord.Client(intents=intents)
        TOKEN = os.getenv("token")
        @client.event
        async def on_ready():
            print("Ready")
            channel_id = os.getenv("channel")
            channel = client.get_channel(int(channel_id))

            if channel:
                mc_server = MCServer()
                while True:
                    try:
                        async for message in channel.history(limit=1):
                            if message.author == client.user:
                                await self.send_embed(channel, mc_server, message)
                            else:
                                await self.send_embed(channel, mc_server)
                    except StopAsyncIteration:
                        # Handle the case when there is no message in the channel history
                        await self.send_embed(channel, mc_server)

                    await asyncio.sleep(1)

        client.run(token=TOKEN)

    async def send_embed(self, channel, mc_server, existing_embed=None):
        address = mc_server.get_address()
        version = mc_server.get_version()
        platform = mc_server.get_platform()
        player_count = mc_server.get_player_count()
        players = mc_server.get_players()

        embed = discord.Embed(
            title="Minecraft Server",
            description="KANGKONG CHIPS ORIGINAL BY JOSH MOICA",
            color=discord.Color.green())

        embed.add_field(name="Address", value=address, inline=False)
        embed.add_field(name="Online Players", value=players, inline=False)

        embed.add_field(name="Platform", value=platform, inline=True)
        embed.add_field(name="Version", value=version, inline=True)
        embed.add_field(name="Players", value=player_count, inline=True)
        embed.set_footer(text="made by Alven")

        if existing_embed:
            print("Updating Message")
            if existing_embed.embeds[0].fields[1].value != players:
                await existing_embed.edit(embed=embed)
                return existing_embed
        else:
            print("Sending New Message")
            return await channel.send(embed=embed)


class MCServer:

    def __init__(self):
        self.address = os.getenv("address")
        self.SERVER = JavaServer.lookup(self.address)

    def get_address(self):
        return self.address

    def get_players(self):
        status = self.SERVER.status()

        if status.players.online != 0:
            player_list = [player.name for player in status.players.sample]
            sorted_player_list = sorted(player_list)
            return '\n'.join(sorted_player_list)
        
        return ""

    def get_version(self):
        status = self.SERVER.status()
        return status.version.name

    def get_player_count(self):
        status = self.SERVER.status()
        return f"{status.players.online}/{status.players.max}"

    def get_platform(self):
        status = self.SERVER.status()
        platform = "Bedrock" if status.motd.bedrock else "Java"
        return platform


keep_alive()
bot = Bot()
bot.run_bot()