####################################################################
#                                                                  #
#    Credit: therealOri  |  https://github.com/therealOri          #
#                                                                  #
####################################################################

####################################################################################
#                                                                                  #
#                            Imports & definitions                                 #
#                                                                                  #
####################################################################################
import asyncio
import discord
import os
import datetime
from libs import rnd
import time
import logging
import sqlite3
import zipfile
from beaupy.spinners import *
from discord.ext import commands
import re
from dotenv import load_dotenv
from discord import app_commands  # Added for slash commands
import csv  # For CSV export
import dateparser
import pytz

CET_TZ = pytz.timezone('Europe/Berlin')

# Load environment variables
load_dotenv()

token = os.getenv('TOKEN')
bot_logo = os.getenv('BOT_LOGO')

hex_red=0xFF0000
hex_green=0x0AC700
hex_yellow=0xFFF000 # I also like -> 0xf4c50b

# +++++++++++ Imports and definitions +++++++++++ #














####################################################################################
#                                                                                  #
#                             Normal Functions                                     #
#                                                                                  #
####################################################################################
def clear():
    os.system("clear||cls")



def random_hex_color():
    hex_digits = '0123456789abcdef'
    hex_digits = rnd.shuffle(hex_digits)
    color_code = ''
    nums = rnd.randint(0, len(hex_digits)-1, 6)
    for _ in nums:
        color_code += hex_digits[_]
    value =  int(f'0x{color_code}', 16)
    return value

def create_table(db_conn, table_name):
    c = db_conn.cursor()
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            row INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            user_name TEXT,
            note TEXT,
            creator_name TEXT,
            created_at TEXT,
            updated_at TEXT
        );
    """)

    c.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in c.fetchall()]

    if "creator_name" not in columns:
        c.execute(f"ALTER TABLE {table_name} ADD COLUMN creator_name TEXT DEFAULT 'Unknown'")

    if "created_at" not in columns:
        c.execute(f"ALTER TABLE {table_name} ADD COLUMN created_at TEXT")
        now = datetime.datetime.now(CET_TZ).isoformat()
        c.execute(f"UPDATE {table_name} SET created_at = ? WHERE created_at IS NULL", (now,))

    if "updated_at" not in columns:
        c.execute(f"ALTER TABLE {table_name} ADD COLUMN updated_at TEXT")
        now = datetime.datetime.now(CET_TZ).isoformat()
        c.execute(f"UPDATE {table_name} SET updated_at = ? WHERE updated_at IS NULL", (now,))

    db_conn.commit()

def parse_time(time_str):
    import re
    now = datetime.datetime.now(CET_TZ)
    if re.match(r'^\d{1,2}(:\d{2})?$', time_str):
        time_str = f"at {time_str}"
    parsed = dateparser.parse(time_str, settings={'TIMEZONE': 'CET', 'RETURN_AS_TIMEZONE_AWARE': True, 'PREFER_DATES_FROM': 'future'})
    if parsed is None:
        return None
    if parsed.date() == now.date() and parsed < now:
        parsed += datetime.timedelta(days=1)
    return parsed

def create_reminders_table(db_conn, table_name):
    c = db_conn.cursor()
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT,
            user_id TEXT,
            creator_id TEXT,
            content TEXT,
            target_time TEXT,
            sent INTEGER DEFAULT 0,
            created_at TEXT
        );
    """)
    db_conn.commit()

# +++++++++++ Normal Functions +++++++++++ #













####################################################################################
#                                                                                  #
#                   Async Functions, buttons, modals, etc.                         #
#                                                                                  #
####################################################################################
async def status():
    while True:
        status_messages = ['Meta Huntering in BM', 'Getting HoF in Manaforge Omega', 'BM Hunter rotation class']
        smsg = rnd.choice(status_messages)
        activity = discord.Streaming(type=1, url='https://www.youtube.com/watch?v=0TAfWiy2Sj0', name=smsg)
        await ntr.change_presence(status=discord.Status.online, activity=activity)
        await asyncio.sleep(43200) #Seconds





class dl_button(discord.ui.View):
    @discord.ui.button(label="Download!", style=discord.ButtonStyle.green, emoji="⬇️")
    async def button_callback(self, interaction, button):
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "user_db_notes.zip")
        d_file = discord.File(file_path)
        await interaction.response.send_message("Here is your notes archive! - Expires in 1min", file=d_file, delete_after=60)

# +++++++++++ Async Functions, buttons, modals, etc. +++++++++++ #

async def reminder_loop():
    while True:
        database = sqlite3.connect('/data/user_notes.db')
        c = database.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'reminders_%'")
        tables = [row[0] for row in c.fetchall()]
        now = datetime.datetime.now(CET_TZ).isoformat()
        for table in tables:
            c.execute(f"SELECT id, channel_id, user_id, creator_id, content FROM {table} WHERE sent = 0 AND target_time <= ?", (now,))
            for rid, channel_id, user_id, creator_id, content in c.fetchall():
                try:
                    creator = await ntr.fetch_user(int(creator_id))
                    creator_name = creator.name
                except:
                    creator_name = f"User {creator_id}"
                try:
                    if channel_id is not None:
                        channel = ntr.get_channel(int(channel_id))
                        if channel:
                            await channel.send(f"🔔 Reminder: {content} #requested by <@{creator_id}>")
                    elif user_id is not None:
                        user = await ntr.fetch_user(int(user_id))
                        if user:
                            await user.send(f"🔔 Reminder: {content}")
                except Exception as e:
                    print(f"Error sending reminder {rid} from {table}: {e}")
                c.execute(f"UPDATE {table} SET sent = 1 WHERE id = ?", (rid,))
        database.commit()
        database.close()
        await asyncio.sleep(60)





####################################################################################
#                                                                                  #
#                                Client Setup                                      #
#                                                                                  #
####################################################################################
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
ntr = commands.Bot(command_prefix='!', intents=intents)
ntr.remove_command('help')

# +++++++++++ Client Setup +++++++++++ #









####################################################################################
#                                                                                  #
#                                   Events                                         #
#                                                                                  #
####################################################################################
@ntr.event
async def on_ready():
    global author_logo
    me = await ntr.fetch_user(254148960510279683)
    author_logo = me.avatar
    ntr.loop.create_task(status())
    ntr.loop.create_task(reminder_loop())

    print(f'Logged in as {ntr.user} (ID: {ntr.user.id})')
    print('------')
    await ntr.tree.sync()  # Sync slash commands

@ntr.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("You must be an administrator to use this command.", delete_after=10)
    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignore unknown commands
    else:
        await ctx.reply(f"An error occurred: {str(error)}", delete_after=10)

@ntr.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True, delete_after=10)

# +++++++++++ Events +++++++++++ #













####################################################################################
#                                                                                  #
#                             Regular Commands                                     #
#                                                                                  #
####################################################################################
async def get_context_handlers(context):
    if isinstance(context, commands.Context):
        guild_id = context.guild.id if context.guild else None
        creator_name = context.author.name if context.author else 'Unknown'
        async def reply_func(content=None, **kwargs):
            return await context.reply(content, **kwargs)
        async def send_func(content=None, **kwargs):
            return await context.send(content, **kwargs)
        is_slash = False
    elif isinstance(context, discord.Interaction):
        guild_id = context.guild_id
        creator_name = context.user.name
        async def reply_func(content=None, **kwargs):
            if 'delete_after' in kwargs:
                del kwargs['delete_after']
            if not context.response.is_done():
                return await context.response.send_message(content=content, **kwargs)
            else:
                return await context.followup.send(content=content, **kwargs)
        async def send_func(content=None, **kwargs):
            if 'delete_after' in kwargs:
                del kwargs['delete_after']
            if not context.response.is_done():
                return await context.response.send_message(content=content, **kwargs)
            else:
                return await context.followup.send(content=content, **kwargs)
        is_slash = True
    else:
        raise ValueError("Invalid context type")
    creator_id = context.author.id if isinstance(context, commands.Context) else context.user.id
    return guild_id, creator_name, reply_func, send_func, is_slash, creator_id

@ntr.command(name='notehelp', description='Explains bot commands.')
@commands.has_permissions(administrator=True)
async def notehelp(context):
    guild_id, creator_name, reply_func, send_func, is_slash, creator_id = await get_context_handlers(context)
    rnd_hex = random_hex_color()
    embed = discord.Embed(title='**🔑 Commands Index**', colour=rnd_hex, timestamp=datetime.datetime.now(CET_TZ))
    embed.set_thumbnail(url=bot_logo)
    if is_slash:
        prefix = '/'
    else:
        prefix = '!'
    # Spacing after title
    embed.add_field(name="\u200b", value="\n\n", inline=False)
    # Notes title
    embed.add_field(name="**📝 __Notes__ 📝**", value="\n", inline=False)
    # Notes section
    notes_section = f"""
**🔖・{prefix}noteadd <user_id> <note>** 
Adds a new note for the user.
**📖・{prefix}readnotes <user_id>** 
Displays all notes for the user in a formatted embed. 
**🗑️・{prefix}delnote <note_id>**
Deletes a specific note and shows what was deleted. 
**🧨・{prefix}clearnotes <user_id>**
Deletes all notes for the user and lists them.
**📦・{prefix}note fetchall**
Downloads a zip archive containing CSV files of all server notes.
""".strip()
    embed.add_field(name="\u200b", value=notes_section, inline=False)
    # Spacing after notes
    embed.add_field(name="\u200b", value="\n", inline=False)
    # Reminders title
    embed.add_field(name="**⏰ __Reminders__ ⏰**", value="\n", inline=False)
    # Reminders section
    reminders_section = f"""
**📌・{prefix}rm <time> <content>**
Sets a reminder to send in the channel at the specified time.
**📩・{prefix}rmdm <time> <content>**
Sets a personal DM reminder at the specified time.
""".strip()
    embed.add_field(name="\u200b", value=reminders_section, inline=False)
    # Spacing after reminders
    embed.add_field(name="\u200b", value="\n", inline=False)
    # General title
    embed.add_field(name="**🔧 __General__ 🔧**", value="\n", inline=False)
    # General section
    general_section = f"""
**❓・{prefix}notehelp**
Shows this help message for Bot commands.
""".strip()
    embed.add_field(name="\u200b", value=general_section, inline=False)
    embed.set_footer(text="Made with 🏹 by Lainly 2025 | BM Hunter forever")
    await send_func(embed=embed)

@ntr.command(name='readnotes')
@commands.has_permissions(administrator=True)
async def readnotes(context, user_id: str):
    guild_id, creator_name, reply_func, send_func, is_slash, creator_id = await get_context_handlers(context)
    if guild_id is None:
        await reply_func("This command can only be used in a server.", ephemeral=True if is_slash else False)
        return

    database = sqlite3.connect('/data/user_notes.db')
    c = database.cursor()
    table_name = f"guild_{guild_id}"

    create_table(database, table_name)

    user_id = re.sub(r'[<@!>]', '', user_id)

    c.execute(f"SELECT row, creator_name, updated_at, note FROM {table_name} WHERE user_id = ?", (user_id,))
    rows = c.fetchall()

    if not rows:
        try:
            user = await ntr.fetch_user(int(user_id))
            username = user.name
        except:
            username = user_id
        await reply_func(f"\"{username}\" has no notes.")
        database.close()
        return

    try:
        user = await ntr.fetch_user(int(user_id))
        username = user.name
        thumbnail = user.avatar
    except:
        username = user_id
        thumbnail = None

    note_texts = []
    for r in rows:
        note_id, creator, dt, content = r
        parsed_dt = datetime.datetime.fromisoformat(dt).astimezone(CET_TZ)
        formatted_dt = parsed_dt.strftime('%d/%m/%Y %H:%M:%S | CET')
        note_texts.append(f"**Note #{note_id}**\nFrom: \"{creator}\"\nLast Update: {formatted_dt}\n{content}")

    full_text = "\n---\n".join(note_texts)

    rnd_hex = random_hex_color()
    embed = discord.Embed(title=f"Notes for \"{username}\"", description=full_text, colour=rnd_hex, timestamp=datetime.datetime.now(CET_TZ))
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    await send_func(embed=embed)
    database.close()

@ntr.command(name='delnote')
@commands.has_permissions(administrator=True)
async def delnote(context, note_id: int):
    guild_id, creator_name, reply_func, send_func, is_slash, creator_id = await get_context_handlers(context)
    if guild_id is None:
        await reply_func("This command can only be used in a server.", ephemeral=True if is_slash else False)
        return

    database = sqlite3.connect('/data/user_notes.db')
    c = database.cursor()
    table_name = f"guild_{guild_id}"

    create_table(database, table_name)

    c.execute(f"SELECT row, creator_name, updated_at, note FROM {table_name} WHERE row = ?", (note_id,))
    existing_row = c.fetchone()

    if not existing_row:
        await reply_func(f"No note found with ID {note_id}.")
    else:
        note_id, creator, dt, content = existing_row
        parsed_dt = datetime.datetime.fromisoformat(dt).astimezone(CET_TZ)
        formatted_dt = parsed_dt.strftime('%d/%m/%Y %H:%M:%S | CET')
        note_text = f"**Note #{note_id}**\nFrom: \"{creator}\"\nLast Update: {formatted_dt}\n{content}"
        c.execute(f"DELETE FROM {table_name} WHERE row = ?", (note_id,))
        database.commit()
        await reply_func(f"Deleted the following note:\n{note_text}")

    database.close()

@ntr.command(name='clearnotes')
@commands.has_permissions(administrator=True)
async def clearnotes(context, user_id: str):
    guild_id, creator_name, reply_func, send_func, is_slash, creator_id = await get_context_handlers(context)
    if guild_id is None:
        await reply_func("This command can only be used in a server.", ephemeral=True if is_slash else False)
        return

    database = sqlite3.connect('/data/user_notes.db')
    c = database.cursor()
    table_name = f"guild_{guild_id}"

    create_table(database, table_name)

    user_id = re.sub(r'[<@!>]', '', user_id)

    c.execute(f"SELECT row, creator_name, updated_at, note FROM {table_name} WHERE user_id = ?", (user_id,))
    rows = c.fetchall()

    if not rows:
        await reply_func(f"No notes found for the user with ID {user_id}.")
        database.close()
        return

    note_texts = []
    for r in rows:
        note_id, creator, dt, content = r
        parsed_dt = datetime.datetime.fromisoformat(dt).astimezone(CET_TZ)
        formatted_dt = parsed_dt.strftime('%d/%m/%Y %H:%M:%S | CET')
        note_texts.append(f"**Note #{note_id}**\nFrom: \"{creator}\"\nLast Update: {formatted_dt}\n{content}")

    full_text = "\n---\n".join(note_texts)

    c.execute(f"DELETE FROM {table_name} WHERE user_id = ?", (user_id,))
    database.commit()

    await reply_func(f"Deleted the following notes:\n{full_text}")
    database.close()

@ntr.group(name="note", invoke_without_command=True)
@commands.has_permissions(administrator=True)
async def note(context):
    guild_id, creator_name, reply_func, send_func, is_slash, creator_id = await get_context_handlers(context)
    await reply_func("Available subcommands: fetchall")

@ntr.command(name="noteadd", description="Adds a note about a user.")
@commands.has_permissions(administrator=True)
async def noteadd(context, user_id: str, *, note: str):
    guild_id, creator_name, reply_func, send_func, is_slash, creator_id = await get_context_handlers(context)
    if guild_id is None:
        await reply_func("This command can only be used in a server.", ephemeral=True if is_slash else False)
        return

    database = sqlite3.connect('/data/user_notes.db')
    c = database.cursor()
    table_name = f"guild_{guild_id}"

    create_table(database, table_name)

    user_id = re.sub(r'[<@!>]', '', user_id)

    try:
        user = await ntr.fetch_user(int(user_id))
    except:
        await reply_func("Invalid user ID.")
        database.close()
        return

    user_name = f"@{user.name}"
    now = datetime.datetime.now(CET_TZ).isoformat()
    row = (user_id, user_name, note, creator_name, now, now)
    c.execute(f"INSERT INTO {table_name} (user_id, user_name, note, creator_name, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)", row)
    database.commit()
    note_id = c.lastrowid
    await reply_func(f"✅ Note Taken. Note: {note} (ID: {note_id})")
    database.close()

@note.command(name="fetchall", description="Fetches all user notes.")
@commands.has_permissions(administrator=True)
async def note_fetchall(context):
    guild_id, creator_name, reply_func, send_func, is_slash, creator_id = await get_context_handlers(context)
    if guild_id is None:
        await reply_func("This command can only be used in a server.", ephemeral=True if is_slash else False)
        return
    guild = ntr.get_guild(guild_id) or await ntr.fetch_guild(guild_id)
    server_name = guild.name.replace(' ', '_')
    date_str = datetime.datetime.now().strftime('%d-%m-%Y')
    filename = f"{server_name}-notes-archive-{date_str}.csv"
    database = sqlite3.connect('/data/user_notes.db')
    c = database.cursor()
    table_name = f"guild_{guild_id}"
    create_table(database, table_name)
    c.execute(f"SELECT * FROM {table_name}")
    rows = c.fetchall()
    database.close()
    if rows:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['row', 'user_id', 'user_name', 'note', 'creator_name', 'created_at', 'updated_at'])
            for row in rows:
                modified_row = list(row)
                modified_row[1] = f'="{row[1]}"'  # Force user_id as text in Excel
                writer.writerow(modified_row)
        with zipfile.ZipFile('user_db_notes.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(filename)
        os.remove(filename)
        if is_slash:
            await send_func("DB logs here - Expires in 1min", view=dl_button())
        else:
            await send_func("DB logs here - Expires in 1min", view=dl_button(), delete_after=60)
    else:
        await reply_func("Database is empty - No notes available to fetch.")

# +++++++++++ Regular Commands +++++++++++ #

async def set_reminder(context, time_str: str, content: str, is_dm: bool):
    guild_id, creator_name, reply_func, send_func, is_slash, creator_id = await get_context_handlers(context)
    if guild_id is None:
        await reply_func("This command can only be used in a server.", ephemeral=True if is_slash else False)
        return
    parsed_time = parse_time(time_str)
    if parsed_time is None:
        await reply_func("Invalid time format. Examples: 'in 2 hours', 'tomorrow at 8', 'next monday at 20:00'")
        return
    if parsed_time < datetime.datetime.now(CET_TZ):
        await reply_func("Cannot set a reminder in the past.")
        return
    database = sqlite3.connect('/data/user_notes.db')
    table_name = f"reminders_{guild_id}"
    create_reminders_table(database, table_name)
    now = datetime.datetime.now(CET_TZ).isoformat()
    channel_id = context.channel.id if isinstance(context, commands.Context) else context.channel_id
    user_id = creator_id if is_dm else None
    channel_id = channel_id if not is_dm else None
    row = (str(channel_id) if channel_id else None, str(user_id) if user_id else None, str(creator_id), content, parsed_time.isoformat(), 0, now)
    c = database.cursor()
    c.execute(f"INSERT INTO {table_name} (channel_id, user_id, creator_id, content, target_time, sent, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", row)
    database.commit()
    rid = c.lastrowid
    formatted_date = parsed_time.strftime('%d/%m/%Y')
    formatted_time = parsed_time.strftime('%H:%M:%S')
    await reply_func(f"Reminder set by {creator_name} for {formatted_date}, {formatted_time}, CET. #Reminder ID:{rid}")
    database.close()

async def extract_time_and_content(arg):
    words = arg.split()
    for i in range(1, len(words) + 1):
        time_candidate = ' '.join(words[:i])
        parsed = parse_time(time_candidate)
        if parsed:
            content = ' '.join(words[i:])
            if content:  # Ensure there's content left
                return parsed, content
    return None, None

@commands.has_permissions(administrator=True)
async def prefix_rm(context, *, arg: str):
    guild_id, creator_name, reply_func, send_func, is_slash, creator_id = await get_context_handlers(context)
    if guild_id is None:
        await reply_func("This command can only be used in a server.", ephemeral=True if is_slash else False)
        return
    parsed_time, content = extract_time_and_content(arg)
    if not parsed_time or not content:
        await reply_func("Invalid format. Example: !rm in 2 hours reminder message")
        return
    if parsed_time < datetime.datetime.now(CET_TZ):
        await reply_func("Cannot set a reminder in the past.")
        return
    database = sqlite3.connect('/data/user_notes.db')
    table_name = f"reminders_{guild_id}"
    create_reminders_table(database, table_name)
    now = datetime.datetime.now(CET_TZ).isoformat()
    channel_id = context.channel.id
    row = (str(channel_id), None, str(creator_id), content, parsed_time.isoformat(), 0, now)
    c = database.cursor()
    c.execute(f"INSERT INTO {table_name} (channel_id, user_id, creator_id, content, target_time, sent, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", row)
    database.commit()
    rid = c.lastrowid
    formatted_date = parsed_time.strftime('%d/%m/%Y')
    formatted_time = parsed_time.strftime('%H:%M:%S')
    await reply_func(f"Reminder set by {creator_name} for {formatted_date}, {formatted_time}, CET. #Reminder ID:{rid}")
    database.close()

@commands.has_permissions(administrator=True)
async def prefix_rmdm(context, *, arg: str):
    guild_id, creator_name, reply_func, send_func, is_slash, creator_id = await get_context_handlers(context)
    if guild_id is None:
        await reply_func("This command can only be used in a server.", ephemeral=True if is_slash else False)
        return
    parsed_time, content = extract_time_and_content(arg)
    if not parsed_time or not content:
        await reply_func("Invalid format. Example: !rmdm tomorrow at 8 wake up")
        return
    if parsed_time < datetime.datetime.now(CET_TZ):
        await reply_func("Cannot set a reminder in the past.")
        return
    database = sqlite3.connect('/data/user_notes.db')
    table_name = f"reminders_{guild_id}"
    create_reminders_table(database, table_name)
    now = datetime.datetime.now(CET_TZ).isoformat()
    user_id = creator_id
    row = (None, str(user_id), str(creator_id), content, parsed_time.isoformat(), 0, now)
    c = database.cursor()
    c.execute(f"INSERT INTO {table_name} (channel_id, user_id, creator_id, content, target_time, sent, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", row)
    database.commit()
    rid = c.lastrowid
    formatted_date = parsed_time.strftime('%d/%m/%Y')
    formatted_time = parsed_time.strftime('%H:%M:%S')
    await reply_func(f"DM Reminder set by {creator_name} for {formatted_date}, {formatted_time}, CET. #Reminder ID:{rid}")
    database.close()

# +++++++++++ Regular Commands +++++++++++ #


















# Slash Command Equivalents (available to all users)

@ntr.tree.command(name="notehelp", description="Shows this help message for note commands. ❓")
async def slash_notehelp(interaction: discord.Interaction):
    await notehelp(interaction)

@ntr.tree.command(name="readnotes", description="Displays all notes for the user in a formatted embed. 📖")
@app_commands.describe(user_id="The user ID to read notes for")
async def slash_readnotes(interaction: discord.Interaction, user_id: str):
    await readnotes(interaction, user_id)

@ntr.tree.command(name="delnote", description="Deletes a specific note and shows what was deleted. 🗑️")
@app_commands.describe(note_id="The note ID to delete")
async def slash_delnote(interaction: discord.Interaction, note_id: int):
    await delnote(interaction, note_id)

@ntr.tree.command(name="clearnotes", description="Deletes all notes for the user and lists them. 🗑️🗑️")
@app_commands.describe(user_id="The user ID to clear notes for")
async def slash_clearnotes(interaction: discord.Interaction, user_id: str):
    await clearnotes(interaction, user_id)

@ntr.tree.command(name="noteadd", description="Adds a new note for the user. 🔖")
@app_commands.describe(user_id="The user ID to add a note for", note="The note content")
async def slash_noteadd(interaction: discord.Interaction, user_id: str, note: str):
    await noteadd(interaction, user_id, note=note)

note_group = app_commands.Group(name="note", description="Note management commands")
@note_group.command(name="fetchall", description="Downloads a zip archive of all server notes. 📦")
async def slash_note_fetchall(interaction: discord.Interaction):
    await note_fetchall(interaction)
ntr.tree.add_command(note_group)

@ntr.tree.command(name="rm", description="Sets a reminder to send in the channel at the specified time. ⏰")
@app_commands.describe(time_str="The time for the reminder (e.g., 'in 2 hours', 'next monday at 8')", content="The reminder message")
async def slash_rm(interaction: discord.Interaction, time_str: str, content: str):
    await set_reminder(interaction, time_str, content, False)

@ntr.tree.command(name="rmdm", description="Sets a personal DM reminder at the specified time. 📩")
@app_commands.describe(time_str="The time for the reminder (e.g., 'in 2 hours', 'next monday at 8')", content="The reminder message")
async def slash_rmdm(interaction: discord.Interaction, time_str: str, content: str):
    await set_reminder(interaction, time_str, content, True)

if __name__ == '__main__':
    ntr.run(token, reconnect=True)
