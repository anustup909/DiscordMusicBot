# 🎵 Private Discord Music Bot

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/discord.py-v2.0%2B-blueviolet?style=for-the-badge&logo=discord&logoColor=white" alt="discord.py Version" />
  <img src="https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge&logo=git&logoColor=white" alt="Proprietary License" />
  <a href="https://instagram.com/anustup909" target="_blank">
    <img src="https://img.shields.io/badge/Instagram-Contact-E4405F?style=for-the-badge&logo=instagram&logoColor=white" alt="Instagram Contact" />
  </a>
</p>

A premium, private Discord Music Bot built with Python using `discord.py` and `yt-dlp`. It features optimized, lag-free audio streaming directly from YouTube link searches using slash commands.

---

## 🚫 Terms of Use & Copyright Notice

> [!WARNING]  
> **PROPRIETARY CODEBASE - STRICTLY NO COPYING**
> 
> All rights reserved. This repository and its contents are proprietary and confidential:
> - **No Copying/Replication**: You are strictly prohibited from copying, adapting, or reproducing any portion of this code.
> - **No Redistribution**: You may not distribute, clone, or publish forks of this repository.
> - **Authorized Access Only**: This code is licensed strictly for personal, private execution by the owner of this repository.

For inquiries, permissions, or questions, please contact me directly via **[Instagram](https://instagram.com/anustup909)**.

---

## ⚡ Key Highlights
- **Direct YouTube Streaming**: Instant streaming without downloading heavy files locally.
- **Advanced Search Support**: Input keywords or direct URLs to play music seamlessly.
- **Zero FFmpeg Hassle**: Utilizes `static-ffmpeg` to automatically download and run FFmpeg binaries.
- **Private Access Restriction**: The bot automatically leaves any unauthorized guilds, ensuring private usage.
- **Optimized Playback**: Customized streaming parameters to prevent lag and buffer drops.

---

## 🛠️ Step-by-Step Setup Guide

### 1. Discord Developer Portal Configuration
1. Navigate to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create a **New Application** and set up your bot's name and icon.
3. In the left menu, select **Bot**:
   - Scroll down to **Gateway Privileged Intents** and ensure **Message Content Intent** is enabled.
   - Click **Reset Token** and copy your secure bot token.
4. Go to **OAuth2** -> **URL Generator** in the left menu:
   - Check the **Scopes**: `bot` and `applications.commands`.
   - Check the **Bot Permissions**:
     - `Send Messages`
     - `Embed Links`
     - `Connect` (Voice)
     - `Speak` (Voice)
   - Copy the generated URL and use it to authorize the bot into your private server.

### 2. Local Installation
1. Open PowerShell or Command Prompt in the project folder.
2. Initialize the Python virtual environment:
   ```powershell
   python -m venv .venv
   ```
3. Activate the virtual environment:
   ```powershell
   .venv\Scripts\activate
   ```
4. Install the required modules:
   ```powershell
   pip install -r requirements.txt
   ```
5. Configure your secrets in the `.env` file (copied from `.env.example`):
   ```env
   DISCORD_TOKEN=your_secure_bot_token_here
   ALLOWED_GUILD_ID=your_private_server_id_here
   ```
   *(To copy your server ID, enable Discord's **Developer Mode** under Settings -> Advanced, then right-click your server's icon.)*

### 3. Running the Bot
Make sure your virtual environment is active, then execute:
```powershell
python main.py
```
> **Note**: On the very first run, `static-ffmpeg` will auto-download the required FFmpeg dependencies. This process completes within a few seconds.

---

## 🎵 Commands List

The bot operates entirely via Slash Commands:

| Command | Description |
|---|---|
| `/join` | Instructs the bot to join your active voice channel. |
| `/play <query_or_url>` | Plays music from a direct YouTube link or search query. |
| `/nowplaying` | Displays full details and thumbnail of the active track. |
| `/queue` | Shows the upcoming list of queued tracks. |
| `/pause` | Pauses playback. |
| `/resume` | Resumes playback. |
| `/skip` | Skips the current playing song. |
| `/stop` or `/leave` | Clears the queue, stops playback, and disconnects the bot. |

---

## ✉️ Contact & Support

If you have questions or want to get in touch, reach out to me on:
- **Instagram**: [@anustup909](https://instagram.com/anustup909) *(Note: If this username differs from your Instagram handle, update this link in the README!)*
- **GitHub**: [anustup909](https://github.com/anustup909)
