import streamlit as st

st.set_page_config(
    page_title="Smriti AI",
    page_icon="🎓",
    layout="centered"
)
st.markdown("""
<style>

/* 🌈 Animated Gradient Background */
.stApp {
    background: linear-gradient(
        120deg,
        #1e3c72,
        #2a5298,
        #6dd5ed,
        #cc2b5e,
        #753a88
    );
    background-size: 400% 400%;
    animation: gradientFlow 12s ease infinite;
}

/* Gradient Animation */
@keyframes gradientFlow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ✨ Glassmorphism Cards */
div[data-testid="stContainer"] {
    background: rgba(255, 255, 255, 0.12);
    border-radius: 18px;
    padding: 18px;
    backdrop-filter: blur(12px);
    box-shadow: 0px 8px 25px rgba(0,0,0,0.25);
}

/* 🟦 Text Styling */
h1, h2, h3, h4 {
    color: white !important;
    font-family: "Poppins", sans-serif;
}

p, label, span {
    color: white !important;
    font-size: 16px;
}

/* 🎯 Buttons Modern Look */
.stButton > button {
    background: rgba(255,255,255,0.25);
    border: 1px solid rgba(255,255,255,0.4);
    border-radius: 12px;
    padding: 10px 18px;
    color: white;
    font-weight: 600;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.05);
    background: rgba(255,255,255,0.4);
}

/* 💬 Chat Message Styling */
.stChatMessage {
    background: rgba(255,255,255,0.15);
    border-radius: 15px;
    padding: 10px;
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<div style='text-align: center; padding: 25px 0;'>

<h1 style='
    font-size:clamp(18px, 2vw, 28px);
    font-weight: 900;
    color: white;
    text-shadow: 0px 0px 20px rgba(255,255,255,0.4);
'>
🎓 AI Study Companion
</h1>

<p style='
    font-size: 22px;
    color: rgba(255,255,255,0.8);
'>
Your all-in-one academic & productivity assistant
</p>

</div>
""", unsafe_allow_html=True)



st.info("""
✨ **Why this app is powerful**
- Multiple AI agents working together  
- Human-in-the-loop feedback system  
- Persistent memory using SQLite  
- Built for real student productivity  
""")

st.markdown("---")
st.subheader("Choose what you want to do")


col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("""
            <h2 style="
                font-size: 50px;
                font-weight: 900;
                color: white;
                margin-bottom: 10px;
            ">
            📖 AI Tutor
            </h2>
            """, unsafe_allow_html=True)
        st.markdown(
            "Ask doubts from PDFs, get instant answers, and generate summaries.\n\n"
            "• RAG-based doubt solving\n"
            "• Summary generation\n"
            "• Notes understanding"
        )

        if st.button("Open Tutor", use_container_width=True):
            st.switch_page("pages/4_tutor.py")

with col2:
    with st.container(border=True):
        st.markdown("""
            <h2 style="
                font-size: 50px;
                font-weight: 900;
                color: white;
                margin-bottom: 10px;
            ">
            📖 Productivity and Memory agent
            </h2>
            """, unsafe_allow_html=True)

        st.markdown(
            "Track daily work, detect backlog, and get adaptive AI feedback.\n\n"
            "• SQLite memory\n"
            "• Backlog detection\n"
            "• AI feedback & tips"
        )

        if st.button("Open Productivity Agent", use_container_width=True):
            st.switch_page("pages/1_memory.py")

col3, col4 = st.columns(2)

with col3:
    with st.container(border=True):
        st.markdown("""
            <h2 style="
                font-size: 50px;
                font-weight: 900;
                color: white;
                margin-bottom: 10px;
            ">
            📖 Smart Timetable Planner
            </h2>
            """, unsafe_allow_html=True)

        st.markdown(
            "Turn your timetable into a smart, optimized study plan.\n\n"
            "• Free slot detection\n"
            "• Topic mapping\n"
            "• Human-in-the-loop feedback"
        )

        if st.button("Open Timetable Planner", use_container_width=True):
            st.switch_page("pages/3_timetable.py")

with col4:
    with st.container(border=True):
        st.markdown("""
            <h2 style="
                font-size: 50px;
                font-weight: 900;
                color: white;
                margin-bottom: 10px;
            ">
            📖 Syllabus Analyzer
            </h2>
            """, unsafe_allow_html=True)

        st.markdown(
            "Understand syllabus, extract topics, and generate study plans.\n\n"
            "• Topic extraction\n"
            "• Resource suggestions\n"
            "• Study planning"
        )

        if st.button("Open Syllabus Planner", use_container_width=True):
            st.switch_page("pages/2_ingestion.py")

st.markdown("---")
st.caption("👈 You can also use the sidebar to navigate between pages")


import streamlit as st
import os

st.set_page_config(page_title="Focus Music", layout="centered")

# ---------------- SESSION STATE ----------------
if "music_bytes" not in st.session_state:
    st.session_state.music_bytes = None

if "music_url" not in st.session_state:
    st.session_state.music_url = None

# ---------------- TITLE ----------------
st.title("🎧 Focus Music")
st.write("Online: AI-based | Offline: Manual selection")

mode = st.radio(
    "Choose mode",
    ["Online (AI Music)", "Offline (Local Music)"]
)

# ---------------- ONLINE MODE ----------------
if mode == "Online (AI Music)":
    user_input = st.text_area(
        "How are you feeling or what are you working on?",
        placeholder="Example: sleepy, coding, exam stress"
    )

    online_music = {
        "deep_focus": {
            "label": "Deep Focus (Ambient)",
            "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"
        },
        "relaxed_focus": {
            "label": "Relaxed Focus (Lofi)",
            "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
        },
        "calm_focus": {
            "label": "Calm Piano Focus",
            "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"
        }
    }

    def ai_select_category(text):
        text = text.lower()
        if "sleep" in text or "tired" in text or "exam" in text:
            return "deep_focus"
        elif "stress" in text or "anxious" in text:
            return "calm_focus"
        else:
            return "relaxed_focus"

    if st.button("🤖 Let AI Choose Music"):
        if user_input.strip():
            key = ai_select_category(user_input)
            st.session_state.music_url = online_music[key]["url"]
            st.session_state.music_bytes = None  # reset offline

    if st.session_state.music_url:
        st.audio(st.session_state.music_url, loop=True)

# ---------------- OFFLINE MODE ----------------
else:
    st.subheader("🎵 Offline Music (Manual)")
    music_folder = "music"

    if not os.path.exists(music_folder):
        st.error("❌ 'music' folder not found")
    else:
        files = [f for f in os.listdir(music_folder) if f.endswith(".mp3")]

        if not files:
            st.warning("No MP3 files found in music folder")
        else:
            song = st.selectbox("Select a song", files)

            if st.button("▶ Play"):
                with open(os.path.join(music_folder, song), "rb") as f:
                    st.session_state.music_bytes = f.read()
                st.session_state.music_url = None  # reset online

            if st.session_state.music_bytes:
                st.audio(st.session_state.music_bytes, format="audio/mp3", loop=True)

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(-45deg,#DC143C,#FF8C00,#FFD700,#9370DB);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
</style>
""", unsafe_allow_html=True)
