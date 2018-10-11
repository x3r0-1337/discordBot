import discord
import asyncio
from datetime import date
from discord.ext.commands import Bot
import anilistParser
import re


def initialize():
    try:
        with open('config.txt', 'x') as config:
            token = input('Enter bot token: ')
            config.write('token = ' + token + '\n')
            identifier = input('Enter bot identifier: ')
            config.write('identifier = ' + identifier + '\n')
            config.write('channel_list' + '\n')
            channellist = []
        print('config.txt created and initialized successfully')
        return token, identifier, channellist
    except FileExistsError:
        with open('config.txt', 'r') as config:
            line = config.readlines()
            channellist = []
            flag = 0
            for i in range(0, len(line)):
                if flag == 1:
                    channellist.append(line[i].strip())
                    continue
                if 'token' in line[i].split():
                    token = str(list(line[i].strip().split()).pop())
                elif 'identifier' in line[i].split():
                    identifier = str(list(line[i].strip().split()).pop())
                elif ('channel_list' in line[i].split()) and ((len(line) - 1) > i):
                    flag = 1
        print('Configuration initialized from config.txt')
        return token, identifier, channellist


def updatechannellist(channellist):
    with open('config.txt', 'r') as config:
        lines = config.readlines()
        for j, k in enumerate(lines):
            if 'channel_list' in k:
                i = j+1
    with open('config.txt', 'w') as config:
        config.writelines(lines[:i])
        for chnlst in channellist:
            config.writelines(str(chnlst) + '\n')
    return


def retrieve(animu: anilistParser.anime):
    if animu.status == 'Airing':
        myembed = discord.Embed(title=animu.title, url=animu.url,
                                colour=0x00ff00)
    elif animu.status == 'Not Yet Aired':
        myembed = discord.Embed(title=animu.title, url=animu.url,
                                colour=0xff0000)
    elif animu.status == 'Finished Airing':
        myembed = discord.Embed(title=animu.title, url=animu.url,
                                colour=0x0000ff)
    else:
        myembed = discord.Embed(title=animu.title, url=animu.url)
    myembed.set_thumbnail(url=animu.image)
    if animu.synonyms == 'None':
        myembed.add_field(name='Synonyms', value='None', inline=False)
    else:
        myembed.add_field(name='Synonyms', value=', '.join(animu.synonyms),
                          inline=False)
    myembed.add_field(name='Format', value=animu.frmt)
    dt = ((animu.styear) if animu.stmonth == 'Unknown' else (
        animu.stmonth + ' ' + animu.styear))
    myembed.add_field(name=('Airing in' if animu.status != 'Finished Airing'
                            else 'Aired on'), value=dt)
    if animu.status == 'Finished Airing' and animu.episodes != 'Unknown':
        myembed.add_field(name='Episodes', value=animu.episodes)
    myembed.add_field(name='Source', value=animu.source)
    if animu.genres == 'Unknown':
        myembed.add_field(name='Genre(s)', value='Unknown',
                          inline=False)
    else:
        myembed.add_field(name='Genre(s)', value=', '.join(animu.genres),
                          inline=False)
    if len(animu.description) > 1024:
        myembed.add_field(name='Description',
                          value=animu.description[:1024], inline=False)
        myembed.add_field(name='Description(cont.)',
                          value=animu.description[1024:], inline=False)
    else:
        myembed.add_field(name='Description', value=animu.description,
                          inline=False)
    if animu.styear == 'Unknown' or animu.season == 'Unknown':
        sdt = animu.season
    else:
        sdt = animu.season + ' ' + animu.styear
    if animu.status == "Airing":
        statair = (" - " + animu.currep + " / " + animu.episodes)
    else:
        statair = ''
    myembed.set_footer(text="Season: " + sdt + " | " + animu.status + statair)
    return myembed


def anichoice(alist):
    if len(alist) == 0:
        embed = discord.Embed(title='No Search Results')
    else:
        embed = discord.Embed(title='Search Results')
        for i, j in enumerate(alist):
            embed.add_field(name=('`' + str(i+1) + '.` ' + j.title), value='\u200b', inline=False)
        embed.set_footer(text='Type a number to view more information or `cancel` to cancel search.')
    return embed


def anidb(id):
    try:
        with open('animudb.txt', 'x') as db:
            db.write(str(id) + '\n')
    except FileExistsError:
        with open('animudb.txt', 'r') as db:
            adb = db.readlines()
            for line in adb:
                if str(id) in line:
                    return 1
        with open('animudb.txt', 'a') as db:
            db.write(str(id) + '\n')
        return 0


async def findMessage(channel, reqdtitle):
    async for message in channel.history(limit=300):
        if message.author == bot.user:
            if message.embeds[0].title == reqdtitle:
                return message
            else:
                requestedMessage = 'Null'
        else:
            requestedMessage = 'Null'
    return requestedMessage


print(discord.__version__)
token, identifier, channellist = initialize()
bot = Bot(identifier, description='')


@bot.event
async def on_ready():
    print('Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    print('\nPress Ctrl + C to exit')


@bot.command(pass_context=True)
async def say(ctx, *, message: str):
    if str(ctx.message.channel.id) in channellist:
        await ctx.send(message)


@bot.command(pass_context=True)
async def delete(ctx, num: int):
    if ('administrator', True) in list(ctx.message.author.guild_permissions):
        await ctx.channel.purge(limit=num)
    else:
        await ctx.send('You do not have the required permissions to invoke ' +
                       'this command', delete_after=5.0)


@bot.command(pass_context=True)
async def xkcd(ctx, *num):
    if str(ctx.message.channel.id) in channellist:
        if len(num) == 0:
            await ctx.send('https://xkcd.com')
        else:
            await ctx.send('https://xkcd.com/' + str(num[0]))


@bot.group(pass_context=True)
async def channel(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid command.')
        await asyncio.sleep(1)
        await ctx.channel.purge(limit=2)
    elif ('administrator', False) in list(
          ctx.message.author.guild_permissions):
        await ctx.send('You do not have the required permissions to invoke ' +
                       'this command.')
        await asyncio.sleep(1)
        await ctx.channel.purge(limit=2)


@channel.command(pass_context=True)
async def invoke(ctx):
    channellist.append(str(ctx.message.channel.id))
    updatechannellist(channellist)
    await ctx.send('This channel is now monitored')
    await asyncio.sleep(1)
    await ctx.channel.purge(limit=2)


@channel.command(pass_context=True)
async def leave(ctx):
    if str(ctx.message.channel.id) in channellist:
        channellist.remove(str(ctx.message.channel.id))
        updatechannellist(channellist)
        await ctx.send('This channel is no longer monitored')
        await asyncio.sleep(1)
        await ctx.channel.purge(limit=2)


@bot.group(pass_context=True)
async def anime(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid command.')
        await asyncio.sleep(1)
        await ctx.channel.purge(limit=2)
    elif ('administrator', False) in list(
          ctx.message.author.guild_permissions):
        await ctx.send('You do not have the required permissions to invoke ' +
                       'this command.')
        await asyncio.sleep(1)
        await ctx.channel.purge(limit=2)


@anime.command(pass_context=True)
async def airing(ctx):
    channel = ctx.message.channel
    if str(channel.id) in channellist:
        await ctx.message.channel.trigger_typing()
        year = int(date.today().year)
        month = int(date.today().month)
        if int(date.today().month) == 1:
            year -= 1
            month = 12
        else:
            month -= 1
        airanime = await anilistParser.query('airing')
        for a in airanime:
            if (a.status == 'Finished Airing') and ((int(a.styear) < year) or (a.stmonthint + (int(a.episodes) if a.episodes != 'Unknown' else 0)//4 < month)) :
                continue
            existence = anidb(a.id)
            if existence == 1:
                if a.status == 'Finished Airing':
                    continue
                embedmessage = await findMessage(channel, a.title)
                reg = re.compile(r'\d+|Unknown+')
                if embedmessage != 'Null':
                    if reg.findall(str(embedmessage.embeds[0].footer.text))[1] != a.currep:
                        myembed = retrieve(a)
                        await embedmessage.edit(embed=myembed)
                    else:
                        continue
                else:
                    continue
            else:
                await ctx.message.channel.trigger_typing()
                myembed = retrieve(a)
                await ctx.send(embed=myembed)


@anime.command(pass_context=True)
async def search(ctx, *searchstr):


    def check(n):
        return ((n.content.isdigit() or n.content=='cancel') and n.author == ctx.message.author)
    

    if str(ctx.message.channel.id) in channellist:
            await ctx.message.channel.trigger_typing()
            searchres = await anilistParser.query('search', ' '.join(searchstr))
            embedchoice = anichoice(searchres)
            msg = await ctx.send(embed=embedchoice)
            if embedchoice.title == 'No Search Results':
                await asyncio.sleep(5)
                await msg.delete()
            else:
                try:
                    res = await bot.wait_for('message', check=check, timeout=300.0)
                except asyncio.TimeoutError:
                    await msg.edit(content='Search Timed Out, Try again.', embed=None, delete_after=5.0)
                else:
                    if res.content.isdigit():
                        resnum = int(res.content)-1
                        resanimu = retrieve(searchres[resnum])
                        await msg.edit(embed=resanimu)
                        await res.delete()
                    elif res.content == 'cancel':
                        await msg.edit(content='Cancelled.', embed=None, delete_after=5.0)
                        await res.delete()


bot.run(token)
