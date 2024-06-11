import discord
from discord.ext import tasks
from mcstatus import JavaServer
import os
from dotenv import load_dotenv
from keep_alive import keep_alive

class Bot:
    def __init__(self):
        self.client = discord.Client(intents=discord.Intents.default())
        self.mc_server = MCServer()
        self.channel_id = os.getenv('channel')
        self.channel = self.client.get_channel(int(self.channel_id))

    def run_bot(self):
        TOKEN = os.getenv('token')

        @self.client.event
        async def on_ready():
            print("Ready")
            self.channel = self.client.get_channel(int(self.channel_id))
            self.update_status.start()

        self.client.run(token=TOKEN)

    @tasks.loop(seconds=3)
    async def update_status(self):
        if self.channel:
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
        embed = discord.Embed(
            title="Minecraft Server [Online]",
            description="ChennyCakes Server",
            color=discord.Color.green())
        
        version = mc_server.get_version()

        if version == "Unknown":
            print("Server Offline")
            embed = discord.Embed(
            title="Minecraf Server [Offline]",
            description="KANGKONG CHIPS ORIGINAL BY JOSH MOJICA",
            color=discord.Color.red())
            if existing_embed:
                await existing_embed.edit(embed=embed)
                return
            else:
                print("Sending New Message")
                await channel.send(embed=embed)
                return 
        print("Server Online")
        address = mc_server.get_address()
        platform = mc_server.get_platform()
        player_count = mc_server.get_player_count()
        players = mc_server.get_players()
        ping = mc_server.get_ping()

        embed.add_field(name="Address", value=address, inline=False)
        embed.add_field(name="Online Players", value=players, inline=False)

        embed.add_field(name="Platform", value=platform, inline=True)
        embed.add_field(name="Version", value=version, inline=True)
        embed.add_field(name="Players", value=player_count, inline=True)
        embed.set_footer(text=f"Server Ping: {ping} • ACQ")

        if existing_embed:
            existing_title = existing_embed.embeds[0].title
            print(existing_title)
            if existing_title == "Minecraft Server [Offline]":
                print("Updating Message")
                await existing_embed.edit(embed=embed)
            else:
                if existing_embed.embeds[0].fields[1].value != players:
                    print("Updating Message")
                    await existing_embed.edit(embed=embed)
                else:
                    print("No Update")
        else:
            print("Sending New Message")
            await channel.send(embed=embed)
            return 


class MCServer:
    def __init__(self):
        self.address = os.getenv('address')
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
        try:
            status = self.SERVER.status()
            self.is_online = True
            return status.version.name
        except Exception:
            self.is_online = False
            return "Unknown"

    def get_player_count(self):
        status = self.SERVER.status()
        return f"{status.players.online}/{status.players.max}"

    def get_platform(self):
        status = self.SERVER.status()
        platform = "Bedrock" if status.motd.bedrock else "Java"
        return platform
    
    def get_ping(self):
        return f"{int(self.SERVER.ping())} ms"
    
    def get_server_status(self):
        return self.SERVER.status()


load_dotenv()
keep_alive()
bot = Bot()
bot.run_bot()
