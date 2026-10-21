import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Study Assistant", page_icon="📚")
st.title("📚 AI Study Assistant")



# Create the client and chat only once, and keep both alive
if "chat" not in st.session_state:
    st.session_state.client = genai.Client()
    st.session_state.chat = st.session_state.client.chats.create(
        model="gemini-flash-lite-latest",
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a friendly study assistant for a first-year "
                "college student. Explain things in simple words with "
                "small examples. Keep answers short."
            )
        ),
    )
    st.session_state.messages = []

def ask(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        box = st.empty()
        full = ""
        for chunk in st.session_state.chat.send_message_stream(prompt):
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
    notes_file = st.file_uploader("Upload notes (.txt)", type="txt")
    if st.button("Summarize notes") and notes_file:
        notes = notes_file.read().decode("utf-8")
        ask(f"Summarize these notes into 5 short bullet points:\n\n{notes}")

# Normal chat box
question = st.chat_input("Ask anything...")
if question:
    ask(question)