import discord
from discord.ext import tasks
from mcstatus import JavaServer
import os
from keep_alive import keep_alive

class Bot:
    def __init__(self):
        self.client = discord.Client(intents=discord.Intents.default())
        self.mc_server = MCServer()
        self.channel_id = os.getenv("channel")
        self.channel = None
        self.message = None

    def run_bot(self):
        TOKEN = os.getenv("token")

        @self.client.event
        async def on_ready():
            print("Ready")
            if self.channel == None:
                self.channel = self.client.get_channel(int(self.channel_id))
            self.update_status.start()

        self.client.run(token=TOKEN)

    @tasks.loop(seconds=3)
    async def update_status(self):
        if self.channel:
            print("Inside Channel")
            try:
                print("Checking Message History")
                async for message in self.channel.history(limit=1):
                    if message.author == self.client.user:
                        await self.send_embed(self.channel, self.mc_server, message)
                    else:
                        await self.send_embed(self.channel, self.mc_server)
            except StopAsyncIteration:
                await self.send_embed(self.channel)
            except Exception as e:
                print(f"An error occurred in the update_status task: {e}")
        

    async def send_embed(self, channel, mc_server, existing_embed=None):
        address = mc_server.get_address()
        version = mc_server.get_version()
        platform = mc_server.get_platform()
        player_count = mc_server.get_player_count()
        players = mc_server.get_players()
        ping = mc_server.get_ping()

        embed = discord.Embed(
            title="Minecraft Server",
            description="KANGKONG CHIPS ORIGINAL BY JOSH MOJICA",
            color=discord.Color.green())

        embed.add_field(name="Address", value=address, inline=False)
        embed.add_field(name="Online Players", value=players, inline=False)

        embed.add_field(name="Platform", value=platform, inline=True)
        embed.add_field(name="Version", value=version, inline=True)
        embed.add_field(name="Players", value=player_count, inline=True)
        embed.set_footer(text=f"Server Ping: {ping} • ACQ")

        if existing_embed:
            print(existing_embed.embeds[0].fields[1].value)
            if existing_embed.embeds[0].fields[1].value != players:
                print("Updating Message")
                await existing_embed.edit(embed=embed)
                return
            else:
                print("No Update")
        else:
            print("Sending New Message")
            await channel.send(embed=embed)
            return 


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
    
    def get_ping(self):
        return f"{int(self.SERVER.ping())} ms"


# keep_alive()
bot = Bot()
bot.run_bot()
