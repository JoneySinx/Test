import urllib.parse
import html
import logging
from hydrogram import enums
from info import BIN_CHANNEL, URL
from utils import temp, get_size

# Configure Logging
logger = logging.getLogger(__name__)

async def media_watch(message_id):
    try:
        # Fetch Message
        media_msg = await temp.BOT.get_messages(BIN_CHANNEL, message_id)
        media = getattr(media_msg, media_msg.media.value, None)
        
        if not media:
            return "<h1>File Not Found or Deleted</h1>"

        # Generate Stream Link
        stream_link = urllib.parse.urljoin(URL, f'download/{message_id}')
        
        # Get File Details
        file_name = getattr(media, 'file_name', 'Unknown File')
        file_size = get_size(getattr(media, 'file_size', 0))
        mime_type = getattr(media, 'mime_type', 'video/mp4')
        
        # Determine Player Type (Video/Audio)
        is_video = 'video' in mime_type
        is_audio = 'audio' in mime_type
        
        if not (is_video or is_audio):
            return f"""
            <html>
            <head><title>Error</title></head>
            <body style="background:#0f172a; color:#f8fafc; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh;">
                <div style="text-align:center;">
                    <h1>⚠️ File Format Not Supported</h1>
                    <p>This file type ({mime_type}) cannot be streamed.</p>
                    <a href="{stream_link}" style="color:#818cf8; text-decoration:none; border:1px solid #818cf8; padding:10px 20px; border-radius:5px; display:inline-block; margin-top:10px;">Download File</a>
                </div>
            </body>
            </html>
            """

        heading = html.escape(file_name)
        
        # Render HTML
        return html_template.format(
            heading=heading,
            file_name=file_name,
            file_size=file_size,
            src=stream_link,
            mime_type=mime_type,
            poster="https://i.ibb.co/M8S0Zzj/live-streaming.png" # You can add dynamic thumbnail logic here if needed
        )

    except Exception as e:
        logger.error(f"Render Template Error: {e}")
        return "<h1>Something went wrong. Please check logs.</h1>"


# --- Optimized HTML Template ---
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{heading}</title>
    <meta property="og:title" content="{heading}">
    <meta property="og:site_name" content="YourX Stream">
    <meta property="og:description" content="Stream or Download this file instantly. Size: {file_size}">
    <meta property="og:image" content="{poster}">
    
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/remixicon@2.5.0/fonts/remixicon.css">
    
    <link rel="stylesheet" href="https://cdn.plyr.io/3.7.8/plyr.css" />
    
    <style>
        :root {{
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --bg-dark: #0f172a;
            --bg-card: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        
        /* Header */
        .header {{
            width: 100%;
            padding: 1.5rem 2rem;
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(10px);
            position: sticky;
            top: 0;
            z-index: 50;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            display: flex;
            justify-content: center;
        }}
        
        .file-title {{
            font-size: 1.1rem;
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 90%;
            color: var(--text-main);
        }}
        
        /* Main Container */
        .main-container {{
            flex: 1;
            width: 100%;
            max-width: 1000px;
            padding: 2rem 1rem;
            display: flex;
            flex-direction: column;
            gap: 2rem;
            justify-content: center;
        }}
        
        /* Player Wrapper */
        .player-wrapper {{
            background: #000;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255,255,255,0.05);
        }}
        
        /* Metadata Card */
        .meta-card {{
            background: var(--bg-card);
            padding: 1.5rem;
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            border: 1px solid rgba(255,255,255,0.05);
        }}
        
        .file-info {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: var(--text-muted);
            font-size: 0.9rem;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            padding-bottom: 1rem;
        }}
        
        /* Action Buttons */
        .actions {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 1rem;
        }}
        
        .btn {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            padding: 0.8rem 1.2rem;
            border-radius: 8px;
            font-weight: 500;
            text-decoration: none;
            transition: all 0.2s ease;
            cursor: pointer;
            border: none;
            font-size: 0.95rem;
        }}
        
        .btn-primary {{
            background: var(--primary);
            color: white;
            box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.3);
        }}
        .btn-primary:hover {{ background: var(--primary-hover); transform: translateY(-1px); }}
        
        .btn-secondary {{
            background: rgba(255,255,255,0.05);
            color: var(--text-main);
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .btn-secondary:hover {{ background: rgba(255,255,255,0.1); }}

        /* Toast Notification */
        #toast {{
            visibility: hidden;
            min-width: 250px;
            background-color: #10b981;
            color: #fff;
            text-align: center;
            border-radius: 8px;
            padding: 12px;
            position: fixed;
            z-index: 100;
            left: 50%;
            bottom: 30px;
            transform: translateX(-50%);
            font-size: 0.9rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            opacity: 0;
            transition: opacity 0.3s;
        }}
        #toast.show {{ visibility: visible; opacity: 1; }}

        /* Plyr Customization */
        .plyr {{ --plyr-color-main: var(--primary); border-radius: 12px; }}

        @media (max-width: 640px) {{
            .file-title {{ font-size: 1rem; }}
            .main-container {{ padding: 1rem; }}
            .actions {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>

    <header class="header">
        <div class="file-title"><i class="ri-file-video-line"></i> {file_name}</div>
    </header>

    <div class="main-container">
        
        <div class="player-wrapper">
            <video id="player" class="plyr" playsinline controls poster="{poster}">
                <source src="{src}" type="{mime_type}" />
            </video>
        </div>

        <div class="meta-card">
            <div class="file-info">
                <span><i class="ri-hard-drive-2-line"></i> Size: <b>{file_size}</b></span>
                <span><i class="ri-movie-line"></i> Type: <b>{mime_type}</b></span>
            </div>
            
            <div class="actions">
                <a href="{src}" class="btn btn-primary" download>
                    <i class="ri-download-cloud-2-line"></i> Download
                </a>
                <a href="vlc://{src}" class="btn btn-secondary">
                    <i class="ri-play-circle-line"></i> Play in VLC
                </a>
                <button onclick="copyLink()" class="btn btn-secondary">
                    <i class="ri-file-copy-line"></i> Copy Link
                </button>
            </div>
        </div>
    </div>

    <div id="toast">Link Copied to Clipboard!</div>

    <script src="https://cdn.plyr.io/3.7.8/plyr.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const controls = [
                'play-large', 'restart', 'rewind', 'play', 'fast-forward',
                'progress', 'current-time', 'duration', 'mute', 'volume',
                'captions', 'settings', 'pip', 'airplay', 'fullscreen'
            ];
            
            const player = new Plyr('#player', {{
                controls,
                keyboard: {{ focused: true, global: true }},
                tooltips: {{ controls: true, seek: true }}
            }});
        }});

        function copyLink() {{
            const link = "{src}";
            navigator.clipboard.writeText(link).then(() => {{
                const toast = document.getElementById("toast");
                toast.className = "show";
                setTimeout(() => {{ toast.className = toast.className.replace("show", ""); }}, 3000);
            }}).catch(err => {{
                console.error('Failed to copy: ', err);
            }});
        }}
    </script>
</body>
</html>
"""
