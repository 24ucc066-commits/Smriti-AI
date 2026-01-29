import streamlit as st
import pdfplumber
import uuid
import os
from groq import Groq
from collections import Counter

# ---------------------------
# GROQ SETUP
# ---------------------------
groq_api_key = st.secrets.get("GROQ_API_KEY")
if not groq_api_key:
    st.error("GROQ_API_KEY missing in secrets.toml")
    st.stop()

client = Groq(api_key=groq_api_key)

def groq_call(prompt, system="You are a helpful academic tutor."):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# ---------------------------
# SESSION STATE
# ---------------------------
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "chat_threads" not in st.session_state:
    st.session_state.chat_threads = []

if "chat_store" not in st.session_state:
    st.session_state.chat_store = {}

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_names" not in st.session_state:
    st.session_state.thread_names = {}

if st.session_state.thread_id not in st.session_state.chat_threads:
    st.session_state.chat_threads.append(st.session_state.thread_id)

# ---------------------------
# HELPERS
# ---------------------------
def reset_chat():
    tid = str(uuid.uuid4())
    st.session_state.thread_id = tid
    st.session_state.chat_threads.append(tid)
    st.session_state.messages = []
    st.session_state.thread_names[tid] = f"💬 Chat {len(st.session_state.chat_threads)}"

def load_conversation(tid):
    return st.session_state.chat_store.get(tid, [])

# ---------------------------
# PDF LOADING
# ---------------------------
def load_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text.strip()

# ---------------------------
# SIMPLE RAG (NO EMBEDDINGS)
# ---------------------------
def chunk_text(text, size=500):
    words = text.split()
    return [" ".join(words[i:i+size]) for i in range(0, len(words), size)]

def keyword_score(chunk, question):
    q_words = Counter(question.lower().split())
    c_words = Counter(chunk.lower().split())
    return sum((q_words & c_words).values())

def retrieve_chunks(chunks, question, k=3):
    scored = [(chunk, keyword_score(chunk, question)) for chunk in chunks]
    scored = sorted(scored, key=lambda x: x[1], reverse=True)
    return [c for c, s in scored[:k] if s > 0]

def confidence_score(chunks):
    if not chunks:
        return 30
    return min(95, 60 + len(chunks) * 10)

# ---------------------------
# AI FUNCTIONS
# ---------------------------
def answer_question(context, question):
    prompt = f"""
Use the following context to answer the question.

Context:
{context}

Question:
{question}
"""
    return groq_call(prompt)

def generate_summary(text):
    prompt = f"""
Create a clear academic summary from the following notes.

{text}
"""
    return groq_call(prompt, system="You summarize academic notes.")

# ---------------------------
# UI STYLES
# ---------------------------
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
# SIDEBAR
# ---------------------------
st.sidebar.title("📂 Your Tutor Chats")

if st.sidebar.button("➕ New Chat"):
    reset_chat()
    st.rerun()

st.sidebar.subheader("My Conversations")

for tid in st.session_state.chat_threads[::-1]:
    name = st.session_state.thread_names.get(tid, tid[:8])
    if st.sidebar.button(name):
        st.session_state.thread_id = tid
        st.session_state.messages = load_conversation(tid)
        st.rerun()

# ---------------------------
# MAIN UI
# ---------------------------
st.title("📖 Your Tutor")
st.write("Ask questions from your notes or generate a summary.")

uploaded_pdf = st.file_uploader("Upload Notes PDF", type="pdf")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if uploaded_pdf:
    text = load_pdf(uploaded_pdf)
    chunks = chunk_text(text)
    st.success("PDF processed successfully!")

    if st.session_state.thread_id not in st.session_state.thread_names:
        base = os.path.splitext(uploaded_pdf.name)[0]
        st.session_state.thread_names[st.session_state.thread_id] = f"📘 {base}"

    option = st.radio("Choose Action", ["ASK DOUBTS", "GENERATE SUMMARY"])

    if option == "ASK DOUBTS":
        question = st.chat_input("Ask your doubt")
        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            relevant = retrieve_chunks(chunks, question)
            context = "\n\n".join(relevant)
            confidence = confidence_score(relevant)

            with st.chat_message("assistant"):
                answer = answer_question(context, question)
                st.markdown(answer)
                st.markdown(f"### ✅ Confidence Score: **{confidence}%**")
                if confidence < 60:
                    st.warning("⚠ Answer may be less reliable due to weak context match.")

            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.session_state.chat_store[st.session_state.thread_id] = st.session_state.messages

    elif option == "GENERATE SUMMARY":
        if st.button("GENERATE SUMMARY"):
            summary = generate_summary(text)
            st.markdown(summary)
