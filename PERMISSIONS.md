# Discord Bot Permissions Guide

This document outlines all the required permissions and intents for the Noter bot to function correctly.

---

## 🔐 Required Privileged Gateway Intents

**These MUST be enabled in the Discord Developer Portal:**

### 1. **MESSAGE CONTENT INTENT** ⚠️ **CRITICAL**
- **Why Required**: Allows the bot to read message content for prefix commands (`!noteadd`, `!rmdm`, etc.)
- **Without This**: Prefix commands (`!commands`) will not work at all
- **How to Enable**:
  1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
  2. Select your application
  3. Click "Bot" in the left sidebar
  4. Scroll down to "Privileged Gateway Intents"
  5. Toggle **ON** "MESSAGE CONTENT INTENT"
  6. Click "Save Changes"
  7. **Restart your bot**

### 2. **SERVER MEMBERS INTENT**
- **Why Required**: Allows the bot to access guild member information
- **Used For**:
  - Fetching user information (line 226, 284, 454, 569, 667, 779)
  - Validating administrator permissions (line 702, 732, 746)
  - Getting member details for notes
- **How to Enable**:
  1. Same location as MESSAGE CONTENT INTENT
  2. Toggle **ON** "SERVER MEMBERS INTENT"
  3. Save changes

---

## 🤖 Required Bot Permissions

**When generating the invite link, select these permissions:**

### Text Permissions

#### ✅ **View Channels** (Essential)
- **Permission Bit**: `VIEW_CHANNEL` (1024)
- **Why Required**: Bot needs to see channels to operate in them
- **Used In**: All commands

#### ✅ **Send Messages** (Essential)
- **Permission Bit**: `SEND_MESSAGES` (2048)
- **Why Required**: Send responses, embeds, and reminders
- **Used In**:
  - All command responses (lines 237, 299, 306, 422, 474, 503, 543, 590, 625, 679, 736)
  - Error messages
  - Reminder notifications

#### ✅ **Send Messages in Threads** (Recommended)
- **Permission Bit**: `SEND_MESSAGES_IN_THREADS` (274877906944)
- **Why Required**: If commands are used in threads
- **Used In**: Same as Send Messages

#### ✅ **Embed Links** (Essential)
- **Permission Bit**: `EMBED_LINKS` (16384)
- **Why Required**: All bot responses use Discord embeds
- **Used In**:
  - All embeds created by `create_error_embed()` and `create_success_embed()`
  - Help messages (line 375)
  - Note displays (line 470, 581)
  - Reminder confirmations (line 234, 241, 665)

#### ✅ **Attach Files** (Essential)
- **Permission Bit**: `ATTACH_FILES` (32768)
- **Why Required**: Sending note archive ZIP files
- **Used In**:
  - `/note fetchall` and `!note fetchall` commands (line 196, 620)
  - ZIP file downloads

#### ✅ **Read Message History** (Essential)
- **Permission Bit**: `READ_MESSAGE_HISTORY` (65536)
- **Why Required**: Reading messages for prefix commands
- **Used In**:
  - Processing prefix commands (line 318)
  - Message event handling (line 313)

#### ✅ **Add Reactions** (Essential) ⚠️ **CRITICAL FOR RMDM**
- **Permission Bit**: `ADD_REACTIONS` (64)
- **Why Required**: Adding ✅ reaction to `!rmdm` messages
- **Used In**:
  - `!rmdm` command (line 675, 783)
  - Confirmation reactions
- **Without This**: The green checkmark feature won't work

#### ✅ **Use External Emojis** (Optional)
- **Permission Bit**: `USE_EXTERNAL_EMOJIS` (262144)
- **Why Required**: If you want to use custom emojis in bot responses
- **Used In**: Not currently used, but good for future features

#### ✅ **Mention @everyone, @here, and All Roles** (Optional)
- **Permission Bit**: `MENTION_EVERYONE` (131072)
- **Why Required**: Only if you want reminders to mention @everyone
- **Currently Used**: No (mentions are user-specific with `<@{user_id}>`)

### General Permissions

#### ✅ **Use Application Commands** (Essential)
- **Permission Bit**: `USE_APPLICATION_COMMANDS` (2147483648)
- **Why Required**: For all slash commands (`/noteadd`, `/rmdm`, etc.)
- **Used In**: All slash command definitions (lines 810-848)

---

## 📋 Permission Integer Calculation

To generate the invite link, you need a permission integer. Here's the breakdown:

### Minimum Required Permissions
```
View Channels:              1024
Add Reactions:              64
Send Messages:              2048
Embed Links:                16384
Attach Files:               32768
Read Message History:       65536
Use Application Commands:   2147483648
Send Messages in Threads:   274877906944
────────────────────────────────────────
TOTAL (Decimal):            277025554432
TOTAL (Hex):                0x408001D040
```

### Recommended Permissions (Includes Optional)
```
All Minimum +
Use External Emojis:        262144
────────────────────────────────────────
TOTAL (Decimal):            277025816576
TOTAL (Hex):                0x408005D040
```

---

## 🔗 Generating the Invite Link

### Method 1: Discord Developer Portal (Recommended)

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application
3. Click "OAuth2" → "URL Generator"
4. Under **SCOPES**, select:
   - ✅ `bot`
   - ✅ `applications.commands`
5. Under **BOT PERMISSIONS**, select:
   - ✅ View Channels
   - ✅ Send Messages
   - ✅ Send Messages in Threads
   - ✅ Embed Links
   - ✅ Attach Files
   - ✅ Read Message History
   - ✅ Add Reactions
   - ✅ Use External Emojis (optional)
6. Copy the generated URL at the bottom
7. Open the URL in your browser
8. Select the server and authorize

### Method 2: Manual URL Construction

```
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_CLIENT_ID&permissions=277025554432&scope=bot%20applications.commands
```

Replace `YOUR_BOT_CLIENT_ID` with your bot's client ID.

---

## 🛠️ Code Reference

### Where Permissions Are Used

| Feature | Permission | Code Location |
|---------|-----------|---------------|
| Read prefix commands | Message Content Intent | Line 313-318 |
| Fetch user info | Server Members Intent | Lines 226, 284, 454, 569, 667, 779 |
| Send embeds | Send Messages + Embed Links | Lines 237, 299, 422, 474, 503, etc. |
| Send DMs | Send Messages | Lines 243, 668, 780 |
| Add checkmark reaction | Add Reactions | Lines 675, 783 |
| Download archives | Attach Files | Lines 196, 620 |
| Process commands | Read Message History | Line 318 |
| Slash commands | Use Application Commands | Lines 810-848 |
| Channel reminders | Send Messages | Line 237 |
| DM reminders | Send Messages (DMs) | Line 243, 668, 780 |

### Intents Configuration (Code: Lines 260-263)

```python
intents = discord.Intents.default()
intents.members = True              # Server Members Intent
intents.message_content = True      # Message Content Intent (CRITICAL!)
ntr = commands.Bot(command_prefix='!', intents=intents)
```

---

## ✅ Verification Checklist

After setting up permissions, verify everything works:

### In Discord Developer Portal:
- [ ] MESSAGE CONTENT INTENT is enabled
- [ ] SERVER MEMBERS INTENT is enabled
- [ ] Bot has been re-invited with correct permissions (or permissions updated in server settings)

### In Server Settings:
- [ ] Bot role has "Add Reactions" permission
- [ ] Bot can see the channels where commands are used
- [ ] Bot can send messages in those channels

### Testing:
- [ ] Run `!notehelp` - should display help embed
- [ ] Run `/notehelp` - should display help embed
- [ ] Run `!rmdm in 5 minutes test` - should:
  - Send DM with reminder details
  - Add ✅ reaction to your message
  - Show debug logs in console
- [ ] Run `/rmdm` - should:
  - Send DM with reminder details
  - Show "✅ Personal Reminder set. Details sent to your DM." ephemeral message

### Check Bot Logs:
After starting the bot, you should see:
```
[STARTUP] Bot starting...
[READY] Logged in as YourBot (ID: ...)
[READY] Message Content Intent: True   ← MUST BE TRUE
[READY] Members Intent: True           ← MUST BE TRUE
------
[READY] Slash commands synced
```

If any intent shows `False`, go back to the Developer Portal and enable it!

---

## ⚠️ Common Permission Issues

### Issue 1: "Missing Permissions" Error
- **Cause**: Bot lacks permission in the channel
- **Fix**: Check channel-specific permissions or move bot role higher in role hierarchy

### Issue 2: Prefix Commands Don't Work
- **Cause**: MESSAGE CONTENT INTENT not enabled
- **Fix**: Enable in Developer Portal and restart bot
- **Verify**: Check logs show `Message Content Intent: True`

### Issue 3: Can't Add Reactions
- **Cause**: Missing "Add Reactions" permission
- **Fix**: Re-invite bot with updated permissions or grant permission in server settings

### Issue 4: Can't Send DMs
- **Cause**: User has DMs disabled or blocked the bot
- **Fix**: This is user-side; bot can't override this
- **Workaround**: Tell users to enable DMs from server members

### Issue 5: Slash Commands Don't Appear
- **Cause**: Missing "Use Application Commands" scope or permission
- **Fix**: Re-invite bot with `bot` and `applications.commands` scopes
- **Note**: Can take up to 1 hour to sync globally

---

## 🔒 Security Notes

### Permissions This Bot DOES NOT Need:
- ❌ Administrator (never give this!)
- ❌ Manage Server
- ❌ Manage Roles
- ❌ Manage Channels
- ❌ Kick Members
- ❌ Ban Members
- ❌ Manage Webhooks
- ❌ Manage Emojis
- ❌ View Audit Log

**Security Principle**: Only grant the minimum permissions required for functionality.

### Who Can Use Prefix Commands:
- Prefix commands (`!noteadd`, `!rmdm`, etc.) require **Administrator** permission
- This is enforced by `@commands.has_permissions(administrator=True)` decorator
- Even if bot has permissions, users without Admin can't use `!commands`

### Who Can Use Slash Commands:
- All server members can see and use slash commands by default
- Server admins can restrict slash commands via Discord's permission system:
  - Server Settings → Integrations → Bots → [Your Bot] → Manage
  - Restrict by role or channel

---

## 📞 Support

If you're still having permission issues after following this guide:

1. Check Docker logs: `docker logs -f noter-bot`
2. Look for `[ERROR]` or `Missing Permissions` messages
3. Verify intents show `True` in startup logs
4. Test in a new test server with fresh bot invite
5. Review the TROUBLESHOOTING.md file

---

**Last Updated**: Based on noter.py (855 lines)

**Permission Integer for Quick Copy**: `277025554432` (minimum required)

