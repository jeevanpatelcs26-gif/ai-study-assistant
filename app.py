import os
import streamlit as st
from pypdf import PdfReader
from google import genai
from google.genai import types

st.set_page_config(page_title="Study Assistant", page_icon="📚")
st.title("📚 AI Study Assistant")
def get_api_key():
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.environ.get("GEMINI_API_KEY")

# Create the client and chat only once, and keep both alive
if "chat" not in st.session_state:
    st.session_state.client = genai.Client(api_key=get_api_key())
    st.session_state.chat = st.session_state.client.chats.create(
        model="gemini-flash-lite-latest",
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a friendly study assistant for a first-year "
                "college student. Explain things in simple words with "
                "small examples. Keep answers short. If the student "
                "shares notes, answer from the notes first."
            )
        ),
    )
    st.session_state.messages = []
    st.session_state.notes_text = ""
    st.session_state.notes_name = ""


def ask(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # If notes are uploaded, send them along with the question
    full_prompt = prompt
    if st.session_state.notes_text:
        full_prompt = (
            "Here are my notes:\n\n"
            + st.session_state.notes_text
            + "\n\nQuestion: "
            + prompt
        )

    with st.chat_message("assistant"):
        box = st.empty()
        full = ""
        for chunk in st.session_state.chat.send_message_stream(full_prompt):
            full += chunk.text or ""
            box.markdown(full)
    st.session_state.messages.append({"role": "assistant", "content": full})


# Show the earlier messages
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Sidebar with study tools
with st.sidebar:
    st.header("Study tools")

    topic = st.text_input("Topic")
    if st.button("Make a quiz") and topic:
        ask(f"Create a 5-question multiple choice quiz on {topic}. "
            "Do not show answers yet. Wait for my answers, then grade me.")
    if st.button("Make flashcards") and topic:
        ask(f"Make 5 flashcards on {topic}. Format each as Q: ... and A: ...")

    st.divider()
    notes_file = st.file_uploader("Upload notes (PDF or TXT)", type=["pdf", "txt"])
    if notes_file and notes_file.name != st.session_state.notes_name:
        if notes_file.name.endswith(".pdf"):
            reader = PdfReader(notes_file)
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
        else:
            text = notes_file.read().decode("utf-8")
        st.session_state.notes_text = text[:30000]
        st.session_state.notes_name = notes_file.name
        if not text.strip():
            st.warning("No text found. Scanned PDFs (photos of pages) don't work.")
        else:
            st.success(f"Loaded {notes_file.name}")

    if st.button("Summarize notes"):
        if st.session_state.notes_text:
            ask("Summarize my notes into 5 short bullet points.")
        else:
            st.warning("Upload a PDF or TXT file first.")

# Normal chat box
question = st.chat_input("Ask anything...")
if question:
    ask(question)