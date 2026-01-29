import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from pypdf import PdfReader
from groq import Groq
import os

# --------------------------------------------------
# GROQ SETUP
# --------------------------------------------------
groq_api_key = st.secrets.get("GROQ_API_KEY")
if not groq_api_key:
    st.error("GROQ_API_KEY not found in secrets.toml")
    st.stop()

client = Groq(api_key=groq_api_key)

def groq_call(prompt, system="You are an expert exam mentor."):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )
    return response.choices[0].message.content

# --------------------------------------------------
# STREAMLIT PAGE SETUP
# --------------------------------------------------
st.set_page_config(
    page_title="Smriti AI – Exam Agent",
    page_icon="📘",
    layout="wide"
)

st.title("📘 Smriti AI – Intelligent Exam Preparation Agent")
st.caption("Quick Revision • Mind Maps • Practice Questions • Exam Strategy")

# --------------------------------------------------
# PDF TEXT EXTRACTION
# --------------------------------------------------
def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text

# --------------------------------------------------
# AI FEATURES
# --------------------------------------------------
def quick_revision(syllabus):
    return groq_call(f"""
Generate a 10-minute quick revision.

Focus on:
- Important concepts
- Definitions
- Formulas
- Frequently asked exam points

Syllabus:
{syllabus}
""")

def mind_map_structure(syllabus):
    return groq_call(f"""
Convert the syllabus into a mind map structure.

Rules:
- Use '->' for hierarchy
- Keep node names short
- Output ONLY structure

Example:
Topic
Topic -> Subtopic
Subtopic -> Point

Syllabus:
{syllabus}
""", system="You generate structured academic mind maps.")

def practice_questions(syllabus):
    return groq_call(f"""
Generate exam-oriented practice questions.

For each question mention:
- Difficulty (Easy/Medium/Hard)
- Expected marks
- Time to attempt

Syllabus:
{syllabus}
""")

def exam_strategy(syllabus, instructions):
    return groq_call(f"""
Based on the syllabus and exam instructions:

Suggest:
- Time management strategy
- Section-wise attempt order
- Common mistakes
- Final revision tips

Syllabus:
{syllabus}

Exam Instructions:
{instructions}
""", system="You are an exam strategy expert.")

def evaluate_answers(questions, user_answers):
    return groq_call(f"""
Evaluate the student's answers.

Tasks:
1. Check correctness and clarity
2. Give score out of 10
3. Short feedback (2–3 lines)
4. End with ONE motivational sentence

Practice Questions:
{questions}

User Answers:
{user_answers}

Output format:
Score: X/10
Feedback:
- ...
- ...

Motivation:
"..."
""", system="You are a fair and encouraging exam evaluator.")

# --------------------------------------------------
# MIND MAP IMAGE
# --------------------------------------------------
def generate_mind_map_image(text):
    G = nx.DiGraph()

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if "->" in line:
            parent, child = [x.strip() for x in line.split("->")]
            G.add_edge(parent, child)
        else:
            G.add_node(line)

    plt.figure(figsize=(16, 12))
    pos = nx.spring_layout(G, seed=42, k=0.9)

    nx.draw(
        G, pos,
        with_labels=True,
        node_size=3500,
        node_color="#AED6F1",
        edge_color="#5D6D7E",
        font_size=9,
        font_weight="bold"
    )

    st.pyplot(plt)
    plt.close()

# --------------------------------------------------
# UI – INPUT
# --------------------------------------------------
st.header("1️⃣ Provide Syllabus (Text or PDF)")

text_syllabus = st.text_area(
    "✍️ Paste syllabus (optional)",
    height=180,
    placeholder="Binary Trees, Graph Algorithms, OS Scheduling..."
)

uploaded_pdf = st.file_uploader("📄 Upload syllabus PDF", type=["pdf"])

syllabus = ""
if uploaded_pdf:
    with st.spinner("Extracting text from PDF..."):
        syllabus += extract_text_from_pdf(uploaded_pdf)
        st.success("PDF syllabus loaded ✔")

if text_syllabus.strip():
    syllabus += "\n" + text_syllabus

if not syllabus.strip():
    st.info("Please paste syllabus or upload PDF to continue.")

st.divider()

# --------------------------------------------------
# UI – TOOLS
# --------------------------------------------------
st.header("2️⃣ Exam Preparation Tools")

col1, col2 = st.columns(2)

with col1:
    if st.button("⚡ 10-Minute Quick Revision") and syllabus.strip():
        with st.spinner("Preparing quick revision..."):
            st.subheader("📌 Quick Revision")
            st.write(quick_revision(syllabus))

    if st.button("🗺️ Generate Mind Map"):
        with st.spinner("Creating mind map..."):
            structure = mind_map_structure(syllabus)
            generate_mind_map_image(structure)
            with st.expander("Raw structure"):
                st.text(structure)

with col2:
    if st.button("🔥 Practice Questions") and syllabus.strip():
        with st.spinner("Generating questions..."):
            st.session_state["questions"] = practice_questions(syllabus)
        st.subheader("📝 Practice Questions")
        st.write(st.session_state["questions"])

# --------------------------------------------------
# ANSWER EVALUATION
# --------------------------------------------------
if "questions" in st.session_state:
    st.subheader("✍️ Answer the Questions")
    user_answers = st.text_area("Write answers", height=200)

    if st.button("✅ Submit Answers"):
        with st.spinner("Evaluating..."):
            result = evaluate_answers(
                st.session_state["questions"],
                user_answers
            )
        st.subheader("📊 Evaluation Result")
        st.write(result)

st.divider()

# --------------------------------------------------
# STRATEGY
# --------------------------------------------------
st.header("3️⃣ Exam Strategy Generator")

instructions = st.text_area(
    "Paste exam instructions",
    height=180,
    placeholder="3 hours exam, Section A compulsory..."
)

if st.button("🧠 Generate Exam Strategy"):
    if syllabus.strip() and instructions.strip():
        with st.spinner("Generating strategy..."):
            st.subheader("🎯 Exam Strategy")
            st.write(exam_strategy(syllabus, instructions))
    else:
        st.warning("Please enter syllabus and instructions.")

st.divider()
st.caption("🚀 Smriti AI | Mind Maps via NetworkX | Groq-powered | No LangChain")


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
