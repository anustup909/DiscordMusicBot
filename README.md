# Discord Music Bot

A modern Discord Music Bot written in Python using `discord.py` and `yt-dlp`. It streams audio directly from YouTube links or search queries using Slash Commands.

## Features
- **YouTube Streaming**: Streams audio directly without saving files locally.
- **Search Support**: Play direct links or search YouTube by simply typing keywords.
- **Auto-FFmpeg Setup**: Uses `static-ffmpeg` to automatically download and run FFmpeg (no manual installation required!).
- **Slash Commands**: Up-to-date with Discord's command guidelines.
- **Queue Management**: Add multiple songs to the queue and manage them seamlessly.

---

## 🛠️ Step-by-Step Setup Guide

### 1. Discord Developer Portal Setup
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application** (top right) and name your bot.
3. In the left menu, select **Bot**:
   - Under **Gateway Privileged Intents**, scroll down and enable **Message Content Intent** (and click "Save Changes").
   - Click **Reset Token**, copy the token, and keep it safe.
4. Go to **OAuth2** -> **URL Generator** in the left menu:
   - Under **Scopes**, check `bot` and `applications.commands`.
   - Under **Bot Permissions**, check:
     - **Send Messages**
     - **Embed Links**
     - **Connect** (under Voice)
     - **Speak** (under Voice)
   - Copy the generated URL at the bottom and open it in a new browser tab to invite the bot to your server.

### 2. Local Installation (Windows)
1. Open PowerShell or Command Prompt in the bot directory.
2. Create a virtual environment:
   ```powershell
   python -m venv .venv
   ```
3. Activate the virtual environment:
   ```powershell
   .venv\Scripts\activate
   ```
4. Install all dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
5. Ensure your Bot Token is in the `.env` file. You can also specify an optional server (guild) ID to lock the bot to your server (making it private) and allow commands to register instantly:
   ```env
   DISCORD_TOKEN=your_copied_token_here
   ALLOWED_GUILD_ID=your_server_id_here
   ```
   *To get your Server ID: Enable **Developer Mode** in Discord Settings -> Advanced. Then right-click your server icon in the server list and select **Copy Server ID**.*

### 3. Run the Bot
While the virtual environment is activated, run:
```powershell
python main.py
```
> **Note**: On the first start, `static-ffmpeg` will automatically download the FFmpeg binaries needed for streaming. This might take a few seconds.

---

## 🎵 Music Commands

Once the bot is online, use these slash commands in your Discord server:

- `/join` - Joins your active voice channel.
- `/play <query_or_url>` - Searches YouTube or plays a link (e.g., `/play lofi hip hop` or `/play https://www.youtube.com/watch?...`).
- `/nowplaying` - Displays the info and thumbnail of the active track.
- `/queue` - Lists upcoming songs in the queue.
- `/pause` - Pauses the playback.
- `/resume` - Resumes the playback.
- `/skip` - Skips the current song.
- `/stop` or `/leave` - Stops music, clears the queue, and disconnects the bot.
