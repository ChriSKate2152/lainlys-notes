# Lainlys-notes

A comprehensive Discord bot for managing user notes in servers. This bot allows server administrators and moderators to keep track of important information about users, such as warnings, reminders, or custom details. It supports multiple notes per user, with features like adding, reading, deleting specific notes or all notes for a user, and exporting notes as a CSV archive. Notes include metadata like creator, creation time, and last update time.

The bot distinguishes between prefix commands (!commands) restricted to server administrators and slash commands (/commands) available to all users, with access controllable via Discord's permission system. This makes it flexible for different server setups.

This bot is based on Noter from https://github.com/therealOri/noter.git with multiple improvements implemented such as:
* Added support for multi-notes per UserID
* Added command to delete a single note or all notes per UserID
* Adjusted bot to work with Discord 2.3.2 api requirements
* Enhanced export functionality to CSV with dynamic filenames
* Docker support with volume mounting for data persistence

Credit: therealOri | https://github.com/therealOri

## Installation

1. Ensure you have Python 3.11+ installed.

2. Clone the repository:
   ```bash
   git clone https://github.com/ChriSKate2152/lainlys-notes.git
   cd lainlys-notes
   ```

3. Create and activate a virtual environment:
   ```bash
   python3 -m venv ntrENV
   source ntrENV/bin/activate  # On Linux/Mac
   # or on Windows: ntrENV\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the project root (copy from `.env.example` if available, or create manually):
   ```
   TOKEN=your-discord-bot-token
   BOT_LOGO=https://example.com/your-logo.png  # Optional: URL to bot's logo for embeds
   ```

6. Run the bot:
   ```bash
   python noter.py
   ```
   The bot will start and sync slash commands on ready. Notes are stored in `user_notes.db` (or `/data/user_notes.db` in Docker).

## Docker Deployment

1. Ensure Docker is installed on your system.

2. Build the Docker image:
   ```bash
   docker build -t noter-bot .
   ```

3. Run the container, passing environment variables (recommended for security instead of copying .env) and mounting a volume for data persistence:
   ```bash
   docker run -d --name noter-bot \
     -e TOKEN=your-discord-bot-token \
     -e BOT_LOGO=https://example.com/your-logo.png \
     -v /d/Lainly-bot:/data \
     noter-bot
   ```
   Alternatively, if using a .env file:
   ```bash
   docker run -d --name noter-bot --env-file .env -v /d/Lainly-bot:/data noter-bot
   ```
   Note: The `-v /d/Lainly-bot:/data` mounts the Windows directory D:\Lainly-bot to /data in the container for persisting data like the database. Adjust the host path as needed for your OS.

4. View logs to confirm the bot is running:
   ```bash
   docker logs noter-bot
   ```

5. Stop and remove the container when done:
   ```bash
   docker stop noter-bot
   docker rm noter-bot
   ```

## Deployment: Adding the Bot to Your Discord Server

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).

2. Create a new application and navigate to the "Bot" tab to create a bot.

3. Copy the bot token and add it to your `.env` file or pass it via environment variables.

4. Under "OAuth2" > "URL Generator":
   - Select scopes: `bot` and `applications.commands`.
   - Select bot permissions: At minimum, `View Channels`, `Send Messages`, `Embed Links`, `Attach Files` (for exports), and `Read Message History` if needed.
   - For full functionality, especially if using in restricted channels, ensure the bot has appropriate permissions.
   - Copy the generated URL and open it in your browser to invite the bot to your server. Choose the server and authorize.

5. Once added, the bot will appear offline until you run it. On startup, it will sync slash commands globally (may take up to an hour to appear in all servers).

6. Server admins can control access:
   - Use channel permissions or role restrictions to limit who can use /commands.
   - !commands are inherently restricted to administrators via bot code.

## Commands and Permissions

The bot provides two types of commands:

### Prefix Commands (!commands)
These are restricted to users with Administrator permissions on the server. They cannot be used by regular members.

- `!noteadd {user_id} {note}`: Adds a new note for the specified user. 🔖
- `!readnotes {user_id}`: Displays all notes for the user in a formatted embed. 📖
- `!delnote {note_id}`: Deletes a specific note and shows what was deleted. 🗑️
- `!clearnotes {user_id}`: Deletes all notes for the user and lists them. 🗑️🗑️
- `!note fetchall`: Downloads a zip archive of all server notes as CSV. 📦
- `!notehelp`: Shows this help message for note commands. ❓

### Slash Commands (/commands)
These are available to all users in the server, but access can be limited by server admins through Discord's permission system (e.g., channel permissions, role restrictions). This allows fine-grained control without bot-side restrictions.

- `/noteadd {user_id} {note}`: Adds a new note for the specified user. 🔖
- `/readnotes {user_id}`: Displays all notes for the user in a formatted embed. 📖
- `/delnote {note_id}`: Deletes a specific note and shows what was deleted. 🗑️
- `/clearnotes {user_id}`: Deletes all notes for the user and lists them. 🗑️🗑️
- `/note fetchall`: Downloads a zip archive of all server notes as CSV. 📦
- `/notehelp`: Shows this help message for note commands. ❓
- `/help`: Shows this help message for note commands. ❓

Notes are stored per guild (server) with unique IDs, timestamps, and creator info. Responses are sent in the channel where the command is invoked. Exports create a CSV file named "{servername}-notes-archive-{dd}-{mm}-{yyyy}.csv" zipped for download.

Made with :bow_and_arrow: by Lainly 2025 | BM Hunter forever