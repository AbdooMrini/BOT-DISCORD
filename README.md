# Discord Voice Tracker Bot

A Discord bot that follows a specific user and plays a sound when they join or move between voice channels.

## Features

- 🎯 Tracks a specific user's voice channel movements
- 🔊 Plays a custom sound when the tracked user joins or moves between voice channels
- 🤖 Auto-disconnects after playing the sound
- 🛠️ Automatically downloads and sets up FFmpeg
- 🌐 Includes a web server to keep the bot alive on hosting platforms

## Requirements

- Python 3.8 or higher
- Discord.py library
- A Discord bot token
- FFmpeg (automatically downloaded if not present)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/discord-voice-tracker-bot.git
   cd discord-voice-tracker-bot
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project directory with your Discord bot token and target user:
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   TARGET_USER=username_to_track
   ```

4. Add your sound file:
   - Create a `sounds` directory in the project root
   - Add your MP3 file as `sounds/sound.mp3`

## Usage

Run the bot with: 