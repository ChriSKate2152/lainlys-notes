# Lainlys-notes
A Discord bot for handling notes for users. Keep track of things about your Discord users!
This bot is based on Noter from https://github.com/therealOri/noter.git with multiple improvements implemented such as: 
* Ability to set multiple role IDs. 
* Added support for multi-notes per UserID 
* Added command to delete a single note or all notes per UserID
* Adjusted bot to work with Discord 2.3.2 api requirements

Now supports multiple notes per user, with details like creator, timestamps, and multiple staff roles.

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

5. Create a `.env` file in the project root (copy from `.env.example`):
   ```
   TOKEN=your-discord-bot-token
   BOT_LOGO=https://example.com/your-logo.png
   # Comma-separated list
   STAFF_ROLE_IDS=123456789,987654321
   ```

6. Run the bot:
   ```bash
   python noter.py
   ```

## Docker Deployment

1. Ensure Docker is installed on your system.

2. Build the Docker image:
   ```bash
   docker build -t noter-bot .
   ```

3. Run the container, passing environment variables (recommended for security instead of copying .env):
   ```bash
   docker run -d --name noter-bot \
     -e TOKEN=your-discord-bot-token \
     -e BOT_LOGO=https://example.com/your-logo.png \
     -e STAFF_ROLE_IDS=123456789,987654321 \
     noter-bot
   ```
   Alternatively, if using a .env file:
   ```bash
   docker run -d --name noter-bot --env-file .env noter-bot
   ```

4. View logs:
   ```bash
   docker logs noter-bot
   ```

5. Stop the container:
   ```bash
   docker stop noter-bot
   ```

## Deployment: Adding the Bot to Your Discord Server

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).

2. Create a new application and navigate to the "Bot" tab to create a bot.

3. Copy the bot token and add it to your `.env` file.

4. Under "OAuth2" > "URL Generator":
   - Select scopes: `bot` and `applications.commands`.
   - Select permissions: General permissions like View Channels, Send Messages, etc., as needed (minimal for this bot).
   - Copy the generated URL and open it in your browser to invite the bot to your server.

5. In your server, create role(s) for staff/moderators and note their ID(s) (right-click role > Copy ID, enable Developer Mode in settings if needed).

6. Update `STAFF_ROLE_IDS` in `.env` with the comma-separated list of IDs.

7. Restart the bot or container if running.

## Commands
- `!noteadd {user_id} {note}`: Add a new note for the specified user (multiple notes per user allowed).
- `!readnotes {user_id}`: Show all notes for the specified user, including ID, creator, last updated time, and content.
- `!delnote {note_id}`: Delete a specific note by its ID.
- `!clearnotes {user_id}`: Delete all notes for the specified user.
- `!note fetchall`: Download a zip archive of all notes in the server.
- `!notehelp`: Display help for note commands.

Notes are stored per guild with unique IDs, timestamps, and creator info. Responses are sent in the channel.

Made with :bow_and_arrow: by Lainly 2025 | BM Hunter forever