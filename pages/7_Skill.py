import streamlit as st
import os
import random
from groq import Groq

# ----------------------------
# Streamlit Setup
# ----------------------------
st.set_page_config(page_title="Skill Development Agent", layout="wide")

# ----------------------------
# Offline Skills
# ----------------------------
OFFLINE_SKILLS = {
    "Python": {
        "cheatsheet": "Python basics:\n- Variables\n- Loops\n- Functions\n- Lists & Dictionaries",
        "practice": [
            "Write a function to reverse a string",
            "Create a list of even numbers from 1 to 50",
            "Write a program to check palindrome"
        ]
    },
    "Communication Skills": {
        "cheatsheet": "Communication basics:\n- Clarity\n- Confidence\n- Active listening",
        "practice": [
            "Introduce yourself in 30 seconds",
            "Explain your favorite movie",
            "Practice saying NO politely"
        ]
    }
}

# ----------------------------
# Session State Init
# ----------------------------
if "question" not in st.session_state:
    st.session_state.question = ""

if "game_started" not in st.session_state:
    st.session_state.game_started = False

# ----------------------------
# Title
# ----------------------------
st.title("🚀 Skill Development Agent")
st.caption("Learn skills offline 📚 | Play & learn online 🎮")

# ----------------------------
# Mode Selection
# ----------------------------
mode = st.radio("Select Mode", ["Offline Mode", "Online Mode"])
skill = st.selectbox("Choose a Skill", list(OFFLINE_SKILLS.keys()))

# ----------------------------
# OFFLINE MODE
# ----------------------------
if mode == "Offline Mode":
    st.subheader("📴 Offline Learning Mode")
    st.code(OFFLINE_SKILLS[skill]["cheatsheet"])
    st.info(random.choice(OFFLINE_SKILLS[skill]["practice"]))

# ----------------------------
# ONLINE MODE (GROQ SDK)
# ----------------------------
else:
    st.subheader("🌐 Online Game-Based Learning")

    groq_api_key = st.secrets.get("GROQ_API_KEY")
    if not groq_api_key:
        st.error("GROQ_API_KEY not found in secrets.toml")
        st.stop()

    client = Groq(api_key=groq_api_key)

    def groq_call(prompt, system="You are an interactive learning game master."):
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    game_type = st.selectbox(
        "Choose Learning Game",
        ["Quiz Challenge", "Role Play", "Problem Solving Game"]
    )

    # ----------------------------
    # START GAME
    # ----------------------------
    if st.button("Start Game 🎮"):
        st.session_state.game_started = True

        question_prompt = f"""
Skill: {skill}
Game Type: {game_type}

Generate ONE clear question or challenge.
Do NOT give the answer.
Keep it short and engaging.
"""

        st.session_state.question = groq_call(question_prompt)

    # ----------------------------
    # SHOW QUESTION
    # ----------------------------
    if st.session_state.game_started:
        st.markdown("### 🎯 Challenge")
        st.info(st.session_state.question)

        user_answer = st.text_input("Your Response")

        # ----------------------------
        # SUBMIT ANSWER
        # ----------------------------
        if st.button("Submit Answer"):
            feedback_prompt = f"""
Skill: {skill}
Game Type: {game_type}

Question:
{st.session_state.question}

Student Answer:
{user_answer}

Now:
1. Say if the answer is correct or not
2. Explain WHY
3. Give a better version if needed
4. Motivate the student
"""

            feedback = groq_call(
                feedback_prompt,
                system="You are a strict but friendly skill coach."
            )

            st.markdown("### 🤖 AI Feedback")
            st.success(feedback)


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
