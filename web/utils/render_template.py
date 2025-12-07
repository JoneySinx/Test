html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{heading} | YourX Stream</title>
    
    <!-- Meta -->
    <meta property="og:title" content="{heading}">
    <meta property="og:site_name" content="YourX Stream">
    <meta property="og:description" content="Stream or download instantly. Size: {file_size}">
    <meta property="og:image" content="{poster}">
    <meta name="theme-color" content="#0f172a">

    <!-- Fonts & Icons -->
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/remixicon@2.5.0/fonts/remixicon.css">

    <!-- Plyr CSS -->
    <link rel="stylesheet" href="https://cdn.plyr.io/3.7.8/plyr.css" />

    <style>
        :root {{
            --bg-body: #020617;
            --bg-elevated: #020617;
            --bg-card: #020617;
            --border-subtle: rgba(148, 163, 184, 0.25);
            --primary: #6366f1;
            --primary-soft: rgba(99, 102, 241, 0.12);
            --primary-hover: #4f46e5;
            --text-main: #e5e7eb;
            --text-muted: #9ca3af;
            --radius-lg: 18px;
            --radius-md: 12px;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Outfit', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: radial-gradient(circle at top left, #111827 0, #020617 45%, #020617 100%);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* Top Brand Bar */
        .top-bar {{
            width: 100%;
            padding: 0.75rem 1.5rem;
            border-bottom: 1px solid rgba(148, 163, 184, 0.15);
            backdrop-filter: blur(12px);
            background: linear-gradient(to right, rgba(15, 23, 42, 0.9), rgba(15, 23, 42, 0.75));
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.95rem;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: var(--text-muted);
        }}

        .brand span.logo-mark {{
            width: 26px;
            height: 26px;
            border-radius: 999px;
            background: radial-gradient(circle at 30% 0, #a5b4fc, #6366f1 45%, #4c1d95 100%);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.9rem;
            font-weight: 600;
            box-shadow: 0 0 0 1px rgba(129, 140, 248, 0.5), 0 10px 25px rgba(15, 23, 42, 0.8);
        }}

        .brand span.text-strong {{
            color: #e5e7eb;
            font-weight: 600;
        }}

        /* Layout */
        .page {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1.75rem 1rem 2.25rem;
        }}

        .shell {{
            width: 100%;
            max-width: 1100px;
        }}

        .grid {{
            display: grid;
            grid-template-columns: minmax(0, 2.1fr) minmax(0, 1.4fr);
            gap: 1.5rem;
            align-items: stretch;
        }}

        @media (max-width: 880px) {{
            .grid {{
                grid-template-columns: minmax(0, 1fr);
            }}
        }}

        /* Player Card */
        .player-card {{
            background: radial-gradient(circle at top, rgba(15, 23, 42, 0.9), #020617);
            border-radius: var(--radius-lg);
            overflow: hidden;
            border: 1px solid rgba(148, 163, 184, 0.3);
            box-shadow:
                0 24px 80px rgba(15, 23, 42, 0.95),
                0 0 0 1px rgba(15, 23, 42, 0.6);
            position: relative;
        }}

        .player-top {{
            padding: 1rem 1.25rem 0.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 0.75rem;
        }}

        .title-wrap {{
            display: flex;
            flex-direction: column;
            gap: 0.3rem;
            min-width: 0;
        }}

        .file-badge {{
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-muted);
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
        }}

        .file-badge i {{
            font-size: 0.85rem;
            color: #a5b4fc;
        }}

        .file-heading {{
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-main);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 100%;
        }}

        .chip {{
            padding: 0.25rem 0.7rem;
            border-radius: 999px;
            border: 1px solid rgba(148, 163, 184, 0.4);
            font-size: 0.7rem;
            color: var(--text-muted);
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            background: rgba(15, 23, 42, 0.8);
        }}

        .chip-dot {{
            width: 7px;
            height: 7px;
            border-radius: 999px;
            background: #22c55e;
            box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.15);
        }}

        .player-wrap {{
            padding: 0 0.75rem 0.75rem;
        }}

        .player-inner {{
            border-radius: 14px;
            overflow: hidden;
            background: #000;
        }}

        /* Plyr */
        .plyr {{
            --plyr-color-main: var(--primary);
            border-radius: 14px;
        }}

        /* Meta Card */
        .meta-card {{
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(15, 23, 42, 0.98));
            border-radius: var(--radius-lg);
            border: 1px solid var(--border-subtle);
            padding: 1.25rem 1.2rem 1.4rem;
            display: flex;
            flex-direction: column;
            gap: 1.15rem;
            position: relative;
            overflow: hidden;
        }}

        .meta-card::before {{
            content: "";
            position: absolute;
            inset: -40%;
            opacity: 0.12;
            background: radial-gradient(circle at top left, #6366f1, transparent 55%),
                        radial-gradient(circle at bottom right, #4c1d95, transparent 60%);
            pointer-events: none;
        }}

        .meta-header {{
            position: relative;
            z-index: 1;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}

        .meta-title {{
            font-size: 1.05rem;
            font-weight: 600;
        }}

        .meta-sub {{
            font-size: 0.8rem;
            color: var(--text-muted);
        }}

        .meta-sub span.dot {{
            display: inline-block;
            width: 4px;
            height: 4px;
            border-radius: 999px;
            background: rgba(148, 163, 184, 0.6);
            margin: 0 0.35rem;
        }}

        .file-stats {{
            position: relative;
            z-index: 1;
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.75rem;
            padding: 0.9rem 0.9rem;
            border-radius: var(--radius-md);
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(148, 163, 184, 0.25);
        }}

        .stat {{
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }}

        .stat-label {{
            font-size: 0.76rem;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }}

        .stat-label i {{
            font-size: 0.9rem;
            color: #a5b4fc;
        }}

        .stat-value {{
            font-size: 0.9rem;
            font-weight: 500;
        }}

        /* Actions */
        .actions {{
            position: relative;
            z-index: 1;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 0.6rem;
        }}

        .btn {{
            border: none;
            outline: none;
            cursor: pointer;
            border-radius: 999px;
            font-size: 0.9rem;
            font-weight: 500;
            padding: 0.75rem 1rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.4rem;
            text-decoration: none;
            transition: all 0.16s ease-out;
            white-space: nowrap;
        }}

        .btn-primary {{
            background: linear-gradient(135deg, #6366f1, #4f46e5);
            color: #f9fafb;
            box-shadow:
                0 12px 30px rgba(79, 70, 229, 0.35),
                0 0 0 1px rgba(129, 140, 248, 0.6);
        }}

        .btn-primary:hover {{
            transform: translateY(-1px);
            box-shadow:
                0 16px 40px rgba(79, 70, 229, 0.45),
                0 0 0 1px rgba(129, 140, 248, 0.8);
        }}

        .btn-ghost {{
            background: rgba(15, 23, 42, 0.9);
            color: var(--text-main);
            border: 1px solid rgba(148, 163, 184, 0.35);
        }}

        .btn-ghost:hover {{
            background: rgba(15, 23, 42, 1);
            transform: translateY(-1px);
        }}

        .btn-ghost i,
        .btn-primary i {{
            font-size: 1.05rem;
        }}

        @media (max-width: 480px) {{
            .meta-card {{
                padding: 1.05rem 1rem 1.2rem;
            }}
            .file-stats {{
                grid-template-columns: minmax(0, 1fr);
            }}
            .btn {{
                font-size: 0.88rem;
            }}
        }}

        /* Toast */
        #toast {{
            visibility: hidden;
            min-width: 240px;
            max-width: 90vw;
            background: rgba(22, 163, 74, 0.98);
            color: #ecfdf5;
            text-align: center;
            border-radius: 999px;
            padding: 0.75rem 1.4rem;
            position: fixed;
            z-index: 100;
            left: 50%;
            bottom: 22px;
            transform: translateX(-50%);
            font-size: 0.85rem;
            box-shadow: 0 8px 30px rgba(22, 163, 74, 0.55);
            opacity: 0;
            transition: opacity 0.24s ease-out, transform 0.24s ease-out;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }}

        #toast.show {{
            visibility: visible;
            opacity: 1;
            transform: translateX(-50%) translateY(-4px);
        }}

        #toast i {{
            font-size: 1rem;
        }}
    </style>
</head>
<body>

    <div class="top-bar">
        <div class="brand">
            <span class="logo-mark">Y</span>
            <span class="text-strong">YourX Stream</span>
            <span>·</span>
            <span>Fast, clean streaming</span>
        </div>
    </div>

    <main class="page">
        <div class="shell">
            <div class="grid">

                <!-- Player side -->
                <section class="player-card">
                    <div class="player-top">
                        <div class="title-wrap">
                            <div class="file-badge">
                                <i class="ri-play-circle-line"></i>
                                Now Streaming
                            </div>
                            <div class="file-heading" title="{file_name}">
                                {file_name}
                            </div>
                        </div>
                        <div class="chip">
                            <span class="chip-dot"></span>
                            Live session
                        </div>
                    </div>

                    <div class="player-wrap">
                        <div class="player-inner">
                            <video id="player" class="plyr" playsinline controls poster="{poster}">
                                <source src="{src}" type="{mime_type}" />
                                Your browser does not support HTML5 video.
                            </video>
                        </div>
                    </div>
                </section>

                <!-- Meta / actions side -->
                <aside class="meta-card">
                    <div class="meta-header">
                        <div class="meta-title">Instant stream & download</div>
                        <div class="meta-sub">
                            Secure file delivery <span class="dot"></span> Optimized for all devices
                        </div>
                    </div>

                    <div class="file-stats">
                        <div class="stat">
                            <div class="stat-label">
                                <i class="ri-hard-drive-2-line"></i>
                                File size
                            </div>
                            <div class="stat-value">{file_size}</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">
                                <i class="ri-movie-2-line"></i>
                                Media type
                            </div>
                            <div class="stat-value">{mime_type}</div>
                        </div>
                    </div>

                    <div class="actions">
                        <a href="{src}" class="btn btn-primary" download>
                            <i class="ri-download-cloud-2-line"></i>
                            Download file
                        </a>

                        <a href="vlc://{src}" class="btn btn-ghost">
                            <i class="ri-play-circle-line"></i>
                            Open in VLC
                        </a>

                        <button type="button" onclick="copyLink()" class="btn btn-ghost">
                            <i class="ri-file-copy-line"></i>
                            Copy link
                        </button>
                    </div>
                </aside>

            </div>
        </div>
    </main>

    <div id="toast">
        <i class="ri-checkbox-circle-line"></i>
        Link copied to clipboard
    </div>

    <!-- Plyr JS -->
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
            if (!navigator.clipboard) {{
                // fallback
                const textarea = document.createElement('textarea');
                textarea.value = link;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                showToast();
                return;
            }}
            navigator.clipboard.writeText(link)
                .then(showToast)
                .catch(() => showToast());
        }}

        function showToast() {{
            const toast = document.getElementById('toast');
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2600);
        }}
    </script>
</body>
</html>
"""
