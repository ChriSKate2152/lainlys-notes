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

# Load environment variables
load_dotenv()

token = os.getenv('TOKEN')
bot_logo = os.getenv('BOT_LOGO')
staff_role_ids_str = (os.getenv('STAFF_ROLE_IDS') or '').split('#')[0].strip()
staff_role_ids = [int(id.strip()) for id in staff_role_ids_str.split(',')] if staff_role_ids_str else []


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
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        c.execute(f"UPDATE {table_name} SET created_at = ? WHERE created_at IS NULL", (now,))

    if "updated_at" not in columns:
        c.execute(f"ALTER TABLE {table_name} ADD COLUMN updated_at TEXT")
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        c.execute(f"UPDATE {table_name} SET updated_at = ? WHERE updated_at IS NULL", (now,))

    db_conn.commit()
# +++++++++++ Normal Functions +++++++++++ #













####################################################################################
#                                                                                  #
#                   Async Functions, buttons, modals, etc.                         #
#                                                                                  #
####################################################################################
async def status():
    while True:
        status_messages = ['Meta Huntering in BM', '!notehelp for help', 'Getting HoF in Manaforge Omega', 'BM Hunter rotation class']
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

    print(f'Logged in as {ntr.user} (ID: {ntr.user.id})')
    print('------')

# +++++++++++ Events +++++++++++ #













####################################################################################
#                                                                                  #
#                             Regular Commands                                     #
#                                                                                  #
####################################################################################
@ntr.command(name='help', description='Shows you what commands you can use.')
async def help_cmd(ctx: commands.Context):
    rnd_hex = random_hex_color()
    embed = discord.Embed(title='📝 Note Commands Help', colour=rnd_hex, timestamp=datetime.datetime.now(datetime.timezone.utc))
    embed.set_thumbnail(url=bot_logo)
    embed.add_field(name='!noteadd <user_id> <note>', value="Adds a new note for the user. 🔖\n*Example:* `!noteadd 123456789 Hello world`", inline=False)
    embed.add_field(name='!readnotes <user_id>', value="Displays all notes for the user in a formatted embed. 📖", inline=False)
    embed.add_field(name='!delnote <note_id>', value="Deletes a specific note and shows what was deleted. 🗑️", inline=False)
    embed.add_field(name='!clearnotes <user_id>', value="Deletes all notes for the user and lists them. 🗑️🗑️", inline=False)
    embed.add_field(name='!note fetchall', value="Downloads a zip archive of all server notes. 📦", inline=False)
    embed.add_field(name='!notehelp', value="Shows this help message for note commands. ❓", inline=False)
    await ctx.send(embed=embed)

@ntr.command(name='notehelp', description='Explains note commands.')
async def notehelp(ctx: commands.Context):
    rnd_hex = random_hex_color()
    embed = discord.Embed(title='📝 Note Commands Help', colour=rnd_hex, timestamp=datetime.datetime.now(datetime.timezone.utc))
    embed.set_thumbnail(url=bot_logo)
    embed.add_field(name='!noteadd <user_id> <note>', value="Adds a new note for the user. 🔖\n*Example:* `!noteadd 123456789 Hello world`", inline=False)
    embed.add_field(name='!readnotes <user_id>', value="Displays all notes for the user in a formatted embed. 📖", inline=False)
    embed.add_field(name='!delnote <note_id>', value="Deletes a specific note and shows what was deleted. 🗑️", inline=False)
    embed.add_field(name='!clearnotes <user_id>', value="Deletes all notes for the user and lists them. 🗑️🗑️", inline=False)
    embed.add_field(name='!note fetchall', value="Downloads a zip archive of all server notes. 📦", inline=False)
    embed.add_field(name='!notehelp', value="Shows this help message for note commands. ❓", inline=False)
    await ctx.send(embed=embed)

@ntr.command(name='ping', description='Test to see if the bot is responsive.')
async def ping(ctx: commands.Context):
    await ctx.send(f"⏱️ Pong! ⏱️\nConnection speed is {round(ntr.latency * 1000)}ms")

@ntr.command(name='readnotes')
async def readnotes(ctx: commands.Context, user_id: str):
    if not any(role.id in staff_role_ids for role in ctx.author.roles):
        await ctx.reply("You don't have permission to use this command.", delete_after=10)
        return

    database = sqlite3.connect('user_notes.db')
    c = database.cursor()
    guild_id = ctx.guild.id
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
        await ctx.reply(f"\"{username}\" has no notes.")
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
        parsed_dt = datetime.datetime.fromisoformat(dt)
        formatted_dt = parsed_dt.strftime('%d/%m/%Y %H:%M:%S | UTC')
        note_texts.append(f"**Note #{note_id}**\nFrom: \"{creator}\"\nLast Update: {formatted_dt}\n{content}")

    full_text = "\n---\n".join(note_texts)

    rnd_hex = random_hex_color()
    embed = discord.Embed(title=f"Notes for \"{username}\"", description=full_text, colour=rnd_hex, timestamp=datetime.datetime.now(datetime.timezone.utc))
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    await ctx.send(embed=embed)
    database.close()

@ntr.command(name='delnote')
async def delnote(ctx: commands.Context, note_id: int):
    if not any(role.id in staff_role_ids for role in ctx.author.roles):
        await ctx.reply("You don't have permission to use this command.", delete_after=10)
        return

    database = sqlite3.connect('user_notes.db')
    c = database.cursor()
    guild_id = ctx.guild.id
    table_name = f"guild_{guild_id}"

    create_table(database, table_name)

    c.execute(f"SELECT row, creator_name, updated_at, note FROM {table_name} WHERE row = ?", (note_id,))
    existing_row = c.fetchone()

    if not existing_row:
        await ctx.reply(f"No note found with ID {note_id}.")
    else:
        note_id, creator, dt, content = existing_row
        parsed_dt = datetime.datetime.fromisoformat(dt)
        formatted_dt = parsed_dt.strftime('%d/%m/%Y %H:%M:%S | UTC')
        note_text = f"**Note #{note_id}**\nFrom: \"{creator}\"\nLast Update: {formatted_dt}\n{content}"
        c.execute(f"DELETE FROM {table_name} WHERE row = ?", (note_id,))
        database.commit()
        await ctx.reply(f"Deleted the following note:\n{note_text}")

    database.close()

@ntr.command(name='clearnotes')
async def clearnotes(ctx: commands.Context, user_id: str):
    if not any(role.id in staff_role_ids for role in ctx.author.roles):
        await ctx.reply("You don't have permission to use this command.", delete_after=10)
        return

    database = sqlite3.connect('user_notes.db')
    c = database.cursor()
    guild_id = ctx.guild.id
    table_name = f"guild_{guild_id}"

    create_table(database, table_name)

    user_id = re.sub(r'[<@!>]', '', user_id)

    c.execute(f"SELECT row, creator_name, updated_at, note FROM {table_name} WHERE user_id = ?", (user_id,))
    rows = c.fetchall()

    if not rows:
        await ctx.reply(f"No notes found for the user with ID {user_id}.")
        database.close()
        return

    note_texts = []
    for r in rows:
        note_id, creator, dt, content = r
        parsed_dt = datetime.datetime.fromisoformat(dt)
        formatted_dt = parsed_dt.strftime('%d/%m/%Y %H:%M:%S | UTC')
        note_texts.append(f"**Note #{note_id}**\nFrom: \"{creator}\"\nLast Update: {formatted_dt}\n{content}")

    full_text = "\n---\n".join(note_texts)

    c.execute(f"DELETE FROM {table_name} WHERE user_id = ?", (user_id,))
    database.commit()

    await ctx.reply(f"Deleted the following notes:\n{full_text}")
    database.close()

@ntr.group(name="note", invoke_without_command=True)
async def note(ctx: commands.Context):
    await ctx.reply("Available subcommands: fetchall")

@ntr.command(name="noteadd", description="Adds a note about a user.")
async def noteadd(ctx: commands.Context, user_id: str, *, note: str):
    if not any(role.id in staff_role_ids for role in ctx.author.roles):
        await ctx.reply("You don't have permission to use this command.", delete_after=10)
        return

    database = sqlite3.connect('user_notes.db')
    c = database.cursor()
    guild_id = ctx.guild.id
    table_name = f"guild_{guild_id}"

    create_table(database, table_name)

    user_id = re.sub(r'[<@!>]', '', user_id)

    try:
        user = await ntr.fetch_user(int(user_id))
    except:
        await ctx.reply("Invalid user ID.")
        database.close()
        return

    user_name = f"@{user.name}"
    creator_name = ctx.author.name
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    row = (user_id, user_name, note, creator_name, now, now)
    c.execute(f"INSERT INTO {table_name} (user_id, user_name, note, creator_name, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)", row)
    database.commit()
    note_id = c.lastrowid
    await ctx.reply(f"✅ Note Taken. Note: {note} (ID: {note_id})")
    database.close()

@note.command(name="fetchall", description="Fetches all user notes.")
async def note_fetchall(ctx: commands.Context):
    if not any(role.id in staff_role_ids for role in ctx.author.roles):
        await ctx.reply("You don't have permission to use this command.", delete_after=10)
        return

    database = sqlite3.connect('user_notes.db')
    c = database.cursor()
    guild_id = ctx.guild.id
    table_name = f"guild_{guild_id}"

    create_table(database, table_name)
    c.execute(f"SELECT * FROM {table_name}")
    rows = c.fetchall()
    database.close()

    if rows:
        items = [str(row) for row in rows]
        with open('output.txt', 'w') as f:
            f.write('\n'.join(items))

        with zipfile.ZipFile('user_db_notes.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write('output.txt')

        os.remove("output.txt")
        await ctx.send("DB logs here - Expires in 1min", view=dl_button(), delete_after=60)
    else:
        await ctx.reply("Database is empty - No notes available to fetch.")

# ntr.add_command(note_group)  # No longer needed with decorator

# +++++++++++ Regular Commands +++++++++++ #


















if __name__ == '__main__':
    ntr.run(token, reconnect=True)
