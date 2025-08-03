import discord
from discord.ext import commands
import os
import logging
import datetime
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration des intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Créer le bot
bot = commands.Bot(command_prefix='+', intents=intents)

# Dictionnaire pour stocker les rôles sauvegardés des utilisateurs mutés
muted_users_roles = {}

@bot.event
async def on_ready():
    logger.info(f'Bot connecté en tant que {bot.user}!')
    logger.info(f'Connecté à {len(bot.guilds)} serveur(s)')

@bot.event
async def on_message(message):
    # Ignorer les messages du bot
    if message.author == bot.user:
        return
    
    # Liste des commandes valides du bot
    valid_commands = ['ping', 'test', 'ban', 'unban', 'kick', 'unmute', 'commandes']
    
    # Si le message commence par +, vérifier si c'est une commande valide
    if message.content.startswith('+'):
        command_name = message.content[1:].split()[0].lower()  # Extraire le nom de la commande
        
        # Si c'est une commande valide, logger et traiter
        if command_name in valid_commands:
            logger.info(f"MESSAGE REÇU: '{message.content}' de {message.author} dans #{message.channel}")
            await bot.process_commands(message)
        # Sinon, ignorer complètement (pas de log, pas de traitement)
        return
    
    # Pour les messages sans +, traiter normalement (au cas où il y aurait d'autres événements)
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # Ne rien faire, même pas de log pour éviter le spam complet
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argument manquant. Utilisez `+commandes` pour voir la syntaxe correcte.")
        logger.error(f"Argument manquant: {error} | Message: {ctx.message.content}")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Vous n'avez pas les permissions nécessaires pour cette commande!")
        logger.error(f"Permissions manquantes: {error} | Utilisateur: {ctx.author}")
    else:
        logger.error(f"ERREUR COMMANDE: {error} | Message: {ctx.message.content}")
        await ctx.send(f"❌ Erreur: {error}")

@bot.command(name='ping')
async def ping(ctx):
    logger.info(f"COMMANDE PING exécutée par {ctx.author}")
    await ctx.send('🏓 Pong! Le bot fonctionne!')

@bot.command(name='test')
async def test(ctx):
    logger.info(f"COMMANDE TEST exécutée par {ctx.author}")
    await ctx.send('✅ Test réussi! Le bot répond correctement.')

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None, *, reason="Aucune raison spécifiée"):
    # Si pas de mention, vérifier si c'est une réponse à un message
    if member is None:
        if ctx.message.reference and ctx.message.reference.message_id:
            try:
                # Récupérer le message original
                referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                # Vérifier que l'auteur du message est un membre du serveur
                if isinstance(referenced_message.author, discord.Member):
                    member = referenced_message.author
                else:
                    await ctx.send("❌ L'auteur du message n'est pas un membre de ce serveur!")
                    return
            except discord.NotFound:
                await ctx.send("❌ Message de référence non trouvé!")
                return
            except Exception as e:
                await ctx.send(f"❌ Erreur lors de la récupération du message: {e}")
                return
        else:
            await ctx.send("❌ Veuillez mentionner un utilisateur ou répondre à un message pour bannir quelqu'un!")
            return
    
    logger.info(f"COMMANDE BAN tentée par {ctx.author} sur {member}")
    
    try:
        await member.ban(reason=f"{reason} - Par {ctx.author}")
        await ctx.send(f"🔨 {member} a été banni! Raison: {reason}")
        logger.info(f"BAN RÉUSSI: {member} banni par {ctx.author}")
    except Exception as e:
        await ctx.send(f"❌ Erreur lors du ban: {e}")
        logger.error(f"ERREUR BAN: {e}")

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None, *, reason="Aucune raison spécifiée"):
    # Si pas de mention, vérifier si c'est une réponse à un message
    if member is None:
        if ctx.message.reference and ctx.message.reference.message_id:
            try:
                # Récupérer le message original
                referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                # Vérifier que l'auteur du message est un membre du serveur
                if isinstance(referenced_message.author, discord.Member):
                    member = referenced_message.author
                else:
                    await ctx.send("❌ L'auteur du message n'est pas un membre de ce serveur!")
                    return
            except discord.NotFound:
                await ctx.send("❌ Message de référence non trouvé!")
                return
            except Exception as e:
                await ctx.send(f"❌ Erreur lors de la récupération du message: {e}")
                return
        else:
            await ctx.send("❌ Veuillez mentionner un utilisateur ou répondre à un message pour expulser quelqu'un!")
            return
    
    logger.info(f"COMMANDE KICK tentée par {ctx.author} sur {member}")
    
    try:
        await member.kick(reason=f"{reason} - Par {ctx.author}")
        await ctx.send(f"👢 {member} a été expulsé! Raison: {reason}")
        logger.info(f"KICK RÉUSSI: {member} expulsé par {ctx.author}")
    except Exception as e:
        await ctx.send(f"❌ Erreur lors du kick: {e}")
        logger.error(f"ERREUR KICK: {e}")

@bot.command(name='unban')
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int, *, reason="Aucune raison spécifiée"):
    logger.info(f"COMMANDE UNBAN tentée par {ctx.author} pour l'ID {user_id}")
    
    try:
        # Récupérer l'utilisateur par son ID
        user = await bot.fetch_user(user_id)
        # Débannir l'utilisateur
        await ctx.guild.unban(user, reason=f"{reason} - Par {ctx.author}")
        await ctx.send(f"✅ {user} a été débanni! Raison: {reason}")
        logger.info(f"UNBAN RÉUSSI: {user} débanni par {ctx.author}")
    except discord.NotFound:
        await ctx.send(f"❌ Aucun utilisateur banni trouvé avec l'ID: {user_id}")
        logger.error(f"ERREUR UNBAN: Utilisateur ID {user_id} non trouvé dans les bannissements")
    except Exception as e:
        await ctx.send(f"❌ Erreur lors du unban: {e}")
        logger.error(f"ERREUR UNBAN: {e}")




@bot.command(name='unmute')
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, target=None, *, reason="Aucune raison spécifiée"):
    logger.info(f"COMMANDE UNMUTE tentée par {ctx.author}")
    
    # Si "all" est spécifié, démute tous les membres avec le rôle Muted
    if target and target.lower() == "all":
        count = 0
        try:
            muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
            if not muted_role:
                await ctx.send("❌ Aucun rôle 'Muted' trouvé sur ce serveur!")
                return
            
            for member in ctx.guild.members:
                if muted_role in member.roles:
                    # Restaurer les anciens rôles si disponibles
                    if member.id in muted_users_roles:
                        old_roles = []
                        for role_id in muted_users_roles[member.id]:
                            role = ctx.guild.get_role(role_id)
                            if role:
                                old_roles.append(role)
                        
                        if old_roles:
                            await member.edit(roles=old_roles, reason=f"Unmute all - {reason} - Par {ctx.author}")
                        else:
                            # Si pas de rôles sauvegardés, chercher un rôle de base comme "Membre" ou "@everyone"
                            base_role = discord.utils.get(ctx.guild.roles, name="Membre")
                            if base_role:
                                await member.edit(roles=[base_role], reason=f"Unmute all - {reason} - Par {ctx.author}")
                            else:
                                await member.remove_roles(muted_role, reason=f"Unmute all - {reason} - Par {ctx.author}")
                        
                        # Supprimer de la sauvegarde
                        del muted_users_roles[member.id]
                    else:
                        # Chercher un rôle de base pour les utilisateurs sans sauvegarde
                        base_role = discord.utils.get(ctx.guild.roles, name="Membre")
                        if base_role:
                            await member.edit(roles=[base_role], reason=f"Unmute all - {reason} - Par {ctx.author}")
                        else:
                            await member.remove_roles(muted_role, reason=f"Unmute all - {reason} - Par {ctx.author}")
                    
                    count += 1
                    logger.info(f"UNMUTE: {member} démute par {ctx.author}")
            
            await ctx.send(f"🔊 {count} utilisateur(s) ont été démutés et leurs rôles restaurés! Raison: {reason}")
            logger.info(f"UNMUTE ALL RÉUSSI: {count} utilisateurs démutés par {ctx.author}")
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du unmute all: {e}")
            logger.error(f"ERREUR UNMUTE ALL: {e}")
        return
    
    # Sinon, traiter comme unmute d'un utilisateur spécifique
    member = None
    
    # Vérifier si c'est une mention
    if ctx.message.mentions:
        member = ctx.message.mentions[0]
    # Vérifier si c'est une réponse à un message
    elif ctx.message.reference and ctx.message.reference.message_id:
        try:
            referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if isinstance(referenced_message.author, discord.Member):
                member = referenced_message.author
            else:
                await ctx.send("❌ L'auteur du message n'est pas un membre de ce serveur!")
                return
        except discord.NotFound:
            await ctx.send("❌ Message de référence non trouvé!")
            return
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la récupération du message: {e}")
            return
    else:
        await ctx.send("❌ Veuillez mentionner un utilisateur, répondre à un message, ou utiliser `+unmute all`!")
        return
    
    try:
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            await ctx.send("❌ Aucun rôle 'Muted' trouvé sur ce serveur!")
            return
        
        if muted_role not in member.roles:
            await ctx.send(f"❌ {member} n'est pas mute!")
            return
        
        # Restaurer les anciens rôles si disponibles
        if member.id in muted_users_roles:
            old_roles = []
            for role_id in muted_users_roles[member.id]:
                role = ctx.guild.get_role(role_id)
                if role:
                    old_roles.append(role)
            
            if old_roles:
                await member.edit(roles=old_roles, reason=f"Unmute - {reason} - Par {ctx.author}")
                await ctx.send(f"🔊 {member} a été démute et ses {len(old_roles)} rôles ont été restaurés! Raison: {reason}")
            else:
                # Si pas de rôles sauvegardés, chercher un rôle de base comme "Membre"
                base_role = discord.utils.get(ctx.guild.roles, name="Membre")
                if base_role:
                    await member.edit(roles=[base_role], reason=f"Unmute - {reason} - Par {ctx.author}")
                    await ctx.send(f"🔊 {member} a été démute et a reçu le rôle de base! Raison: {reason}")
                else:
                    await member.remove_roles(muted_role, reason=f"Unmute - {reason} - Par {ctx.author}")
                    await ctx.send(f"🔊 {member} a été démute! Raison: {reason}")
            
            # Supprimer de la sauvegarde
            del muted_users_roles[member.id]
        else:
            # Pour les utilisateurs sans sauvegarde, donner le rôle de base
            base_role = discord.utils.get(ctx.guild.roles, name="Membre")
            if base_role:
                await member.edit(roles=[base_role], reason=f"Unmute - {reason} - Par {ctx.author}")
                await ctx.send(f"🔊 {member} a été démute et a reçu le rôle de base! Raison: {reason}")
            else:
                await member.remove_roles(muted_role, reason=f"Unmute - {reason} - Par {ctx.author}")
                await ctx.send(f"🔊 {member} a été démute! Raison: {reason}")
        
        logger.info(f"UNMUTE RÉUSSI: {member} démute par {ctx.author}")
        
    except Exception as e:
        await ctx.send(f"❌ Erreur lors du unmute: {e}")
        logger.error(f"ERREUR UNMUTE: {e}")

@bot.command(name='commandes')
async def commandes_command(ctx):
    logger.info(f"COMMANDE COMMANDES exécutée par {ctx.author}")
    embed = discord.Embed(title="🛡️ Commandes de Modération", color=0x00ff00)
    embed.add_field(name="+ping", value="Teste la connexion", inline=False)
    embed.add_field(name="+test", value="Test général du bot", inline=False)
    embed.add_field(name="+ban @utilisateur [raison]", value="Bannir un utilisateur (mention ou réponse)", inline=False)
    embed.add_field(name="+unban <ID_utilisateur> [raison]", value="Débannir un utilisateur avec son ID", inline=False)
    embed.add_field(name="+kick @utilisateur [raison]", value="Expulser un utilisateur (mention ou réponse)", inline=False)


    embed.add_field(name="+unmute @utilisateur [raison]", value="Démute et restaure rôles ou attribue rôle de base", inline=False)
    embed.add_field(name="+commandes", value="Affiche cette liste de commandes", inline=False)
    await ctx.send(embed=embed)

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("❌ DISCORD_TOKEN non trouvé!")
    else:
        logger.info("🚀 Démarrage du bot...")
        bot.run(token)