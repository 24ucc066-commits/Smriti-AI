import streamlit as st
import pdfplumber
from groq import Groq

# ---------------------------
# GROQ SETUP
# ---------------------------
groq_api_key = st.secrets.get("GROQ_API_KEY")
if not groq_api_key:
    st.error("GROQ_API_KEY not found in secrets.toml")
    st.stop()

client = Groq(api_key=groq_api_key)

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
    return text

# ---------------------------
# GROQ HELPERS (NO LANGCHAIN)
# ---------------------------
def groq_call(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are an academic syllabus analysis assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def extract_topics(text):
    prompt = f"""
From the syllabus text below:
- Identify subjects
- List important topics chapter-wise
- Present output as a clean markdown table

SYLLABUS:
{text}
"""
    return groq_call(prompt)

def suggest_resources(text):
    prompt = f"""
Based on the following syllabus:
- Suggest best books
- Paid & free online courses
- Trusted YouTube channels (academic only)

SYLLABUS:
{text}
"""
    return groq_call(prompt)

def give_tips(text):
    prompt = f"""
Based on the syllabus below:
- Give subject-wise study tips
- Explain how each subject helps in placements

SYLLABUS:
{text}
"""
    return groq_call(prompt)

def generate_study_plan(text):
    prompt = f"""
Create a WEEK-WISE study plan in a markdown table.

Rules:
1. Leave 1 week for mid-sem after half syllabus
2. Leave 1 week for end-sem after full syllabus
3. Prioritize important topics
4. Distribute topics evenly

SYLLABUS:
{text}
"""
    return groq_call(prompt)

# ---------------------------
# UI STYLES
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

# ---------------------------
# MAIN UI
# ---------------------------
st.title("🎓 Academic Syllabus Assistant")
st.write(
    "Upload your syllabus PDF and instantly get **important topics, resources, tips, and a smart study plan**."
)

st.divider()
st.markdown("### 📄 Upload Your Syllabus")

uploaded_pdf = st.file_uploader(
    "Choose a PDF file",
    type="pdf",
    label_visibility="collapsed"
)

if uploaded_pdf:
    with st.spinner("Extracting syllabus..."):
        syllabus_text = load_pdf(uploaded_pdf)

    st.success("Syllabus processed successfully! ✅")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📚 Important Topics",
        "🎯 Resources",
        "💡 Study Tips",
        "📅 Study Plan"
    ])

    with tab1:
        st.subheader("📚 Important Topics")
        if st.button("Extract Topics"):
            with st.spinner("Analyzing syllabus..."):
                topics = extract_topics(syllabus_text)
            st.markdown(topics)

    with tab2:
        st.subheader("🎯 Learning Resources")
        if st.button("Suggest Resources"):
            with st.spinner("Finding best resources..."):
                resources = suggest_resources(syllabus_text)
            st.markdown(resources)

    with tab3:
        st.subheader("💡 Study Tips & Career Relevance")
        if st.button("Get Tips"):
            with st.spinner("Generating tips..."):
                tips = give_tips(syllabus_text)
            st.markdown(tips)

    with tab4:
        st.subheader("📅 Personalized Study Plan")
        if st.button("Generate Plan"):
            with st.spinner("Creating study plan..."):
                plan = generate_study_plan(syllabus_text)
            with st.container(border=True):
                st.markdown(plan)
