import streamlit as st
import random
import os
import re

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(
    page_title="Motivation Buddy 💙",
    page_icon="💙",
    layout="centered"
)

st.title("💙 Motivation Buddy")
st.caption("A friendly space to vent, relax, and feel understood")

# ======================
# MODE SELECTION
# ======================
mode = st.radio(
    "Choose response mode:",
    ["Offline (No Internet)", "Online (Friendly AI – Remembers Chat)"],
    horizontal=True
)

# ======================
# CHAT MEMORY
# ======================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ======================
# LANGUAGE DETECTION
# ======================
def detect_language(text):
    if re.search(r'[\u0900-\u097F]', text):
        return "hinglish"
    return "english"

# ======================
# OFFLINE RESPONSES
# ======================
OFFLINE_RESPONSES = {
    "english": [
        "Hey, take a breath. You’re not failing — you’re learning under pressure.",
        "It’s okay to feel overwhelmed. This phase will pass.",
        "You’ve handled tough moments before. You’ll handle this too."
    ],
    "hinglish": [
        "Yaar, thoda sa ruk aur saans le. Sab ek saath solve karna zaroori nahi.",
        "Pressure feel hona normal hai — matlab tu honestly try kar raha hai.",
        "Tu akela nahi hai. Dheere dheere sab theek ho jaayega."
    ]
}

# ======================
# GROQ LLM (ONLINE MODE)
# ======================
def groq_response(messages, lang):
    from groq import Groq
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    if lang == "hinglish":
        system_prompt = (
            "You are a friendly, supportive motivation buddy for students. "
            "Reply in Hinglish (Hindi + English mix). "
            "Talk like a caring senior or friend. "
            "Be empathetic, calm, and conversational. Avoid lectures."
        )
    else:
        system_prompt = (
            "You are a friendly, supportive motivation buddy for students. "
            "Reply in English. "
            "Talk like a caring senior or friend. "
            "Be empathetic, calm, and conversational. Avoid lectures."
        )

    chat = [{"role": "system", "content": system_prompt}]
    chat.extend(messages)

    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=chat,
        temperature=0.75,
        max_tokens=250
    )

    return completion.choices[0].message.content

# ======================
# CHAT DISPLAY
# ======================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ======================
# INPUT BOX (CHAT STYLE)
# ======================
user_input = st.chat_input("Type how you're feeling… (Hindi or English)")

if user_input:
    lang = detect_language(user_input)

    # Show user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.write(user_input)

    # Generate response
    if mode.startswith("Online") and "GROQ_API_KEY" in os.environ:
        reply = groq_response(st.session_state.messages, lang)
    else:
        reply = random.choice(OFFLINE_RESPONSES[lang])

    # Show assistant message
    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )

    with st.chat_message("assistant"):
        st.write(reply)

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
