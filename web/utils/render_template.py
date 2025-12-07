import urllib.parse
import html
import logging
import io
import os
import base64
import tempfile
import subprocess

from hydrogram import enums
from info import BIN_CHANNEL, URL
from utils import temp, get_size

logger = logging.getLogger(__name__)

async def _try_download_thumbnail(media_msg, media):
    """
    कोशिश करें: Telegram-provided thumbnail डाउनलोड करें और base64 data URI लौटाएं.
    Falls back to generating thumbnail via ffmpeg if no tg-thumb and ffmpeg available.
    Returns: data_uri string or None
    """
    # 1) संभावित thumbnail attributes खोजो
    thumb_candidates = []
    # common attribute names across clients
    for attr in ("thumb", "thumbnail", "thumbs", "photo", "preview", "small_thumbnail"):
        candidate = getattr(media, attr, None)
        if candidate:
            thumb_candidates.append(candidate)

    # Telethon sometimes stores thumbnails inside media.document.thumbs
    try:
        doc = getattr(media, "document", None)
        if doc and getattr(doc, "thumb", None):
            thumb_candidates.append(doc.thumb)
        if doc and getattr(doc, "thumbs", None):
            thumb_candidates.extend(getattr(doc, "thumbs"))
    except Exception:
        pass

    # Try to download first candidate to bytes
    for thumb in thumb_candidates:
        try:
            b = io.BytesIO()
            # many clients support download_media(message/media, file=BytesIO())
            await temp.BOT.download_media(thumb, file=b)
            b.seek(0)
            data = b.read()
            if data:
                mime = "image/jpeg"  # usually jpeg; we keep jpeg by default
                return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"
        except Exception:
            logger.debug("Thumbnail candidate download failed, trying next.", exc_info=True)

    # 2) अगर कोई tg thumb नहीं मिला — fallback: अगर ffmpeg उपलब्ध है, तो full media से एक frame निकालो
    try:
        # Download full media temporarily
        with tempfile.TemporaryDirectory() as td:
            in_path = os.path.join(td, "input_media")
            out_path = os.path.join(td, "thumb.jpg")

            # download media to file path (some clients return path when file param is filepath)
            # try BytesIO first, else path
            try:
                b = io.BytesIO()
                await temp.BOT.download_media(media, file=b)
                b.seek(0)
                if b.getbuffer().nbytes > 0:
                    with open(in_path, "wb") as f:
                        f.write(b.read())
                else:
                    raise RuntimeError("Empty bytes from download")
            except Exception:
                # fallback: ask client to save to path directly
                try:
                    await temp.BOT.download_media(media, file=in_path)
                except Exception:
                    logger.debug("Could not download media for ffmpeg fallback.", exc_info=True)
                    raise

            # Check ffmpeg existence
            ffmpeg_path = shutil.which("ffmpeg") if 'shutil' in globals() else None
            if not ffmpeg_path:
                import shutil
                ffmpeg_path = shutil.which("ffmpeg")
            if ffmpeg_path:
                # extract frame at 1 second (or 0)
                cmd = [ffmpeg_path, "-y", "-i", in_path, "-ss", "00:00:01.000", "-vframes", "1", "-q:v", "2", out_path]
                proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
                if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                    with open(out_path, "rb") as f:
                        data = f.read()
                        return f"data:image/jpeg;base64,{base64.b64encode(data).decode('ascii')}"
    except Exception:
        logger.debug("ffmpeg thumbnail generation failed.", exc_info=True)

    return None


async def media_watch(message_id):
    try:
        media_msg = await temp.BOT.get_messages(BIN_CHANNEL, message_id)

        # Safely resolve media attribute name
        media_attr = None
        if hasattr(media_msg, "media") and getattr(media_msg, "media") is not None:
            try:
                media_attr = media_msg.media.value
            except Exception:
                media_attr = None

        media = getattr(media_msg, media_attr, None) if media_attr else None
        if not media:
            return "<h1>File Not Found or Deleted</h1>"

        # Stream link (quote message_id)
        stream_path = f"download/{urllib.parse.quote(str(message_id))}"
        stream_link = urllib.parse.urljoin(URL, stream_path)

        # File details
        raw_file_name = getattr(media, "file_name", None) or getattr(media, "title", None) or "Unknown File"
        file_name = raw_file_name or "Unknown File"
        safe_heading = html.escape(file_name)
        file_size = get_size(getattr(media, "file_size", 0))
        mime_type = (getattr(media, "mime_type", None) or "").lower()

        # Detect HLS: either mime type indicates mpegurl or filename endswith .m3u8
        is_hls = False
        if "mpegurl" in mime_type or "application/x-mpegurl" in mime_type or (str(file_name).lower().endswith(".m3u8")):
            is_hls = True

        # Detect audio / video (for non-hls)
        is_video = ("video" in mime_type) or (not is_hls and file_name.lower().split('.')[-1] in ("mp4", "mkv", "webm", "mov", "avi"))
        is_audio = ("audio" in mime_type) or (file_name.lower().split('.')[-1] in ("mp3", "aac", "ogg"))

        # If not streamable (and not hls) return download page
        if not (is_video or is_audio or is_hls):
            return f"""
            <html>
            <head><title>Error</title></head>
            <body style="background:#0f172a; color:#f8fafc; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh;">
                <div style="text-align:center;">
                    <h1>⚠️ File Format Not Supported</h1>
                    <p>This file type ({html.escape(mime_type or 'unknown')}) cannot be streamed.</p>
                    <a href="{html.escape(stream_link)}" style="color:#818cf8; text-decoration:none; border:1px solid #818cf8; padding:10px 20px; border-radius:5px; display:inline-block; margin-top:10px;">Download File</a>
                </div>
            </body>
            </html>
            """

        # Try to get poster (thumbnail) as data URI
        poster_datauri = await _try_download_thumbnail(media_msg, media)
        if not poster_datauri:
            # fallback to a static poster
            poster_datauri = "https://i.ibb.co/M8S0Zzj/live-streaming.png"

        safe_stream_link = html.escape(stream_link, quote=True)
        safe_mime = html.escape(mime_type or ("application/vnd.apple.mpegurl" if is_hls else "video/mp4"), quote=True)
        safe_download_name = html.escape(file_name, quote=True)
        vlc_href = f"vlc://{stream_link}"
        safe_vlc_href = html.escape(vlc_href, quote=True)

        # Build media_tag: if HLS, we still use <video id="player"> but JS will attach hls.js when needed
        if is_hls or is_video:
            media_tag = f'''
            <video id="player" class="plyr" playsinline controls preload="metadata" poster="{html.escape(poster_datauri, quote=True)}">
                <source src="{safe_stream_link}" type="{safe_mime}" />
                Your browser does not support the video tag.
            </video>
            '''
        else:
            media_tag = f'''
            <audio id="player" class="plyr" controls preload="metadata">
                <source src="{safe_stream_link}" type="{safe_mime}" />
                Your browser does not support the audio element.
            </audio>
            '''

        # Render template (including HLS handling script)
        return html_template_with_hls.format(
            heading=safe_heading,
            file_name=safe_heading,
            file_size=file_size,
            src=safe_stream_link,
            mime_type=safe_mime,
            poster=html.escape(poster_datauri, quote=True),
            media_tag=media_tag,
            download_name=safe_download_name,
            vlc_href=safe_vlc_href,
            is_hls=str(is_hls).lower()
        )

    except Exception:
        logger.exception("Render Template Error")
        return "<h1>Something went wrong. Please check logs.</h1>"


# --- HTML template with HLS support (uses hls.js when needed) ---
html_template_with_hls = """
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
    /* same styles as before (omitted here for brevity) */
    </style>
</head>
<body>

    <header class="header">
        <div class="file-title"><i class="ri-file-video-line"></i> {file_name}</div>
    </header>

    <div class="main-container">
        <div class="player-wrapper">
            {media_tag}
        </div>

        <div class="meta-card">
            <div class="file-info">
                <span><i class="ri-hard-drive-2-line"></i> Size: <b>{file_size}</b></span>
                <span><i class="ri-movie-line"></i> Type: <b>{mime_type}</b></span>
            </div>
            
            <div class="actions">
                <a href="{src}" class="btn btn-primary" download="{download_name}">
                    <i class="ri-download-cloud-2-line"></i> Download
                </a>
                <a href="{vlc_href}" class="btn btn-secondary" target="_blank" rel="noopener noreferrer">
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
    <!-- hls.js from CDN -->
    <script src="https://cdn.jsdelivr.net/npm/hls.js@1.4.3/dist/hls.min.js"></script>

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

            const isHls = {is_hls};
            const src = "{src}";

            // If HLS and browser doesn't natively support, use hls.js
            if (isHls) {{
                const video = document.getElementById('player');
                // Safari/iOS supports HLS natively
                if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                    // Native support: done (source tag already)
                    // Need to update source if required
                }} else if (Hls.isSupported()) {{
                    const hls = new Hls();
                    hls.loadSource(src);
                    hls.attachMedia(video);
                    hls.on(Hls.Events.MANIFEST_PARSED, function() {{
                        // autoplay or restore
                    }});
                }} else {{
                    // no hls support. show a message or let download happen
                    console.warn('HLS not supported in this browser.');
                }}
            }}
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
