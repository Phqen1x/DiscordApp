import discord
from discord.ext import commands
import os

intents = discord.Intents.all()

application_id = os.environ['APP_ID']
bot_token = os.environ['BOT_TOKEN']

bot = commands.Bot(command_prefix='!', intents=intents, application_id=application_id)

@bot.event
async def on_ready():
    try:
        await bot.tree.sync(guild=discord.Object(id=793600464570548254))
        print('Commands synced')
    except Exception as e:
        print(f"Error syncing commands: {e}")
    bot.message_reactions = {}
    print(f'{bot.user} has connected to Discord!')

@bot.command()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("Commands synced")

# def evaluate_response(response):
#     correct_answer = "jason"
#     return response.lower() == correct_answer

# @bot.tree.command(name='verify', description='Submit your answer')
# async def verify(interaction: discord.Interaction, response: str):
#     if evaluate_response(response):
#         role = discord.utils.get(interaction.guild.roles, name="Verified")
#         old_role = discord.utils.get(interaction.guild.roles, name="Unverified")
#         if role and old_role:
#             await interaction.user.add_roles(role)
#             await interaction.user.remove_roles(old_role)
#             await interaction.response.send_message("You have been verified! Please visit https://discordapp.com/channels/1368764933021634641/1368785712505159710 and read our rules to gain access to the rest of the server!", ephemeral=True)
#     else:
#         await interaction.response.send_message("That is not the correct answer! Please try again!", ephemeral=True)

# @bot.event
# async def on_interaction(interaction):
#     if interaction.channel.id == 1368800194996736030:  # Replace CHANNEL_ID with the ID of the channel you want to monitor
#         if interaction.type == discord.InteractionType.application_command:  # Check if the interaction is an application command
#             return
#         else:
#             await interaction.response.send_message("This is not an application command", ephemeral=True)
#             await interaction.delete_original_message()

# @bot.event
# async def on_message(message):
#     if message.channel.id == 1368800194996736030:  # Replace CHANNEL_ID with the ID of the channel you want to monitor
#         if not message.content.startswith(bot.command_prefix):  # Replace bot.command_prefix with your bot's command prefix
#             await message.delete()
#     await bot.process_commands(message)

@bot.tree.command(name='reaction-role', description='Create a reaction role menu message')
async def reaction_role(
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        description: str,
        reactions: str
):
    reactions_list = reactions.split(',')
    roles_list=[]
    for reaction in reactions_list:
        parts = reaction.split(':')
        if len(parts) != 2:
            await interaction.response.send_message(f"Invalid reaction format: {reaction}", ephemeral=True)
            return
        reaction_emoji = parts[0].strip()
        role_name = parts[1].strip()
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if role:
            roles_list.append((reaction_emoji, role))
        else:
            await interaction.response.send_message(f"Role {role_name} not found", ephemeral=True)
            return

    msg = await channel.send(description)
    for reaction, role in roles_list:
        try:
            await msg.add_reaction(reaction)
        except discord.HTTPException as e:
            if e.status == 400 and e.text == '{"message": "Unknown Emoji", "code": 10014}':
                await interaction.response.send_message(f"Invalid reaction emoji: {reaction}")
            else:
                raise

    # Store the message ID and reaction in a dictionary to monitor later
    bot.message_reactions = getattr(bot, 'message_reactions', {})
    bot.message_reactions[msg.id] = roles_list
    await interaction.response.send_message(f'Reaction role message created in {channel.mention}!', ephemeral=True)

@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message.id in bot.message_reactions:
        reactions_list = bot.message_reactions[reaction.message.id]
        for reaction_emoji, role in reactions_list:
            if reaction.emoji == reaction_emoji:
                await user.add_roles(role)
                print(f"Added role {role.name} to user {user.name}")

@bot.tree.command(name='edit-role-menu', description='Edit a role menu')
async def edit_role_menu(
        interaction: discord.Interaction,
        message_id: int,
        new_description: str = None,
        new_reactions: str = None
        ):
    if message_id not in bot.message_reactions:
        await interaction.response.send_message("Role Menu not found", ephemeral=True)
        return
    
    message = await interaction.channel.fetch_message(message_id)
    if new_description:
        await message.edit(content=new_description)

    if new_reactions:
        reactions_list = new_reacrtions.split(',')
        roles_list = []
        for reaction in reactions_list:
            parts = reaction.split(':')
            if len(parts) != 2:
                await interaction.response.send_message(f"Invalid reaction format: {reaction}", ephemeral=True)
                return
            reaction_emoji = parts[0].strip()
            role_name = parts[1].lower().strip()
            role = discord.utils.get(interaction.guild.roles, name=role_name)
            if role:
                roles_list.append((reaction_emoji, role))
            else:
                await interaction.response.send_message(f"Role {role_name} not found", ephemeral=True)
                return
        await message.clear_reactions()
        for reaction_emoji, role in roles_list:
            await message.add_reaction(reaction_emoji)
        
        bot.message_reactions[message_id] = roles_list
    
    await interaction.response.send_message("Role menu edited successfully", ephemeral=True)

'''
reaction_roles = { '👑': 'Game Staff'}

@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id == 1370116495224475769:
        if payload.emoji.name == '✅':
            guild = bot.get_guild(payload.guild_id)
            member = await guild.fetch_member(payload.user_id)
            role = discord.utils.get(guild.roles, name=reaction_roles[payload.emoji.name]) 
            if role:
                try: 
                    await member.add_roles(role)
                    print(f'Assigned {role.name} to {member.name}')
                except Exception as e:
                    print("Error assigning role:", e)
        else:
            print("Emoji name mismatched.")
'''
@bot.tree.command(name='default-role', description='A starting role on the server')
 def default_role(ctx, ):
    print(f"{member.name} has joined the guild!")
    
    guild = member.guild

    role = discord.utils.get(guild.roles, name="Unverified")
    if role:
        try:
            await member.add_roles(role)
            print(f"Role added to {member.name}")
        except discord.Forbidden:
            print(f"Bot does not have permission to add role to {member.name}")
        except discord.HTTPException as e:
            print(f"Error adding role to {member.name}: {e, text}")
    else:
        print(f"Role not found: Unverified")
    
    
    channel = bot.get_channel(1368764934019612803)
    await channel.send(f"Welcome to {member.guild.name}, {member.mention}! Please ensure you abide by {bot.get_channel(1368785712505159710).mention} at all times!")

@bot.command()
async def reconnect(ctx):
    await ctx.send("Reconnecting...")
    # Disconnect the bot
    await bot.close()
    # Reconnect with the new code
    await bot.login(bot_token)
    await bot.start(bot_token)

bot.run(bot_token)
