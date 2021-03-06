# Copyright (c) <2018>, Ethan <ipvedaily@gmail.com>
# Copyright (c) <2018>, Eef Top <eeftop1994@gmail.com>
# Copyright (c) <2018>, L eon <https://github.com/LeonSkills>
# All rights reserved.
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
import json
import os
import random
import sys
import time
import datetime
import discord

from discord.ext.commands import Bot, CommandNotFound, DisabledCommand, CheckFailure, MissingRequiredArgument, \
    BadArgument, TooManyArguments, UserInputError, CommandOnCooldown
from discord.ext import commands
from discord import Game
from Settings import Settings
from analyzer import Analyzer

VERSION = "1.7.1\n" \
          "Last Updated: 10/24/2018"
BOT_PREFIX = ("~", "?")
client = Bot(command_prefix=BOT_PREFIX)
analyzer = Analyzer(client)
auth_file = 'auth.json'
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
settings = Settings()
start_time = time.time()


class WrongChannelError(commands.CommandError):
    pass


@client.command(name='stats', help="", brief="Shows stats of top 10 scouts.", description="",
                aliases=['highscores'], pass_context=True)
@commands.cooldown(rate=1, per=120, type=commands.BucketType.channel)
@commands.has_any_role(*settings.ranks)
async def stats(ctx, arg="scouts"):
    channel = ctx.message.channel
    if channel.name in settings.channels:
        await analyzer.stats(channel, arg)


@client.command(name='fullstats', help="", brief="Shows stats of all scouts.", description="",
                aliases=['fullhighsores'], pass_context=True)
@commands.cooldown(rate=1, per=600, type=commands.BucketType.channel)
@commands.has_any_role(*settings.ranks)
async def fullstats(ctx, arg="scouts"):
    channel = ctx.message.channel
    if channel.name in settings.channels:
        await analyzer.fullstats(channel, arg)


@client.command(name='save', help="", brief="", description="", hidden=True, pass_context=True)
@commands.has_any_role(*settings.ranks)
async def save(ctx):
    await analyzer.save()
    await client.send_message(ctx.message.channel, "Saving finished.")


@client.command(name='uptime', help="", brief="Displays how long bot has been live.", description="", pass_context=True)
async def uptime(ctx):
    current_time = time.time()
    difference = int(round(current_time - start_time))
    text = str(datetime.timedelta(seconds=difference))
    embed = discord.Embed(colour=ctx.message.author.top_role.colour)
    embed.add_field(name="Bot Uptime:", value=text)
    try:
        await client.send_message(ctx.message.channel, embed=embed)
    except discord.HTTPException:
        await client.send_message(ctx.message.channel, "Current uptime: " + text)


@client.command(name='ban', help="", brief="Adds username for staff to ban.", description="", pass_context=True)
@commands.has_role("Staff")
async def ban(ctx, *names):
    name = ' '.join(names)
    channel = ctx.message.channel
    if channel.name == "ranks-and-bans":
        await analyzer.addban(name, ctx.message.channel)
    else:
        raise WrongChannelError


@client.command(name='rank', help="", brief="Adds username for staff to rank.", description="", pass_context=True)
@commands.has_role("Staff")
async def rank(ctx, *names):
    name = ' '.join(names)
    channel = ctx.message.channel
    if channel.name == "ranks-and-bans":
        await analyzer.addrank(name, ctx.message.channel)
    else:
        raise WrongChannelError


@client.command(name='removeban', help="", brief="Removes bans from list.", description="",
                aliases=['unban', 'deban'], pass_context=True)
@commands.has_role("Staff")
async def removeban(ctx, *names):
    name = ' '.join(names)
    channel = ctx.message.channel
    if channel.name == "ranks-and-bans":
        await analyzer.removeban(name, ctx.message.channel)
    else:
        raise WrongChannelError


@client.command(name='removerank', help="", brief="Removes rank from list.", description="", aliases=['unrank', 'derank'], pass_context=True)
@commands.has_role("Staff")
async def removerank(ctx, *names):
    name = ' '.join(names)
    channel = ctx.message.channel
    if channel.name == "ranks-and-bans":
        await analyzer.removerank(name, ctx.message.channel)
    else:
        raise WrongChannelError


@client.command(name='clearbans', help="", brief="Clears ban list.", description="", pass_context=True)
@commands.has_role("Staff")
async def clearbans(ctx):
    channel = ctx.message.channel
    if channel.name == "ranks-and-bans":
        await analyzer.clearbans(ctx.message.channel)
    else:
        raise WrongChannelError


@client.command(name='clearranks', help="", brief="Clears rank list.", description="", pass_context=True)
@commands.has_role("Staff")
async def clearranks(ctx):
    channel = ctx.message.channel
    if channel.name == "ranks-and-bans":
        await analyzer.clearranks(ctx.message.channel)
    else:
        raise WrongChannelError


@client.command(name='showbans', help="", brief="Shows just ban list.", description="",
                aliases=['bans'], pass_context=True)
@commands.has_role("Staff")
async def showbans(ctx):
    channel = ctx.message.channel
    if channel.name == "ranks-and-bans":
        await analyzer.showbans(channel)
    else:
        raise WrongChannelError


@client.command(name='showranks', help="", brief="Shows just rank list.", description="", pass_context=True)
@commands.has_role("Staff")
async def showranks(ctx):
    channel = ctx.message.channel
    if channel.name == "ranks-and-bans":
        await analyzer.showranks(channel)
    else:
        raise WrongChannelError


@client.command(name='show', help="", brief="Shows rank and ban list.", description="", pass_context=True)
@commands.has_role("Staff")
async def show(ctx):
    channel = ctx.message.channel
    if channel.name == "ranks-and-bans":
        await analyzer.showranksandbans(channel)
    else:
        raise WrongChannelError


@client.command(name='lookup', help="Can tag someone to lookup specific users stats.", brief="", description="",
                aliases=['personal'], pass_context=True)
async def lookup(ctx, *id):
    channel = ctx.message.channel
    if channel.name in settings.channels:
        await analyzer.lookup(channel, id)


@client.command(name='slap', help="", brief="", description="", pass_context=True)
async def slap(ctx, id):
    channel = ctx.message.channel
    await client.send_message(channel, f"{ctx.message.author.name} slapped {id}‽")


@client.command(name='resetscout', help="Deletes your assigned scout list.", aliases=['rs'], brief="", description="",
                pass_context=True)
async def resetscout(ctx):
    channel = ctx.message.channel
    if channel.name in settings.channels:
        author = ctx.message.author
        username = author.name
        await analyzer.reset_scout(channel, author.id, username)


@client.command(name='mute', help="Mutes the bot from pming you.", brief="", description="",
                aliases=['zipit', 'stfu'], pass_context=True)
async def mute(ctx):
    channel = ctx.message.channel
    if channel.name in settings.channels:
        author = ctx.message.author
        username = author.name
        await analyzer.set_mute(channel, author.id, username, 1)


@client.command(name='unmute', help="Unmutes the bot so you can be messaged.", brief="", description="",
                aliases=['unzipit'], pass_context=True)
async def unmute(ctx):
    channel = ctx.message.channel
    if channel.name in settings.channels:
        author = ctx.message.author
        username = author.name
        await analyzer.set_mute(channel, author.id, username, 0)


@client.command(name='updatescoutstats', help="fixes issues with unset scout fields", brief="", description="",
                pass_context=True)
@commands.has_any_role(*settings.ranks)
async def updatescoutstats(ctx):
    channel = ctx.message.channel
    if channel.name in settings.channels:
        await analyzer.update_scout_stats()


@client.command(name='scout', help='Gives you a list of best worlds to scout.', brief="", description="",
                aliases=['request', 'req'], pass_context=True)
async def scout(ctx, *args):
    channel = ctx.message.channel
    if len(args) != 0:
        num_worlds = int(args[0])
        if num_worlds < 3:
            await client.send_message(channel, "You must request at least 3 worlds.")
            return
    if channel.name in settings.channels:
        username = ctx.message.author.name
        author = ctx.message.author
        await analyzer.get_scout_info(channel, author, username, args)


@client.command(name='relay', help="Brings worldlist to newest message.", brief="", description="",
                aliases=['worlds', 'list', 'calls'], pass_context=True)
async def relay(ctx):
    channel = ctx.message.channel
    if channel.name in settings.channels:
        await analyzer.relay(channel)


@client.command(name='worldlist', help="Shows all scouted worlds.", brief="", description="", pass_context=True)
@commands.cooldown(rate=1, per=180, type=commands.BucketType.channel)
async def worldlist(ctx):
    channel = ctx.message.channel
    if channel.name in settings.channels:
        await client.send_message(channel, analyzer.get_table(False))


@client.command(name='deleteworlddata',
                help='Refreshes current world data. If you are found abusing, you will be removed.'
                     ' Works only with Staff rank.', brief="", description="",
                aliases=['deleteeverythingrightmeow'], pass_context=True)
@commands.has_any_role(*settings.ranks)
async def deleteworlddata(ctx):
    channel = ctx.message.channel
    possible_replies = [
        'abolished',
        'obliterated',
        'annihilated',
        'eliminated',
        'removed',
        'cleared',
        'erased',
        'emptied',
        'nulled',
        'terminated',
        'eradicated',
        'negated',
        'undone',
        'wiped',
        'destroyed'
    ]
    if channel.name in settings.channels:
        await analyzer.reset()
        response = f"World data has been {random.choice(possible_replies)}."
        await client.send_message(channel, response)
        await analyzer.relay(channel)


@client.command(name='stop', help='Stops bot vigorously. Works only with Staff rank.', brief="", description="",
                pass_context=True)
@commands.has_role("Staff")
async def stop(ctx):
    print("Attempting to stop")
    await analyzer.saves()
    await analyzer.savew()
    await client.send_message(ctx.message.channel, "Stopping....")
    await client.logout()
    exit(0)


@client.command(name='restart', help='Restarts bot.', brief="", description="",
                pass_context=True)
@commands.has_role("Staff")
async def restart(ctx):
    await analyzer.saves()
    await analyzer.savew()
    await client.send_message(ctx.message.channel, "Restarting....")
    analyzer.restart_program()


@client.command(name='ping', help='Checks bots ping.', brief="", description="", pass_context=True)
async def ping(ctx):
    embed = discord.Embed(colour=ctx.message.author.top_role.colour)
    embed.add_field(name="Pong! :ping_pong:", value="...")
    before = time.monotonic()
    message = await client.send_message(ctx.message.channel, embed=embed)
    pingms = round((time.monotonic() - before) * 1000)
    embed.set_field_at(0, name="Pong! :ping_pong:", value=f"Pong: {pingms}ms")
    await client.edit_message(message, embed=embed)


@client.command(name='commands', help='Lists commands for calling/scouting.', brief="Lists commands", description="",
                pass_context=True)
async def commands():
    await client.say("To report on a world: `w[#] [number of active plinths]`.\n"
                     "Example: `w59 4` or `14 2`\n\n"
                     "To call a core: `w[#] [core name]`.\n"
                     "Example: `w12 cres` or `42 seren`.\n"
                     "Aliases for core names are shown here: `['cres', 'c', 'sword', 'edicts', 'e', 'sw', 'juna', 'j', "
                     "'seren', 'se', 'aagi', 'a']`.\n\n"
                     "To delete a world: `w[#] [0, d, dead, or gone]`.\n"
                     "Example: `w103 d` or `56 0`\n\n"
                     "To get a list of worlds to scout: `?scout [optional amount]`. \n"
                     "Example: `?scout` for a default of 10 worlds or `?scout 5` for 5 worlds.\n"
                     "If you dont want/can to complete the list use `?resetscout`.\n"
                     "If you can't do a world just report it to be 0, or ask someone else to do it for you\n"
                     "To disable the bot pming your list of worlds: `?mute`\n"
                     "To enable the bot pming your list of worlds: `?unmute`\n\n"
                     "You can report the worlds in pm to the bot if you want.\n\n"
                     "The next column will display a max of 10 worlds sorted by active plints.\n"
                     "To get the full list: `?worldlist`")


@client.command(name='info', help='Lists FC info.', brief="", description="",
                pass_context=True)
async def info(ctx):
    channel = ctx.message.channel
    if channel.name in settings.channels:
        await client.say("Look in: #fc-info for information.")
    else:
        pass


@client.command(name='version', help='Lists current bot version.', brief="", description="",
                pass_context=True)
async def version():
    await client.say("Current bot version: " + VERSION)


@client.command(name='ranks', help='Lists current FC ranks.', brief="", description="",
                pass_context=True)
async def ranks(ctx):
    channel = ctx.message.channel
    if channel.name in settings.channels:
        rankies = {"Blue Raivyn\n",
                   "Sscared\n",
                   "Bomy\n",
                   "Insulate\n",
                   "DTP\n",
                   "Pur\n",
                   "Z oD\n",
                   "Legend-ary\n",
                   "HuntrMetroid\n",
                   "Unicorn Snot\n",
                   "Leighrose\n",
                   "Eef Top\n",
                   "Luna Kitten\n",
                   "L eon\n"
                   "Metal-chan"
                   "xElissa"
                   "Karios"
                   "Velvet Tiger"}
        rankies = sorted(rankies)
        ranks_str = "★WealthRS★\n"
        for name in rankies:
            ranks_str += str(name)
        await client.say("```" + ranks_str + "```")
    else:
        pass


@client.event
async def on_ready():
    await client.change_presence(game=Game(name="Hall of Memories"))
    await analyzer.loadworlds()
    await analyzer.loadscouts()
    print('Connected!')
    print('Username: ' + client.user.name)
    print('ID: ' + client.user.id)
    server = [x for x in client.servers if x.name == settings.servers[0]][0]
    bot_channel = [x for x in server.channels if x.name == settings.bot_only_channel][0]
    await client.send_message(bot_channel, "Nobody fear, the bot is here!")


mainMessage = None


@client.event
async def on_message(message):
    # Check if it's not our own message, don't want infinite loops
    if message.author == client.user:
        return

    print(f"Received message {message.content} in channel {message.channel} from {message.author.name}"
          .translate(non_bmp_map))

    # Check if we are in the right channel

    if str(message.channel.type) == "private":
        await analyzer.analyze_call(message)
        return

    if message.channel.name not in settings.channels:
        return

    if message.server.name not in settings.servers:
        return

    message.content = message.content.lower()
    await client.process_commands(message)

    # Analyse the message
    await analyzer.analyze_call(message)


@client.event
async def on_command_error(error, ctx):
    print(f"Rip, error {ctx}, {error}")
    errors = {
        CommandNotFound: 'Command not found.',
        DisabledCommand: 'Command has been disabled.',
        CheckFailure: 'Missing required permissions to issue command.',
        MissingRequiredArgument: 'Command missing required arguments.',
        BadArgument: 'Failed parsing given arguments.',
        TooManyArguments: 'Too many arguments given for command.',
        UserInputError: 'User input error.',
        CommandOnCooldown: 'Command is on cooldown. Please wait a moment before trying again.',
        WrongChannelError: 'Command issued in a channel that isn\'t allowed.'
    }
    for type, text in errors.items():
        if isinstance(error, type):
            return await client.send_message(ctx.message.channel, "Command error: " + errors[type])


if not os.path.exists(auth_file):
    print("no auth json found, please create one")

with open(auth_file) as f:
    auth_data = json.load(f)

client.run(os.environ['BOTTOKEN'])
# client.run(auth_data['token3'])
