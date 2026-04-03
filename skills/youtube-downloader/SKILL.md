# YouTube Downloader

**Description:** Download YouTube videos, audio, playlists with full quality options using yt-dlp.

**Commands:**
- `download <url>` - Download video (best quality)
- `audio <url>` - Download audio only (MP3)
- `playlist <url>` - Download entire playlist
- `info <url>` - Get video information
- `formats <url>` - Show available formats
- `search <query>` - Search YouTube
- `live <url>` - Download live stream

**Quality Options:**
- `best` - Best quality
- `worst` - Smallest size
- `1080p`, `720p`, `480p` - Specific resolution

**Usage:**
```bash
python handler.py download "https://youtube.com/watch?v=..."
python handler.py audio "https://youtube.com/watch?v=..."
python handler.py info "https://youtube.com/watch?v=..."
python handler.py search "python tutorial"
```
