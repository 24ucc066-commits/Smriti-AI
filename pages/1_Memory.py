import sqlite3
from datetime import date
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from groq import Groq

# ---------------------------
# GROQ SETUP (CORRECT)
# ---------------------------
groq_api_key = st.secrets.get("GROQ_API_KEY")
if not groq_api_key:
    st.error("GROQ_API_KEY not found in secrets.toml")
    st.stop()

client = Groq(api_key=groq_api_key)

# ---------------------------
# DATABASE
# ---------------------------
def get_connection():
    return sqlite3.connect("memory.db")

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS progress(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT,
            planned_hours INTEGER,
            worked_hours INTEGER,
            task TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def insert_progress(day, planned, worked, task):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO progress (day, planned_hours, worked_hours, task) VALUES (?, ?, ?, ?)",
        (day, planned, worked, task)
    )
    conn.commit()
    conn.close()

def fetch_all():
    conn = get_connection()
    data = conn.execute("SELECT * FROM progress").fetchall()
    conn.close()
    return data

# ---------------------------
# STYLES
# ---------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        -45deg,
        #DC143C,
        #FF8C00,
        #FFD700,
        #9370DB
    );
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

st.markdown("""
<style>
@keyframes slideUp {
    from { transform: translateY(30px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}
.slide-up {
    animation: slideUp 0.8s ease-out;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="slide-up">
<p>Welcome back! Here's your progress 👋</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# GROQ FEEDBACK AGENT (FIXED)
# ---------------------------
def feedback_agent(summary: str) -> str:
    prompt = f"""
You are a productivity feedback agent.

User data:
{summary}

Give the following with proper labels:
1. Honest feedback
2. Performance track (on track / warning / critical)
3. Whether workload should be reduced
4. Suggested plan for next 3 days
5. 2 simple productivity tips
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful productivity coach."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# ---------------------------
# UI
# ---------------------------
st.title("Memory Productivity Agent 🧠")
st.header("Daily Progress Check-in 📚")

with st.form("daily_form"):
    today = st.date_input("Date", date.today())
    task = st.text_input("What did you work on?")
    planned = st.number_input("Planned Hours", 1, 12, 4)
    worked = st.number_input("Worked Hours", 0, 12, 2)
    submit = st.form_submit_button("Save Progress")

if submit:
    insert_progress(str(today), planned, worked, task)
    st.success("Progress saved successfully! ✅")

# ---------------------------
# DATA ANALYSIS
# ---------------------------
data = fetch_all()
if not data:
    st.info("No data yet. Start logging your progress.")
    st.stop()

df = pd.DataFrame(
    data,
    columns=["id", "day", "planned_hours", "worked_hours", "task"]
)

df["backlog"] = (df["planned_hours"] - df["worked_hours"]).clip(lower=0)
total_backlog = df["backlog"].sum()

if total_backlog <= 2:
    status = "On track"
elif total_backlog <= 6:
    status = "Warning"
else:
    status = "Critical"

trend = (
    "Improving"
    if df["worked_hours"].tail(3).mean()
    > df["planned_hours"].tail(3).mean()
    else "Declining"
)

st.subheader("Performance Summary")
st.write(f"**Total Backlog:** {total_backlog} hours")
st.write(f"**Trend:** {trend}")
st.write(f"**Status:** {status}")

summary = f"""
Total backlog hours: {total_backlog}
Trend: {trend}
Performance status: {status}
"""

# ---------------------------
# FEEDBACK
# ---------------------------
st.header("🤖 Feedback Agent")

if st.button("Get Feedback"):
    with st.spinner("Generating feedback..."):
        feedback = feedback_agent(summary)
    st.markdown(feedback)

# ---------------------------
# AI ADVICE
# ---------------------------
st.header("AI Productivity Advice")

if status == "Critical":
    st.warning("⚠️ Workload automatically reduced")
    st.write("➡️ Suggested daily workload: **2 hours**")
elif status == "Warning":
    st.info("⚠️ Slight adjustment recommended")
    st.write("➡️ Suggested daily workload: **3–4 hours**")
else:
    st.success("✅ You are doing well!")
    st.write("➡️ Suggested daily workload: **4–5 hours**")

# ---------------------------
# VISUALIZATION
# ---------------------------
st.header("Progress Visualization 📊")

df["day"] = pd.to_datetime(df["day"])
df = df.sort_values("day")

fig, ax = plt.subplots()
x = range(len(df))
width = 0.35

ax.bar(
    [i - width / 2 for i in x],
    df["planned_hours"],
    width=width,
    label="Planned"
)
ax.bar(
    [i + width / 2 for i in x],
    df["worked_hours"],
    width=width,
    label="Worked"
)

ax.set_xlabel("Date")
ax.set_ylabel("Hours")
ax.set_xticks(x)
ax.set_xticklabels(df["day"].dt.strftime("%Y-%m-%d"), rotation=45)
ax.legend()

st.pyplot(fig)
