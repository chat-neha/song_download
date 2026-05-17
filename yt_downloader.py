import streamlit as st
import os
import re
from pathlib import Path

# --- Page Config ---
st.set_page_config(
    page_title="YT Downloader",
    page_icon="🎵",
    layout="centered"
)

# --- Custom CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

.stApp {
    background: #0d0d0d;
    color: #f0f0f0;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
}

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ff0000 0%, #ff6b35 50%, #ffcc00 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    margin-bottom: 0.2rem;
    letter-spacing: -1px;
}

.hero-sub {
    text-align: center;
    color: #888;
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    margin-bottom: 2.5rem;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
}

.stTextInput > div > div > input {
    background: #111 !important;
    border: 1.5px solid #333 !important;
    border-radius: 10px !important;
    color: #f0f0f0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.9rem !important;
    padding: 0.75rem 1rem !important;
}

.stTextInput > div > div > input:focus {
    border-color: #ff0000 !important;
    box-shadow: 0 0 0 2px rgba(255,0,0,0.15) !important;
}

.stRadio > div {
    flex-direction: row !important;
    gap: 1rem;
}

.stRadio label {
    color: #ccc !important;
}

div[data-testid="stRadio"] > div {
    display: flex;
    gap: 1.5rem;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #ff0000, #cc0000) !important;
    color: white !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 2rem !important;
    letter-spacing: 1px;
    text-transform: uppercase;
    transition: all 0.2s ease;
    cursor: pointer;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #ff3333, #ff0000) !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(255,0,0,0.3) !important;
}

.stDownloadButton > button {
    width: 100%;
    background: linear-gradient(135deg, #1db954, #17a145) !important;
    color: white !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 2rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.stSuccess {
    background: #0f2d1a !important;
    border: 1px solid #1db954 !important;
    border-radius: 10px !important;
    color: #1db954 !important;
}

.stError {
    background: #2d0f0f !important;
    border: 1px solid #ff4444 !important;
    border-radius: 10px !important;
}

.stWarning {
    border-radius: 10px !important;
}

.stInfo {
    background: #0f1a2d !important;
    border: 1px solid #3399ff !important;
    border-radius: 10px !important;
}

.label-text {
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 0.4rem;
}

.divider {
    border: none;
    border-top: 1px solid #222;
    margin: 1.5rem 0;
}

.footer {
    text-align: center;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: #444;
    margin-top: 3rem;
    letter-spacing: 1px;
}

.badge {
    display: inline-block;
    background: #222;
    border: 1px solid #333;
    border-radius: 6px;
    padding: 2px 10px;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: #888;
    margin: 0 4px;
}
</style>
""", unsafe_allow_html=True)


# --- Helpers ---
def is_valid_youtube_url(url: str) -> bool:
    patterns = [
        r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+',
        r'(https?://)?(www\.)?youtube\.com/shorts/[\w-]+'
    ]
    return any(re.search(p, url) for p in patterns)


def download_video(url: str, fmt: str, output_dir: str) -> tuple[bool, str, str]:
    """
    Returns (success, filepath_or_error, title)
    """
    try:
        from pytubefix import YouTube
        yt = YouTube(url)
        title = yt.title
        safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')

        if fmt == "mp4":
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').last()
            if not stream:
                return False, "No MP4 stream found for this video.", title
            filepath = stream.download(output_path=output_dir, filename=f"{safe_title}.mp4")
            return True, filepath, title

        else:  # mp3
            # Download audio-only stream
            stream = yt.streams.filter(only_audio=True).order_by('abr').last()
            if not stream:
                return False, "No audio stream found for this video.", title
            filepath = stream.download(output_path=output_dir, filename=f"{safe_title}.mp4")
            # Rename to .mp3
            mp3_path = filepath.replace('.mp4', '.mp3')
            os.rename(filepath, mp3_path)
            return True, mp3_path, title

    except ImportError:
        return False, "pytube is not installed. Run: pip install pytube", ""
    except Exception as e:
        return False, str(e), ""


# --- UI ---
st.markdown('<div class="hero-title">⬇ YT DOWNLOADER</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Download YouTube videos as MP3 or MP4 — fast & free</div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="label-text">🔗 YouTube URL</div>', unsafe_allow_html=True)
    url = st.text_input(
        label="url",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed"
    )

    hr = st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown('<div class="label-text">🎚 Format</div>', unsafe_allow_html=True)
    fmt = st.radio(
        label="format",
        options=["mp3", "mp4"],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("")
    download_btn = st.button("Download Now →", use_container_width=True)


# --- Logic ---
if download_btn:
    if not url.strip():
        st.error("Please enter a YouTube URL.")
    elif not is_valid_youtube_url(url.strip()):
        st.warning("That doesn't look like a valid YouTube URL. Please check and try again.")
    else:
        with st.spinner(f"Fetching and downloading as **{fmt.upper()}**..."):
            output_dir = "/tmp/yt_downloads"
            os.makedirs(output_dir, exist_ok=True)
            success, result, title = download_video(url.strip(), fmt, output_dir)

        if success:
            st.success(f"✅ Downloaded: **{title}**")
            with open(result, "rb") as f:
                file_bytes = f.read()
            filename = Path(result).name
            mime = "audio/mpeg" if fmt == "mp3" else "video/mp4"
            st.download_button(
                label=f"⬇ Save {filename}",
                data=file_bytes,
                file_name=filename,
                mime=mime,
                use_container_width=True
            )
            # Cleanup
            try:
                os.remove(result)
            except Exception:
                pass
        else:
            st.error(f"❌ Download failed: {result}")
            if "pytube" in result.lower():
                st.info("Install pytube with: `pip install pytube`")

st.markdown("""
<div class="footer">
    <span class="badge">pytube</span>
    <span class="badge">streamlit</span>
    <span class="badge">python</span>
    <br><br>
    For personal use only. Respect copyright and YouTube's Terms of Service.
</div>
""", unsafe_allow_html=True)
