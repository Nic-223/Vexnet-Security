import discord
import datetime
import json
import requests
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
from discord.ext import commands
import re

## Settings ## 

bot = commands.Bot(intents=discord.Intents.all() , command_prefix= "!" , description='Vexnet Security')

CONFIG_LOG = 1057323213350252625


with open("protectionlist.json", "r") as f:
    protection_list = json.load(f)

online_protection = protection_list["Online Realtime Protection"]
offline_protection = protection_list["Offline Realtime Protection"]
security_mode = protection_list["Security Mode"]

bot.remove_command('help')

@bot.command(name="help")
async def _help(ctx):
    embed = discord.Embed(title="Help", color=0x1C0639)
    embed.add_field(name="**!checklist**", value="Checks the status of the phishing links database.", inline=False)
    embed.add_field(name="**!protection**", value="Can turn on and off the real-time protections.", inline=False)
    embed.add_field(name="**!scan <channel>**", value="Scans a Discord channel for names/words/phrases that match the phishing links database.", inline=False)
    embed.add_field(name="**Usage**", value="Type the name of the command to run it.", inline=False)
    embed.set_footer(text="For more information, type !help <command>")

    embed.add_field(name="**!checklist**", value="This command checks the status of the phishing links database. If the connection is down, consider turning on offline-based real-time protection to keep your server safe from phishing attacks.", inline=False)
    embed.add_field(name="**Usage**", value="Type !checklist to run the command.", inline=False)

    embed.add_field(name="**!protection**", value="This command can turn on and off the real-time protections. Available options are: full, online, local, security, and off. Use the command with an option to turn on that protection, and without an option to turn off all protections.", inline=False)
    embed.add_field(name="**Usage**", value="Type !protection <option> to turn on a protection, or !protection to turn off all protections.", inline=False)

    embed.add_field(name="**!scan <channel>**", value="This command scans a Discord channel for URLs that match the phishing links database. The channel to scan must be mentioned after the command.", inline=False)
    embed.add_field(name="**Usage**", value="Type !scan <channel> to run the command.", inline=False)

    await ctx.send(embed=embed)




@bot.command()
async def protection(ctx, option: str):
    with open("protectionlist.json", "r") as f:
        protection_list = json.load(f)

    if option == "full":
        global online_protection
        global offline_protection
        global security_mode
        online_protection = True
        offline_protection = True
        security_mode = True
        protection_list["Online Realtime Protection"] = "true"
        protection_list["Offline Realtime Protection"] = "true"
        protection_list["Security Mode"] = "true"
        await ctx.send("Full protection settings turned on.")
    elif option == "online":
     
        online_protection = True
        protection_list["Online Realtime Protection"] = "true"
        await ctx.send("Online protection setting turned on.")
    elif option == "local":
        
        offline_protection = True
        protection_list["Offline Realtime Protection"] = "true"
        await ctx.send("Offline protection setting turned on.")
    elif option == "security":
 
        security_mode = True
        protection_list["Security Mode"] = "true"
        await ctx.send("Security Mode protection setting turned on.")
    elif option == "off":

        online_protection = False
        offline_protection = False
        security_mode = False
        protection_list["Online Realtime Protection"] = "false"
        protection_list["Offline Realtime Protection"] = "false"
        protection_list["Security Mode"] = "false"
        await ctx.send("Protection settings turned off.")
    else:
        await ctx.send("Invalid option. Use `full` [turns on everything] or `online/local/security` [Turns on specific things] or `off` [Turns of everything].")

    with open("protectionlist.json", "w") as f:
        json.dump(protection_list, f)

    embed=discord.Embed(title="Protection Settings Changed", description=f"\n**Changed by:** {ctx.author}\n**Changed at:** {datetime.datetime.now()}\n**Changed to:** {option}", color=0x1C0639)
    await bot.get_channel(CONFIG_LOG).send(embed=embed)

@protection.error
async def protection_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        
        embed = discord.Embed(title="Protection Settings", color=0x1C0639)
        embed.add_field(name="**Available Protection Settings**", value="Use the following commands to turn on each protection setting:", inline=False)
        embed.add_field(name="`!protection full`", value="Turns on all protection settings", inline=False)
        embed.add_field(name="`!protection online`", value="Turns on online real-time protection", inline=False)
        embed.add_field(name="`!protection local`", value="Turns on offline real-time protection", inline=False)
        embed.add_field(name="`!protection security`", value="Turns on security mode", inline=False)
        embed.add_field(name="`!protection off`", value="Turns off all protection settings", inline=False)
        embed.set_footer(text="For more information, type !help")
        await ctx.send(embed=embed)



@bot.command()
async def checklist(ctx):
    re = requests.get("https://raw.githubusercontent.com/nikolaischunk/discord-phishing-links/main/txt/domain-list.txt")
    embed = discord.Embed(title="Domain List Check", color=0x1C0639)

    if re.status_code == 200:
        embed.add_field(name="**Status**", value="✅ Connection successful", inline=False)
        embed.add_field(name="**Connection**", value="The domain list is currently up and accessible.", inline=False)
    else:
        embed.add_field(name="**Status**", value="❌ Connection failed", inline=False)
        embed.add_field(name="**Connection**", value="The domain list is currently unavailable. Consider turning on offline-based real-time protection.", inline=False)
    embed.add_field(name="**Usage**", value="This command checks the connection to the domain list and reports its status.", inline=False)
    embed.set_footer(text="For more information, type !help")
    await ctx.send(embed=embed)


@bot.command(name="scan")
async def scan_channel(ctx, channel: discord.TextChannel):
    url = "https://raw.githubusercontent.com/nikolaischunk/discord-phishing-links/main/txt/domain-list.txt"

    response = requests.get(url)
    content = response.content.decode()


    words = re.findall(r'\w+', content)
    match_count = 0

    async for message in channel.history(limit=1000):
        message_words = re.findall(r'\w+', message.content.lower())
        for word in message_words:
            if word in words:
                match_count += 1

    total_words_scanned = len(words) * 1000
    match_percent = (match_count / total_words_scanned) * 100

    embed = discord.Embed(title="URL Scan Results", color=0x1C0639)
    embed.add_field(name="Channel Scanned", value=channel.mention, inline=False)
    embed.add_field(name="Total Words Scanned", value=f"{total_words_scanned:,}", inline=False)
    embed.add_field(name="Matches Found", value=f"{match_count:,} ({match_percent:.1f}% of total words scanned)", inline=False)
    embed.set_footer(text="Scan performed on " + datetime.datetime.now().strftime("%m/%d/%Y %I:%M %p"))

    await ctx.send(embed=embed)

@scan_channel.error
async def scan_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="Error", description="Please provide a valid channel to scan.", color=0xFF0000)
        await ctx.send(embed=embed)



@bot.event
async def on_message(message):
    if online_protection == "true":
        if message.author.bot:
            return
        response = requests.get("https://raw.githubusercontent.com/nikolaischunk/discord-phishing-links/main/txt/domain-list.txt")
        list = response.text.split("\n")
        list = [x for x in list if x]
    
        if any(word in message.content.lower() for word in list):
            
            general_channel = bot.get_channel(CONFIG_LOG) # Your security log channel
            embed=discord.Embed(title="Phising Link", description=f"\n**Correctness value:** [99% / Online]\n**System Used:** [Online Realtime Protection]\n**Users Message:** {message.content.lower()}\n**Message Owner:** {message.author}", color=0xff0000)
            list = response.text.split("\n")
            embed.description += f"\n**Number of blocked domains:** {len(list)}"
            embed.description += f"\n**Channel:** {message.channel.name}"
            embed.description += f"\n**Timestamp:** {message.created_at.strftime('%m/%d/%Y %H:%M:%S')}"

            if message.attachments:
                attachment_urls = [attachment.url for attachment in message.attachments]
                embed.description += f"\n**Attachments:** {attachment_urls}"

            if message.reactions:
                reaction_emojis = [reaction.emoji for reaction in message.reactions]
                embed.description += f"\n**Reactions:** {reaction_emojis}"

            
            embed.description += f"\n**Join date:** {message.author.joined_at.strftime('%m/%d/%Y %H:%M:%S')}"

            if message.author.roles:
                role_names = [role.name for role in message.author.roles]
                embed.description += f"\n**Roles:** {role_names}"

            if message.author.activity:
                embed.description += f"\n**Users Activity:** {message.author.activity.name}"

            embed.set_author(name="Vexnet Security", url="https://discord.com", icon_url="https://media.discordapp.net/attachments/1056604890840956968/1056607196902862899/Neues_Projekt_4.png")
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1056604890840956968/1056607196902862899/Neues_Projekt_4.png")
            embed.add_field(name="Timestamp", value=message.created_at.strftime("%m/%d/%Y %H:%M:%S"), inline=False)
            await general_channel.send(embed=embed)
            await message.delete()
        else:
            await bot.process_commands(message)
    elif offline_protection == "true":
            if message.author.bot:
                return
            with open("banned_words.txt") as f:
                banned_words = f.read().splitlines()
            if any(word in message.content.lower() for word in banned_words):
                general_channel = bot.get_channel(CONFIG_LOG) # Your security log channel
                embed = discord.Embed(title="Phishing Link", description=f"\n**System Used:** [Offline Realtime Protection]\n**Users Message:** {message.content.lower()}\n**Message Owner:** {message.author}", color=0xff0000)
                embed.description += f"\n**Number of blocked words:** {len(banned_words)}"
                embed.description += f"\n**Channel:** {message.channel.name}"
                embed.description += f"\n**Timestamp:** {message.created_at.strftime('%m/%d/%Y %H:%M:%S')}"

                if message.attachments:
                    attachment_urls = [attachment.url for attachment in message.attachments]
                    embed.description += f"\n**Attachments:** {attachment_urls}"

                if message.reactions:
                    reaction_emojis = [reaction.emoji for reaction in message.reactions]
                    embed.description += f"\n**Reactions:** {reaction_emojis}"

                embed.description += f"\n**Join date:** {message.author.joined_at.strftime('%m/%d/%Y %H:%M:%S')}"

                if message.author.roles:
                    role_names = [role.name for role in message.author.roles]
                    embed.description += f"\n**Roles:** {role_names}"


                if message.author.activity:
                    embed.description += f"\n**Users Activity:** {message.author.activity.name}"

                embed.set_author(name="Vexnet Security", url="https://discord.com", icon_url="https://media.discordapp.net/attachments/1056604890840956968/1056607196902862899/Neues_Projekt_4.png")
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/1056604890840956968/1056607196902862899/Neues_Projekt_4.png")
                embed.add_field(name="Timestamp", value=message.created_at.strftime("%m/%d/%Y %H:%M:%S"), inline=False)
                await general_channel.send(embed=embed)
                await message.delete()
            else:
                await bot.process_commands(message)
    else: 
        return

      

bot.run("")