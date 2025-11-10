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

# Configure logging to ensure messages appear in Docker logs
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s', force=True)
logger = logging.getLogger(__name__)

token = os.getenv('TOKEN')
bot_logo = os.getenv('BOT_LOGO')

hex_red=0xFF0000
hex_green=0x0AC700
hex_yellow=0xFFF000 # I also like -> 0xf4c50b

# +++++++++++ Imports and definitions +++++++++++ #

def maybe_allowed_contexts(**kwargs):
    """
    Returns a decorator that applies app_commands.allowed_contexts if available in this discord.py version,
    otherwise returns a no-op decorator for compatibility.
    """
    if hasattr(app_commands, "allowed_contexts"):
        return app_commands.allowed_contexts(**kwargs)
    def _noop_decorator(func):
        return func
    return _noop_decorator

def maybe_allowed_installs(**kwargs):
    """
    Returns a decorator that applies app_commands.allowed_installs if available in this discord.py version,
    otherwise returns a no-op decorator for compatibility.
    """
    if hasattr(app_commands, "allowed_installs"):
        return app_commands.allowed_installs(**kwargs)
    def _noop_decorator(func):
        return func
    return _noop_decorator













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
    is_time_only = re.match(r'^\d{1,2}(:\d{2})?$', time_str)
    if is_time_only:
        time_str = f"at {time_str}"
    parsed = dateparser.parse(time_str, settings={'TIMEZONE': 'CET', 'RETURN_AS_TIMEZONE_AWARE': True, 'PREFER_DATES_FROM': 'future'})
    if parsed is None:
        return None
    if is_time_only and parsed.date() == now.date() and parsed < now:
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
            target_time REAL,
            sent INTEGER DEFAULT 0,
            created_at TEXT
        );
    """)
    # Migration for existing data
    try:
        c.execute(f"ALTER TABLE {table_name} RENAME COLUMN target_time TO target_time_old")
        c.execute(f"ALTER TABLE {table_name} ADD COLUMN target_time REAL")
        c.execute(f"UPDATE {table_name} SET target_time = CAST(strftime('%s', target_time_old) AS REAL)")
        c.execute(f"DROP COLUMN target_time_old")
    except sqlite3.OperationalError:
        pass  # If column doesn't exist or already migrated
    db_conn.commit()

# Add helper functions
def create_error_embed(message):
    embed = discord.Embed(title="Error", description=message, color=0xA020F0, timestamp=datetime.datetime.now(CET_TZ))
    embed.set_footer(text="Lainly's Notes")
    return embed

def create_success_embed(title, description, fields=None):
    embed = discord.Embed(title=title, description=description, color=0xA020F0, timestamp=datetime.datetime.now(CET_TZ))
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
    embed.set_footer(text="Lainly's Notes")
    return embed

# +++++++++++ Normal Functions +++++++++++ #













####################################################################################
#                                                                                  #
#                   Async Functions, buttons, modals, etc.                         #
#                                                                                  #
####################################################################################
async def status():
    while True:
        status_messages = ['Meta Huntering in BM', 'Getting HoF in Manaforge Omega', 'BM Hunter Masterclass']
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
        now_unix = time.time()
        for table in tables:
            c.execute(f"SELECT id, channel_id, user_id, creator_id, content, target_time FROM {table} WHERE sent = 0")
            for rid, channel_id, user_id, creator_id, content, target_time in c.fetchall():
                if target_time is None:
                    continue
                try:
                    if isinstance(target_time, str):
                        dt = datetime.datetime.fromisoformat(target_time)
                        if dt.tzinfo is None:
                            dt = CET_TZ.localize(dt)
                        target_unix = dt.astimezone(pytz.utc).timestamp()
                    else:
                        target_unix = float(target_time)
                except Exception as e:
                    print(f"Error converting target_time {target_time} for rid {rid}: {e}")
                    continue
                if target_unix is not None and target_unix <= now_unix:
                    try:
                        creator = await ntr.fetch_user(int(creator_id))
                        creator_name = creator.name
                    except:
                        creator_name = f"User {creator_id}"
                    try:
                        if channel_id is not None:
                            channel = ntr.get_channel(int(channel_id))
                            if channel:
                                embed = discord.Embed(title="🔔🔔🔔 Reminder!", description=content, color=0xA020F0, timestamp=datetime.datetime.now(CET_TZ))
                                embed.add_field(name="Requested by", value=f"{creator_name} (<@{creator_id}>)", inline=False)
                                embed.set_footer(text="Lainly's Notes")
                                await channel.send(embed=embed)
                        elif user_id is not None:
                            user = await ntr.fetch_user(int(user_id))
                            if user:
                                embed = discord.Embed(title="🔔🔔🔔 Reminder!", description=content, color=0xA020F0, timestamp=datetime.datetime.now(CET_TZ))
                                embed.set_footer(text="Lainly's Notes")
                                await user.send(embed=embed)
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

    print(f'[READY] Logged in as {ntr.user} (ID: {ntr.user.id})')
    print(f'[READY] Message Content Intent: {ntr.intents.message_content}')
    print(f'[READY] Members Intent: {ntr.intents.members}')
    print('------')
    logger.info(f"Logged in as {ntr.user} (ID: {ntr.user.id})")
    logger.info(f"Message Content Intent: {ntr.intents.message_content}")
    logger.info(f"Members Intent: {ntr.intents.members}")
    await ntr.tree.sync()  # Sync slash commands
    print('[READY] Slash commands synced')

@ntr.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(embed=create_error_embed("You must be an administrator to use this command. Use the / version instead."), delete_after=10)
    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignore unknown commands
    else:
        print(f"[ERROR] Command error in {ctx.command}: {error}")
        import traceback
        traceback.print_exc()
        await ctx.send(embed=create_error_embed(f"An error occurred: {str(error)}"), delete_after=10)

@ntr.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    await interaction.response.send_message(embed=create_error_embed(f"An error occurred: {str(error)}"), ephemeral=True)

@ntr.event
async def on_message(message):
    if message.author == ntr.user:
        return
    if message.content.startswith('!'):
        print(f"[DEBUG] Message received: {message.content}")
        logger.info(f"Prefix message detected: {message.content}")
    await ntr.process_commands(message)

@ntr.event
async def on_command_completion(ctx):
    try:
        cmd_name = ctx.command.qualified_name if ctx.command else 'unknown'
        where = 'DM' if ctx.guild is None else f'Guild:{ctx.guild.id}'
        print(f"[DEBUG] Prefix command completed: {cmd_name} | Location: {where}")
        logger.info(f"Prefix command completed: {cmd_name} | Location: {where}")
    except Exception as e:
        print(f"[DEBUG] on_command_completion logging failed: {e}")
        logger.info(f"on_command_completion logging failed: {e}")

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
    embed = discord.Embed(title='**🔑 Commands Index**', colour=0xA020F0, timestamp=datetime.datetime.now(CET_TZ))
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
**📋・{prefix}rmlist**
Lists your upcoming reminders across all servers and lets you delete one by replying with its number. If used in a server channel, the list is sent to you via DM and the original request is acknowledged with a ✅ reaction.
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
        await reply_func(embed=create_error_embed("This command can only be used in a server."), ephemeral=True if is_slash else False)
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
        await reply_func(embed=create_error_embed(f"\"{username}\" has no notes."))
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
        formatted_dt = parsed_dt.strftime('%H:%M %d/%m/%Y CET')
        note_texts.append(f"**Note #{note_id}**\nFrom: \"{creator}\"\nLast Update: {formatted_dt}\n{content}")

    full_text = "\n---\n".join(note_texts)

    embed = discord.Embed(title=f"Notes for \"{username}\"", description=full_text, colour=0xA020F0, timestamp=datetime.datetime.now(CET_TZ))
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    embed.set_footer(text="Lainly's Notes")
    await send_func(embed=embed)
    database.close()

@ntr.command(name='delnote')
@commands.has_permissions(administrator=True)
async def delnote(context, note_id: int):
    guild_id, creator_name, reply_func, send_func, is_slash, creator_id = await get_context_handlers(context)
    if guild_id is None:
        await reply_func(embed=create_error_embed("This command can only be used in a server."), ephemeral=True if is_slash else False)
        return

    database = sqlite3.connect('/data/user_notes.db')
    c = database.cursor()
    table_name = f"guild_{guild_id}"

    create_table(database, table_name)

    c.execute(f"SELECT row, creator_name, updated_at, note FROM {table_name} WHERE row = ?", (note_id,))
    existing_row = c.fetchone()

    if not existing_row:
        await reply_func(embed=create_error_embed(f"No note found with ID {note_id}."))
    else:
        note_id, creator, dt, content = existing_row
        parsed_dt = datetime.datetime.fromisoformat(dt).astimezone(CET_TZ)
        formatted_dt = parsed_dt.strftime('%H:%M %d/%m/%Y CET')
        note_text = f"**Note #{note_id}**\nFrom: \"{creator}\"\nLast Update: {formatted_dt}\n{content}"
        c.execute(f"DELETE FROM {table_name} WHERE row = ?", (note_id,))
        database.commit()
        await reply_func(embed=create_success_embed("Note Deleted", note_text))

    database.close()

@ntr.command(name='clearnotes')
@commands.has_permissions(administrator=True)
async def clearnotes(context, user_id: str):
    guild_id, creator_name, reply_func, send_func, is_slash, creator_id = await get_context_handlers(context)
    if guild_id is None:
        await reply_func(embed=create_error_embed("This command can only be used in a server."), ephemeral=True if is_slash else False)
        return

    database = sqlite3.connect('/data/user_notes.db')
    c = database.cursor()
    table_name = f"guild_{guild_id}"

    create_table(database, table_name)

    user_id = re.sub(r'[<@!>]', '', user_id)

    c.execute(f"SELECT row, creator_name, updated_at, note FROM {table_name} WHERE user_id = ?", (user_id,))
    rows = c.fetchall()

    if not rows:
        await reply_func(embed=create_error_embed(f"No notes found for the user with ID {user_id}."))
        database.close()
        return

    note_texts = []
    for r in rows:
        note_id, creator, dt, content = r
        parsed_dt = datetime.datetime.fromisoformat(dt).astimezone(CET_TZ)
        formatted_dt = parsed_dt.strftime('%H:%M %d/%m/%Y CET')
        note_texts.append(f"**Note #{note_id}**\nFrom: \"{creator}\"\nLast Update: {formatted_dt}\n{content}")

    full_text = "\n---\n".join(note_texts)

    c.execute(f"DELETE FROM {table_name} WHERE user_id = ?", (user_id,))
    database.commit()

    await reply_func(embed=create_success_embed("Notes Cleared", full_text))
    database.close()

@ntr.group(name="note", invoke_without_command=True)
@commands.has_permissions(administrator=True)
async def note(context):
    guild_id, creator_name, reply_func, send_func, is_slash, creator_id = await get_context_handlers(context)
    await reply_func(embed=create_error_embed("Available subcommands: fetchall"))

@ntr.command(name="noteadd", description="Adds a note about a user.")
@commands.has_permissions(administrator=True)
async def noteadd(context, user_id: str, *, note: str):
    guild_id, creator_name, reply_func, send_func, is_slash, creator_id = await get_context_handlers(context)
    if guild_id is None:
        await reply_func(embed=create_error_embed("This command can only be used in a server."), ephemeral=True if is_slash else False)
        return

    database = sqlite3.connect('/data/user_notes.db')
    c = database.cursor()
    table_name = f"guild_{guild_id}"

    create_table(database, table_name)

    user_id = re.sub(r'[<@!>]', '', user_id)

    try:
        user = await ntr.fetch_user(int(user_id))
    except:
        await reply_func(embed=create_error_embed("Invalid user ID."))
        database.close()
        return

    user_name = f"@{user.name}"
    now = datetime.datetime.now(CET_TZ).isoformat()
    row = (user_id, user_name, note, creator_name, now, now)
    c.execute(f"INSERT INTO {table_name} (user_id, user_name, note, creator_name, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)", row)
    database.commit()
    note_id = c.lastrowid
    embed = discord.Embed(
        title="Note Added",
        description=f"Note added for <@{user_id}> by {creator_name}.\n\n**Note ID:** {note_id}\n**Content:** {note}",
        colour=0xA020F0,
        timestamp=datetime.datetime.now(CET_TZ)
    )
    if user.avatar:
        embed.set_thumbnail(url=user.avatar.url)
    embed.set_footer(text="Lainly's Notes")
    await reply_func(embed=embed)
    database.close()

@note.command(name="fetchall", description="Fetches all user notes.")
@commands.has_permissions(administrator=True)
async def note_fetchall(context):
    guild_id, creator_name, reply_func, send_func, is_slash, creator_id = await get_context_handlers(context)
    if guild_id is None:
        await reply_func(embed=create_error_embed("This command can only be used in a server."), ephemeral=True if is_slash else False)
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
            await send_func(embed=create_success_embed("Notes Archive", "DB logs here - Expires in 1min"), view=dl_button(), delete_after=60 if not is_slash else None)
        else:
            await send_func(embed=create_success_embed("Notes Archive", "DB logs here - Expires in 1min"), view=dl_button(), delete_after=60)
    else:
        await reply_func(embed=create_error_embed("Database is empty - No notes available to fetch."))

# +++++++++++ Regular Commands +++++++++++ #

async def set_reminder(context, time_str: str, content: str, is_dm: bool):
    guild_id, creator_name, reply_func, send_func, is_slash, creator_id = await get_context_handlers(context)
    parsed_time = parse_time(time_str)
    if parsed_time is None:
        await reply_func(embed=create_error_embed("Invalid time format. Examples: 'in 2 hours', 'tomorrow at 8', 'next monday at 20:00'"))
        return
    if parsed_time < datetime.datetime.now(CET_TZ):
        await reply_func(embed=create_error_embed("Cannot set a reminder in the past."))
        return
    database = sqlite3.connect('/data/user_notes.db')
    table_name = f"reminders_{guild_id if guild_id else 'dm'}"
    create_reminders_table(database, table_name)
    now = datetime.datetime.now(CET_TZ).isoformat()
    channel_id = context.channel.id if isinstance(context, commands.Context) else context.channel_id
    user_id = creator_id if is_dm else None
    channel_id = channel_id if not is_dm else None
    if guild_id is None and channel_id is not None:
        channel_id = None
        user_id = creator_id  # Treat rm as rmdm in DM
    row = (str(channel_id) if channel_id else None, str(user_id) if user_id else None, str(creator_id), content, parsed_time.timestamp(), 0, now)
    c = database.cursor()
    c.execute(f"INSERT INTO {table_name} (channel_id, user_id, creator_id, content, target_time, sent, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", row)
    database.commit()
    rid = c.lastrowid
    display_time = parsed_time.astimezone(CET_TZ)
    formatted_dt = display_time.strftime('%H:%M %d/%m/%Y CET')
    created_dt = datetime.datetime.fromisoformat(now).astimezone(CET_TZ)
    formatted_created = created_dt.strftime('%H:%M %d/%m/%Y CET')
    fields = [
        ("Set by", creator_name, True),
        ("Reminder Time", f"{formatted_dt}", True),
        ("Reminder ID", str(rid), True),
        ("Content", content, False),
        ("Created At", f"{formatted_created}", True)
    ]
    embed = create_success_embed(":bell: Reminder Set" if not is_dm else ":bell: Personal Reminder Set", "", fields)
    if is_dm:
        # Unified confirmation reply for DM reminders (slash or prefix)
        display_time = parsed_time.astimezone(CET_TZ)
        formatted_dt = display_time.strftime('%H:%M %d/%m/%Y')
        confirm_text = f"🔔 Reminder set for {formatted_dt} CET, I will DM you then!"
        await reply_func(content=confirm_text)
    else:
        await reply_func(embed=embed)
    database.close()

def extract_time_and_content(arg):
    import re
    text = arg.strip()
    if not text:
        return None, None
    # Prefer quoted content first: "... 'your content'" or "... \"your content\""
    quote_match = re.search(r'(["\'])(.+?)\1', text)
    if quote_match:
        content = quote_match.group(2).strip()
        time_part = (text[:quote_match.start()] + text[quote_match.end():]).strip()
        parsed = parse_time(time_part)
        if parsed:
            return parsed, content
    # Tokenize and try to find a reasonable split between time and content
    words = text.split()
    if len(words) < 2:
        return None, None
    unit_re = r'(second|minute|hour|day|week|month|year)s?'
    is_num = lambda w: re.fullmatch(r'\d+', w) is not None
    is_unit = lambda w: re.fullmatch(unit_re, w, re.I) is not None
    has_in_num_unit = lambda s: re.search(rf'\bin\s+\d+\s+{unit_re}\b', s, re.I) is not None
    duration_line_re = re.compile(rf'^\d+\s+{unit_re}(?:\s+(?:and\s+)?\d+\s+{unit_re})*$', re.I)
    # Scan from the beginning, taking the shortest valid time that still "looks right".
    last_good_idx = None
    last_good_dt = None
    for i in range(1, len(words)):  # split before i (time), after i (content)
        time_candidate = ' '.join(words[:i])
        parsed = parse_time(time_candidate)
        if not parsed and duration_line_re.match(time_candidate):
            parsed = parse_time("in " + time_candidate)
        if parsed:
            last_good_idx = i
            last_good_dt = parsed
            # Heuristic: if we already have an "in N unit" and the next tokens begin with another "N unit",
            # stop here to avoid eating content that repeats a duration (e.g., "in 4 days 4 days have passed").
            if i + 1 < len(words) and has_in_num_unit(time_candidate):
                if is_num(words[i]) and is_unit(words[i + 1]):
                    break
            # Otherwise, continue to see if adding more tokens still makes for a better time phrase (e.g., "tomorrow at 8").
    if last_good_idx is not None and last_good_idx < len(words):
        content = ' '.join(words[last_good_idx:]).strip().strip('\'"').strip()
        return last_good_dt, content if content else None
    return None, None

@ntr.command(name='rm')
@commands.has_permissions(administrator=True)
async def prefix_rm(context, *, arg: str):
    guild_id, creator_name, reply_func, send_func, is_slash, creator_id = await get_context_handlers(context)
    if guild_id is not None:
        member = context.guild.get_member(context.author.id)
        if not member.guild_permissions.administrator:
            await reply_func(embed=create_error_embed("You must be an administrator to use this command. Use the / version instead."))
            return
    parsed_time, content = extract_time_and_content(arg)
    if not parsed_time or not content:
        await reply_func(embed=create_error_embed("Invalid format. Example: !rm in 2 hours reminder message"))
        return
    if parsed_time < datetime.datetime.now(CET_TZ):
        await reply_func(embed=create_error_embed("Cannot set a reminder in the past."))
        return
    database = sqlite3.connect('/data/user_notes.db')
    table_name = f"reminders_{guild_id if guild_id else 'dm'}"
    create_reminders_table(database, table_name)
    now = datetime.datetime.now(CET_TZ).isoformat()
    channel_id = context.channel.id
    if guild_id is None:
        channel_id = None
    row = (str(channel_id) if channel_id else None, None if channel_id else str(creator_id), str(creator_id), content, parsed_time.timestamp(), 0, now)
    c = database.cursor()
    c.execute(f"INSERT INTO {table_name} (channel_id, user_id, creator_id, content, target_time, sent, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", row)
    database.commit()
    rid = c.lastrowid
    display_time = datetime.datetime.fromtimestamp(parsed_time.timestamp(), CET_TZ)
    formatted_dt = display_time.strftime('%H:%M %d/%m/%Y CET')
    formatted_created = datetime.datetime.fromisoformat(now).astimezone(CET_TZ).strftime('%H:%M %d/%m/%Y CET')
    fields = [
        ("Set by", creator_name, True),
        ("Reminder Time", f"{formatted_dt}", True),
        ("Reminder ID", str(rid), True),
        ("Content", content, False),
        ("Created At", f"{formatted_created}", True)
    ]
    embed = create_success_embed(":bell: Reminder Set", "", fields)
    await reply_func(embed=embed)
    database.close()

@ntr.command(name='rmdm')
@commands.has_permissions(administrator=True)
async def prefix_rmdm(context, *, arg: str):
    print(f"[DEBUG] prefix_rmdm called with arg: {arg}")
    guild_id, creator_name, reply_func, send_func, is_slash, creator_id = await get_context_handlers(context)
    print(f"[DEBUG] guild_id: {guild_id}, creator_name: {creator_name}, is_slash: {is_slash}")
    if guild_id is not None:
        member = context.guild.get_member(context.author.id)
        if not member.guild_permissions.administrator:
            await reply_func(embed=create_error_embed("You must be an administrator to use this command. Use the / version instead."))
            return
    parsed_time, content = extract_time_and_content(arg)
    if not parsed_time or not content:
        await reply_func(embed=create_error_embed("Invalid format. Example: !rmdm tomorrow at 8 wake up"))
        return
    if parsed_time < datetime.datetime.now(CET_TZ):
        await reply_func(embed=create_error_embed("Cannot set a reminder in the past."))
        return
    database = sqlite3.connect('/data/user_notes.db')
    table_name = f"reminders_{guild_id if guild_id else 'dm'}"
    create_reminders_table(database, table_name)
    now = datetime.datetime.now(CET_TZ).isoformat()
    user_id = creator_id
    row = (None, str(user_id), str(creator_id), content, parsed_time.timestamp(), 0, now)
    c = database.cursor()
    c.execute(f"INSERT INTO {table_name} (channel_id, user_id, creator_id, content, target_time, sent, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", row)
    database.commit()
    rid = c.lastrowid
    # Send creation-time confirmation as a simple reply where invoked
    try:
        display_time = datetime.datetime.fromtimestamp(parsed_time.timestamp(), CET_TZ)
        formatted_dt = display_time.strftime('%H:%M %d/%m/%Y')
        confirm_text = f"🔔 Reminder set for {formatted_dt} CET, I will DM you then!"
        await reply_func(content=confirm_text)
    except Exception as e:
        print(f"[DEBUG] Failed to send confirmation in prefix rmdm: {e}")
    # Also react to the original command message (prefix only)
    if isinstance(context, commands.Context):
        try:
            await context.message.add_reaction("✅")
        except Exception as e:
            print(f"[DEBUG] Failed to add reaction in prefix rmdm: {e}")
    database.close()

# +++++++++++ Regular Commands +++++++++++ #

async def list_and_handle_reminders(context, force_dm: bool = False):
    guild_id, creator_name, reply_func, send_func, is_slash, creator_id = await get_context_handlers(context)
    dm_channel = None
    if force_dm:
        # Override reply target to user's DM
        try:
            user_obj = context.author if isinstance(context, commands.Context) else context.user
            dm_channel = await user_obj.create_dm()
            async def dm_reply_func(content=None, **kwargs):
                return await dm_channel.send(content, **kwargs)
            reply_func = dm_reply_func
        except Exception as e:
            # Bubble up so caller can notify user appropriately
            raise
    now_unix = time.time()
    database = sqlite3.connect('/data/user_notes.db')
    c = database.cursor()
    # Discover all reminder tables to aggregate across all servers and DMs
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'reminders_%'")
    reminder_tables = [row[0] for row in c.fetchall()]
    items = []  # (table_name, rid, content, target_unix)
    for table_name in reminder_tables:
        create_reminders_table(database, table_name)
        c.execute(f"SELECT id, content, target_time FROM {table_name} WHERE sent = 0 AND creator_id = ?", (str(creator_id),))
        rows = c.fetchall()
        for rid, content, target_time in rows:
            try:
                if isinstance(target_time, str):
                    try:
                        target_unix = float(target_time)
                    except:
                        dt = datetime.datetime.fromisoformat(target_time)
                        if dt.tzinfo is None:
                            dt = CET_TZ.localize(dt)
                        target_unix = dt.astimezone(pytz.utc).timestamp()
                else:
                    target_unix = float(target_time)
            except Exception:
                continue
            if target_unix > now_unix:
                items.append((table_name, rid, content, target_unix))
    # Sort by time ascending
    items.sort(key=lambda x: x[3])
    if not items:
        embed = discord.Embed(
            title="⏰ Your Upcoming Reminders",
            description="You have no upcoming reminders.\n\nTip: Create one with `/rm` or `!rm`.",
            colour=0xA020F0,
            timestamp=datetime.datetime.now(CET_TZ)
        )
        try:
            user_obj = context.author if isinstance(context, commands.Context) else context.user
            if getattr(user_obj, "avatar", None):
                thumb = user_obj.avatar.url if hasattr(user_obj.avatar, "url") else user_obj.avatar
                embed.set_thumbnail(url=thumb)
        except Exception:
            pass
        embed.set_footer(text="Lainly's Notes 🏹")
        await reply_func(embed=embed)
        database.close()
        return
    # Build numbered list
    lines = []
    for idx, (_, _, content, target_unix) in enumerate(items, start=1):
        display_time = datetime.datetime.fromtimestamp(target_unix, CET_TZ)
        formatted_dt = display_time.strftime('%H:%M %d/%m/%Y')
        prefix = f"{idx}. "
        indent = " " * len(prefix)
        lines.append(f"{prefix}Reminder: {content}\n{indent}Scheduled for: {formatted_dt} CET")
    desc = "\n\n".join(lines) + "\n\nReply with the number of a reminder here to delete it."
    list_embed = discord.Embed(
        title="⏰ Your Upcoming Reminders",
        description=desc,
        colour=0xA020F0,
        timestamp=datetime.datetime.now(CET_TZ)
    )
    try:
        user_obj = context.author if isinstance(context, commands.Context) else context.user
        if getattr(user_obj, "avatar", None):
            thumb = user_obj.avatar.url if hasattr(user_obj.avatar, "url") else user_obj.avatar
            list_embed.set_thumbnail(url=thumb)
    except Exception:
        pass
    list_embed.set_footer(text="Lainly's Notes 🏹")
    await reply_func(embed=list_embed)
    # Wait for a numeric reply from the same user in the same channel/DM
    # Determine the channel to listen in
    desired_channel_id = None
    if force_dm and dm_channel is not None:
        desired_channel_id = dm_channel.id
    else:
        desired_channel_id = context.channel.id if isinstance(context, commands.Context) else context.channel_id
    def check(msg: discord.Message):
        try:
            # Same author only
            if msg.author.id != creator_id:
                return False
            # Same channel (works for DMs and guild channels)
            if msg.channel.id != desired_channel_id:
                return False
            # Content is a valid number in range
            num = int(msg.content.strip())
            return 1 <= num <= len(items)
        except Exception:
            return False
    try:
        reply_msg: discord.Message = await ntr.wait_for('message', check=check, timeout=60)
        index = int(reply_msg.content.strip())
    except asyncio.TimeoutError:
        database.close()
        return
    # Resolve and delete selected reminder
    selected_table, selected_rid, selected_content, selected_unix = items[index - 1]
    c.execute(f"DELETE FROM {selected_table} WHERE id = ?", (selected_rid,))
    database.commit()
    display_time = datetime.datetime.fromtimestamp(selected_unix, CET_TZ)
    formatted_dt = display_time.strftime('%H:%M %d/%m/%Y')
    confirm_embed = discord.Embed(
        title=f"🗑️ Reminder Deleted",
        description=f"**Reminder:**\n> {selected_content}\n\n**Scheduled:** {formatted_dt} CET\n\n✅ This reminder has been deleted.",
        colour=0xA020F0,
        timestamp=datetime.datetime.now(CET_TZ)
    )
    confirm_embed.set_footer(text="Lainly's Notes 🏹")
    await reply_func(embed=confirm_embed)
    database.close()

@ntr.command(name='rmlist')
async def prefix_rmlist(context):
    # If used in a guild/channel, react and DM the flow to the user
    if context.guild is not None:
        # React to the invoking message
        if isinstance(context, commands.Context):
            try:
                await context.message.add_reaction("✅")
            except Exception as e:
                print(f"[DEBUG] Failed to add reaction in prefix rmlist: {e}")
        try:
            await list_and_handle_reminders(context, force_dm=True)
        except Exception as e:
            try:
                await context.reply(embed=create_error_embed("I couldn't DM you. Please enable DMs from server members and try again."))
            except Exception as ie:
                print(f"[DEBUG] Failed to notify in channel for rmlist DM failure: {ie}")
        return
    await list_and_handle_reminders(context)

















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

@maybe_allowed_contexts(guilds=True, dms=True, private_channels=False)
@maybe_allowed_installs(guilds=True, users=True)
@ntr.tree.command(name="rmlist", description="Lists your upcoming reminders and lets you delete one. 📋")
async def slash_rmlist(interaction: discord.Interaction):
    # If invoked in a guild, DM the flow and show an ephemeral acknowledgment
    if interaction.guild_id is not None:
        # Respond immediately to avoid "application did not respond"
        if not interaction.response.is_done():
            try:
                await interaction.response.send_message(content="✅ Check your DMs for your reminders list.", ephemeral=True)
            except Exception as e:
                print(f"[DEBUG] Failed to send initial ephemeral ack for /rmlist: {e}")
        else:
            try:
                await interaction.followup.send(content="✅ Check your DMs for your reminders list.", ephemeral=True)
            except Exception as e:
                print(f"[DEBUG] Failed to send followup ephemeral ack for /rmlist: {e}")
        # Now run the DM flow
        try:
            await list_and_handle_reminders(interaction, force_dm=True)
        except Exception as e:
            err_embed = create_error_embed("I couldn't DM you. Please enable DMs from server members and try again.")
            if not interaction.response.is_done():
                try:
                    await interaction.response.send_message(embed=err_embed, ephemeral=True)
                except Exception as ie:
                    print(f"[DEBUG] Failed to send error response for /rmlist: {ie}")
            else:
                try:
                    await interaction.followup.send(embed=err_embed, ephemeral=True)
                except Exception as ie:
                    print(f"[DEBUG] Failed to send error followup for /rmlist: {ie}")
        return
    await list_and_handle_reminders(interaction)

if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(line_buffering=True)  # Force unbuffered output for Docker logs
    print("[STARTUP] Bot starting...")
    ntr.run(token, reconnect=True)
