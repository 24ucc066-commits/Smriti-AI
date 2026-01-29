import streamlit as st
import os

st.set_page_config(page_title="Focus Music", layout="centered")

st.title("🎧 Focus Music")
st.write("Online: AI-based | Offline: Manual selection")

# ---------------- MODE ----------------
mode = st.radio(
    "Choose mode",
    ["Online (AI Music)", "Offline (Local Music)"]
)

# ---------------- ONLINE (AI) ----------------
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
        if user_input.strip() == "":
            st.warning("Please enter how you feel.")
        else:
            category = ai_select_category(user_input)
            selected = online_music[category]

            st.success(f"AI selected: **{selected['label']}**")
            st.audio(selected["url"])

# ---------------- OFFLINE (NO AI) ----------------
else:
    st.subheader("🎵 Offline Music (Manual)")

    music_folder = "music"

    if not os.path.exists(music_folder):
        st.error("Music folder not found.")
    else:
        files = [f for f in os.listdir(music_folder) if f.endswith(".mp3")]

        if not files:
            st.warning("No MP3 files found in music folder.")
        else:
            song = st.selectbox("Select a song", files)

            with open(os.path.join(music_folder, song), "rb") as f:
                st.audio(f.read(), format="audio/mp3")


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