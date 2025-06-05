import discord
from discord.ext import commands
import os
import json

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

    try:
        with open('reaction_roles.json', 'r') as f:
            pass
    except FileNotFoundError:
        with open('reaction_roles.json', 'w') as f:
            json.dump({}, f)

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
@commands.has_permissions(manage_roles=True)
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
            roles_list.append((reaction_emoji, role.id))
        else:
            await interaction.response.send_message(f"Role {role_name} not found", ephemeral=True)
            return

    msg = await channel.send(description)
    for reaction, role.id in roles_list:
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

    # Write the reactions and role IDs to a JSON file
    try:
        with open('reaction_roles.json', 'r') as f:
            reaction_roles = json.load(f)
    except FileNotFoundError:
        reaction_roles = {}
    except json.JSONDecodeError:
        reaction_roles = {}

    if str(msg.id) not in reaction_roles:
        reaction_roles[str(msg.id)] = {}

    for reaction, role_id in roles_list:
        reaction_roles[str(msg.id)][reaction] = role_id

    with open('reaction_roles.json', 'w') as f:
        json.dump(reaction_roles, f)

    await interaction.response.send_message(f'Reaction role message created in {channel.mention}!', ephemeral=True)

'''
@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message.id in bot.message_reactions:
        reactions_list = bot.message_reactions[reaction.message.id]
        for reaction_emoji, role in reactions_list:
            if reaction.emoji == reaction_emoji:
                await user.add_roles(role)
                print(f"Added role {role.name} to user {user.name}")
'''
@bot.tree.command(name='edit-role-menu', description='Edit a role menu')
@commands.has_permissions(manage_roles=True)
async def edit_role_menu(
        interaction: discord.Interaction,
        message_id: str,
        new_description: str = None,
        new_reactions: str = None
        ):

    message_int = int(message_id)
    if message_int not in bot.message_reactions:
        await interaction.response.send_message("Role Menu not found", ephemeral=True)
        return
    
    msg = await interaction.channel.fetch_message(message_id)
    if new_description:
        await msg.edit(content=new_description)


    if new_reactions:
        reactions_list = new_reactions.split(',')
        roles_list = []
        for reaction in reactions_list:
            parts = reaction.split(':')
            if len(parts) != 2:
                await interaction.response.send_message(f"Invalid reaction format: {reaction}", ephemeral=True)
                return
            reaction_emoji = parts[0].strip()
            role_name = parts[1].strip()
            role = discord.utils.get(interaction.guild.roles, name=role_name)
            if role:
                roles_list.append((reaction_emoji, role.id))
            else:
                await interaction.response.send_message(f"Role {role_name} not found", ephemeral=True)
                return
        await msg.clear_reactions()
        for reaction_emoji, role in roles_list:
            await msg.add_reaction(reaction_emoji)
        
        bot.message_reactions[message_id] = roles_list
    try:
        with open('reaction_roles.json', 'r') as f:
            reaction_roles = json.load(f)
    except FileNotFoundError:
        reaction_roles = {}
    except json.JSONDecodeError:
        reaction_roles = {}

    if str(msg.id) not in reaction_roles:
        reaction_roles[str(msg.id)] == {}
        for reaction_emoji, role_id in bot.message_reactions[message.id]:
            reaction_roles[str(msg.id)][reaction_emoji] = role_id
    else:
        reaction_roles[str(msg.id)] = {}
        for reaction_emoji, role_id in bot.message_reactions[message_id]:
            reaction_roles[str(msg.id)][reaction_emoji] = role_id

    with open('reaction_roles.json', 'w') as f:
        json.dump(reaction_roles, f)

    await interaction.response.send_message("Role menu edited successfully", ephemeral=True)

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    print(f"Reaction detected: {payload.emoji}")
    # Load the reaction role mapping
    try:
        with open('reaction_roles.json', 'r') as f:
            reaction_roles = json.load(f)
    except FileNotFoundError:
        print("reaction_roles.json file not found")
        return
    except json.JSONDecodeError:
        print("Invalid JSON in reaction_roles.json file")
        return
   
    if str(payload.message_id) in reaction_roles:
        if payload.emoji.name in reaction_roles[str(payload.message_id)]:
            role_id = int(reaction_roles[str(payload.message_id)][payload.emoji.name])
            if role_id:
                # Get the role
                print(f"Role ID: {role_id}")
                guild = bot.get_guild(payload.guild_id)
                role = discord.utils.get(guild.roles, id=int(role_id))
                if role:
                    print(f"Role: {role}")
                    # Add the role to the member
                    member = guild.get_member(payload.user_id)
                    if member:
                        try:
                            await member.add_roles(role)
                            print(f"Role added to {member.name}")
                        except Exception as e:
                            print(f"Error adding role: {e}")


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    try:
        # Load the reaction role mapping
        with open('reaction_roles.json', 'r') as f:
            reaction_roles = json.load(f)
    except FileNotFoundError:
        print("reaction_roles.json file not found")
        return
    except json.JSONDecodeError:
        print("Invalid JSON in reaction_roles.json file")
        return
    
    # Get the role associated with the reaction
    if str(payload.message_id) in reaction_roles:
        if payload.emoji.name in reaction_roles[str(payload.message_id)]:
            role_id = int(reaction_roles[str(payload.message_id)][payload.emoji.name])
            if role_id:
                # Get the role
                guild = bot.get_guild(payload.guild_id)
                role = discord.utils.get(guild.roles, id=int(role_id))
                if role:
                    # Remove the role from the member
                    member = guild.get_member(payload.user_id)
                    if member:
                        try:
                            await member.remove_roles(role)
                            print(f"Role removed from {member.name}")
                        except Exception as e:
                            print(f"Error removing role: {e}")


def get_default_role_id(guild_id):
    try:
        with open('default_roles.json', 'r') as f:
            default_roles = json.load(f)
            return default_roles.get(str(guild_id))
    except FileNotFoundError:
        return None


def set_default_role_id(guild_id, role_id):
    try:
        with open('default_roles.json', 'r') as f:
            default_roles = json.load(f)
    except FileNotFoundError:
        default_roles = {}

    default_roles[str(guild_id)] = role_id

    with open('default_roles.json', 'w') as f:
        json.dump(default_roles, f)


@bot.tree.command(name='set-default-role', description='Set a role to be given to members upon joining the server')
@commands.has_permissions(manage_roles=True)
async def set_default_role(interaction: discord.Interaction, role: discord.Role):
    # Store the default role ID in a database or configuration file
    set_default_role_id(interaction.guild.id, role.id)
    # Save the default role ID
    await interaction.response.send_message(f"Default role set to {role.name}", ephemeral=True)


@bot.event
async def on_member_join(member):
    print(f"{member.name} has joined the guild!")
    
    # Retrieve the default role ID from the database or configuration file
    default_role_id = get_default_role_id(member.guild.id)
    if default_role_id:
        # Get the default role object
        default_role = member.guild.get_role(int(default_role_id))
        if default_role:
            # Add the default role to the new member
            await member.add_roles(default_role)

@bot.command()
@commands.has_permissions(administrator=True)
async def reconnect(ctx):
    await ctx.send("Reconnecting...")
    # Disconnect the bot
    await bot.close()
    # Reconnect with the new code
    await bot.login(bot_token)
    await bot.start(bot_token)


bot.run(bot_token)
