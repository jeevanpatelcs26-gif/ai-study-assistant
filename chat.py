from google import genai
from google.genai import types

client = genai.Client()

chat = client.chats.create(
    model="gemini-flash-latest",
    config=types.GenerateContentConfig(
        system_instruction=(
            "You are a friendly study assistant for a first-year "
            "college student. Explain things in simple words with "
            "small examples. Keep answers short."
        )
    ),
)


def ask(prompt):
    response = chat.send_message(prompt)
    print("\nAssistant:", response.text)


print("Study Assistant is ready!")
print("Commands: /quiz <topic>, /flashcards <topic>, /summarize, quit")
print("Or just type any question.")

while True:
    text = input("\nYou: ").strip()

    if text.lower() == "quit":
        break
    elif text.startswith("/quiz "):
        topic = text[len("/quiz "):]
        ask(
            f"Create a 5-question multiple choice quiz on {topic}. "
            "Do not show the answers yet. Wait for my answers, "
            "then grade me and explain any mistakes."
        )
    elif text.startswith("/flashcards "):
        topic = text[len("/flashcards "):]
        ask(f"Make 5 flashcards on {topic}. Format each as Q: ... and A: ...")
    elif text == "/summarize":
        try:
            with open("notes.txt", encoding="utf-8") as f:
                notes = f.read()
            ask(f"Summarize these notes into 5 short bullet points:\n\n{notes}")
        except FileNotFoundError:
            print("\nCreate a file called notes.txt in this folder first.")
    else:
        ask(text)