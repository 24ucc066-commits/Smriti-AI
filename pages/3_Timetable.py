import streamlit as st
import pdfplumber
import sqlite3
from groq import Groq

# ---------------------------
# GROQ SETUP
# ---------------------------
groq_api_key = st.secrets.get("GROQ_API_KEY")
if not groq_api_key:
    st.error("GROQ_API_KEY not found in secrets.toml")
    st.stop()

client = Groq(api_key=groq_api_key)

def groq_call(prompt, system="You are a helpful student productivity assistant."):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# ---------------------------
# DATABASE (FEEDBACK MEMORY)
# ---------------------------
def init_feedback_db():
    conn = sqlite3.connect("memory.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS plan_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_type TEXT,
            user_feedback TEXT,
            user_action TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_feedback_db()

def save_feedback(plan_type, feedback, action):
    conn = sqlite3.connect("memory.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO plan_feedback (plan_type, user_feedback, user_action) VALUES (?, ?, ?)",
        (plan_type, feedback, action)
    )
    conn.commit()
    conn.close()

def fetch_feedback():
    conn = sqlite3.connect("memory.db")
    data = conn.execute(
        "SELECT user_action, user_feedback FROM plan_feedback ORDER BY id DESC LIMIT 5"
    ).fetchall()
    conn.close()
    return data

# ---------------------------
# PDF TEXT EXTRACTION
# ---------------------------
def load_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
            else:
                table = page.extract_table()
                if table:
                    for row in table:
                        text += " | ".join([cell if cell else "" for cell in row]) + "\n"
    return text.strip()

# ---------------------------
# AI FUNCTIONS (NO LANGCHAIN)
# ---------------------------
def parse_timetable(text):
    prompt = f"""
Extract a student timetable from the text below.

Identify:
- Day
- Start time
- End time
- Subject
- Type (class/lab)

Return a clean, readable MARKDOWN TABLE.

TEXT:
{text}
"""
    return groq_call(prompt, system="You extract structured timetables from messy text.")

def generate_plan(timetable, feedback_memory):
    prompt = f"""
You are a student productivity coach.

Student Timetable:
{timetable}

Past User Feedback:
{feedback_memory or "No previous feedback"}

Rules:
- Avoid patterns the user rejected
- Improve what the user approved
- Be realistic and balanced

Generate an improved WEEKLY STUDY PLAN as a markdown table.
"""
    return groq_call(prompt, system="You design realistic study plans.")

def explain_plan(timetable, weekly_plan, feedback_memory):
    prompt = f"""
Explain WHY the following study plan was created.

Timetable:
{timetable}

Weekly Plan:
{weekly_plan}

Past Feedback Used:
{feedback_memory}

Explain in bullet points:
- How free slots were chosen
- Why workload varies
- How feedback influenced the plan
- Overall strategy
"""
    return groq_call(prompt, system="You explain plans clearly to students.")

def chat(timetable, question):
    prompt = f"""
Student Timetable:
{timetable}

Question:
{question}

Give a friendly, practical answer.
"""
    return groq_call(prompt, system="You are a friendly student assistant.")

def map_topics_to_free_slots(timetable, weekly_plan):
    prompt = f"""
You are an AI study planner.

Using:
1. Student timetable
2. Weekly study plan

Assign topics to free slots.

Rules:
- Light topics for short slots
- Heavy topics for long slots
- After labs → revision/light work
- Add short advice per slot

Return a MARKDOWN TABLE with:
Day | Free Slot | Topic | Study Type | Advice

Timetable:
{timetable}

Weekly Plan:
{weekly_plan}
"""
    return groq_call(prompt, system="You map study topics to free time.")

# ---------------------------
# UI
# ---------------------------
st.title("📅 Smart Timetable Feedback Agent")
st.caption("Human-in-the-loop AI timetable planner")

tab1, tab2 = st.tabs(["Upload PDF", "Write Timetable"])

if "raw_text" not in st.session_state:
    st.session_state["raw_text"] = ""

with tab1:
    pdf = st.file_uploader("Upload timetable PDF", type=["pdf"])
    if pdf:
        st.session_state["raw_text"] = load_pdf(pdf)
        if not st.session_state["raw_text"]:
            st.error("❌ No readable text found (scanned PDF).")
            st.stop()

        st.subheader("📄 Extracted Text Preview")
        st.text_area("Preview", st.session_state["raw_text"][:2000], height=200)

with tab2:
    typed_text = st.text_area("Write timetable in any format")
    if typed_text.strip():
        st.session_state["raw_text"] = typed_text

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

# ---------------------------
# GENERATION PIPELINE
# ---------------------------
if st.button("Generate Smart Timetable"):
    raw_text = st.session_state["raw_text"]
    if not raw_text.strip():
        st.error("❌ Please upload or enter timetable")
        st.stop()

    with st.spinner("Understanding your timetable..."):
        timetable = parse_timetable(raw_text)
    st.subheader("📘 Extracted Timetable")
    st.markdown(timetable)

    past_feedback = fetch_feedback()
    feedback_text = "\n".join([f"- {a.upper()}: {t}" for a, t in past_feedback])

    with st.spinner("Optimizing your week..."):
        weekly_plan = generate_plan(timetable, feedback_text)
    st.subheader("🗓️ Weekly Study Plan")
    st.markdown(weekly_plan)

    with st.spinner("Explaining the plan..."):
        explanation = explain_plan(timetable, weekly_plan, feedback_text)
    st.subheader("🧐 Why This Plan?")
    with st.expander("See explanation"):
        st.markdown(explanation)

    with st.spinner("Mapping topics to free slots..."):
        slot_plan = map_topics_to_free_slots(timetable, weekly_plan)
    st.subheader("🧠 Slot-wise Action Plan")
    st.markdown(slot_plan)

    st.session_state.update({
        "weekly_plan": weekly_plan,
        "timetable": timetable,
        "slot_plan": slot_plan
    })

# ---------------------------
# FEEDBACK LOOP
# ---------------------------
st.subheader("📝 Your Feedback")

user_change = st.text_area("✏️ What should be changed?")
reason = st.text_area("❌ Why didn’t this work?")

c1, c2, c3 = st.columns(3)

with c1:
    if st.button("✅ Approve"):
        save_feedback("timetable_plan", "Approved", "approved")
        st.success("Future plans will follow this style.")

with c2:
    if st.button("✏️ Modify") and user_change.strip():
        save_feedback("timetable_plan", user_change, "modified")
        st.info("Got it. I’ll improve future plans.")

with c3:
    if st.button("❌ Reject") and reason.strip():
        save_feedback("timetable_plan", reason, "rejected")
        st.warning("Understood. I’ll avoid this approach.")

# ---------------------------
# CHAT
# ---------------------------
st.subheader("💬 Chat with your Timetable AI")
user_q = st.text_input("Ask anything about your schedule")

if user_q and "timetable" in st.session_state:
    st.info(chat(st.session_state["timetable"], user_q))
