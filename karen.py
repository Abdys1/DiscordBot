import discord
import random
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os

f = open('.env', 'r')
TOKEN = f.readline()

client = commands.Bot(command_prefix='!')


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game('with your feelings'))
    print('mukodik.')


@client.event
async def on_member_join(member):
    print(f'{member} csatlakozott.')


@client.event
async def on_member_remove(member):
    print(f'{member} kilépett.')


@client.command()
async def ivó(ctx):
    responses = ['Ivó meleg!',
                 'Cigizni ment.',
                 'Puszi a pocidra.',
                 'Eperke.']
    await ctx.send(random.choice(responses))


# moderációs parancsok, amiket majd külön akarok menteni#

@client.command()
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)


@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member.mention} kickelve!')


@client.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member.mention} bannolva!')


@client.command()
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'{user.mention} nincs többé bannolva!')
            return


# zenelejátszós parancsok, amiket majd külön akarok menteni#

@client.command(pass_content=True)
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    await ctx.send(f'Csatlakoztam a {channel}-hez!')


@client.command(pass_context=True)
async def leave(ctx):
    global voice
    # channel = ctx.message.author.voice.channel#
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send(f'De hát ott sem vagyok!')


@client.command(pass_context=True, aliases=['p'])
async def play(ctx, url: str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            print('Régi zenefájl törölve.')
    except PermissionError:
        print('Próbálom, de épp megy.')
        await ctx.send(f'Hiba! A zene megy.')
        return

    await ctx.send(f'Alakulunk.')

    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print('töltöm a zenét.\n')
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f'Átnevezve: {file}\n')
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print(f'{name} véget ért.'))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07

    nname = name.replit("-", 2)
    await ctx.send(f'{nname} szól!')
    print('playing.')


@client.command(pass_content=True)
async def pause(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print('pause: check')
        voice.pause()
        await ctx.send(f'Minek neked zene, ha megállítod?')
    else:
        print('failed to pause: no music')
        await ctx.send(f'Jó, hogy nem vagy süket...')


@client.command(pass_content=True)
async def resume(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print('resume: check')
        voice.resume()
        await ctx.send(f'Na, mégis kéne?')
    else:
        print('failed to resume: not paused')
        await ctx.send(f'Meg sincs állítva, gyökér...')


@client.command(pass_content=True)
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print('playing: check')
        voice.stop()
        await ctx.send(f'Döntsd el, hogy kell-e vagy sem!')
    else:
        print('failed to stop: no music')
        await ctx.send(f'Süket is vagy? Nem szól semmi!')


client.run(TOKEN)
