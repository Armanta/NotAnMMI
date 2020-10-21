import discord
from discord.ext import commands
from discord.ext.commands.errors import *
import settings

OWNER_ID = 602994882927132731

bot = commands.Bot(command_prefix="-", description="Not An MMI")


def not_connected():
    async def predicate(ctx):
        if settings.connected_clients:
            for client in settings.connected_clients:
                if ctx.author.id == client.secure_id:
                    embed = discord.Embed(title="Erreur :x:",
                                          description="Vous êtes déjà connecté",
                                          color=0xe10e0e)
                    await ctx.send(embed=embed)
                    return False
                elif client == settings.connected_clients[-1] and ctx.author.id == client.secure_id:
                    return True
        else:
            return True
    return commands.check(predicate)


def connected(func):
    async def decorator(ctx, *args, **kwargs):
        print(args)
        if settings.connected_clients:
            for client in settings.connected_clients:
                if ctx.author.id == client.secure_id:
                    await func(client, ctx, *args, **kwargs)
                elif client == settings.connected[-1] and ctx.author.id == client.secure_id:
                    embed = discord.Embed(title="Erreur :x:",
                                          description="Vous n'êtes pas connecté",
                                          color=0xe10e0e)
                    await ctx.send(embed=embed)
                    return
        else:
            embed = discord.Embed(title="Erreur :x:",
                              description="Vous n'êtes pas connecté",
                              color=0xe10e0e)
            await ctx.send(embed=embed)
            return
    decorator.__name__ = func.__name__ #https://medium.com/@cantsayihave/decorators-in-discord-py-e44ce3a1aae5
    return decorator

@bot.event
async def on_ready():
    print("Ready !")
    await bot.change_presence(activity=discord.Streaming(name="Zevent#2020", url="https://www.twitch.tv/zerator"))


@bot.command()
@commands.dm_only()
@not_connected()
async def login(ctx, username, password):
    mail = settings.Mail(ctx.author.id)

    if (error := mail.login(username, password)):
        embed = discord.Embed(title="Erreur :x:",
                              description=error,
                              color=0xe10e0e)
    else:
        embed = discord.Embed(title="Boite Mail",
                              description=f"Vous êtes connecté en tant que: `{username}`",
                              color=0x12f368)
        embed.add_field(name="Dossiers",
                        value=f"{' | '.join(mail.folders)}",
                        inline=False)
    await ctx.send(embed=embed)

@login.error
async def login_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        embed = discord.Embed(title="Erreur :x:",
                              description="Veuillez saisir un nom d'utilisateur ainsi qu'un mot de passe",
                              color=0xe10e0e)
        await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def debug(ctx):
    embed = discord.Embed(title="Debug Mode",
                          description=f"{len(settings.connected_clients)}",
                          color=0x12f368)
    for client in settings.connected_clients:
        embed.add_field(name="Nom d'utilisateur",
                    value=client.username,
                    inline=False)
    await ctx.send(embed=embed)

@bot.command()
@commands.dm_only()
@connected
async def logout(session, ctx):
    session.logout()
    embed = discord.Embed(title="Déconnexion",
                          description=f"Vous vous êtes déconnectés",
                          color=0x12f368)
    await ctx.send(embed=embed)

@bot.command()
@commands.dm_only()
@connected
async def show(session, ctx, folder, filter):
    #https://gist.github.com/martinrusev/6121028
    error, id_list, response= session.show(folder, filter)

    if error:
           for id in id_list:
               mail = session.parse(id)
               embed = discord.Embed(title=mail.get("From"),
                                     description=mail.get("Subject"),
                                     color=0xe10e0e)
               await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Erreur :x:",
                              description=response,
                              color=0xe10e0e)
        await ctx.send(embed=embed)

@show.error
async def show_error(ctx, error):
    if isinstance(error, CommandInvokeError):
        embed = discord.Embed(title="Erreur :x:",
                              description="Veuillez saisir un nom nom de dossier ainsi qu'un filtre",
                              color=0xe10e0e)
        await ctx.send(embed=embed)

@bot.command()
async def mailconf(ctx):
    embed = embed = discord.Embed(title="Mail Config v1.0",
                                  description="Recevez vos mails Universitaire via Discord")
    embed.add_field(name="-login user pass",
                    value="Se connecter à un mail universitaire",
                    inline=False)
    embed.add_field(name="-logout",
                    value="Se déconnecter d'un mail universitaire",
                    inline=False)
    embed.add_field(name="-show folder filtre",
                    value="Afficher les messages d'une boite mail\n"
                          "Filtre: `ALL`, `UNSEEN`, `RECENT`, `NEW`, `ALL`, `SEEN`",
                    inline=False)
    await ctx.author.send(embed=embed)

@bot.command()
async def infos(ctx):
    server = ctx.guild
    embed = discord.Embed(title=server.name, description=server.description)
    embed.set_thumbnail(url=server.icon_url)
    embed.set_author(name="Developped by An RT")
    embed.add_field(name="Membres", value=server.member_count, inline=True)
    embed.add_field(name="Text Channel", value=len(server.text_channels), inline=True)
    embed.add_field(name="Voice Channel", value=len(server.voice_channels), inline=True)
    embed.add_field(name="Created at", value=server.created_at.strftime('%y-%m-%d %a %H:%M:%S'), inline=True)
    embed.set_footer(text="RT is the safest way to success")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def say(ctx, *txt):
    await ctx.message.delete()
    await ctx.send(" ".join(txt))

@bot.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, number: int):
    history = await ctx.channel.history(limit=number + 1).flatten()
    for msg in history:
        await msg.delete()

bot.run("Not for Today :)")
