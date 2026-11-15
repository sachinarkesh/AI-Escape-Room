"""Version 1 - Interactive AI Escape Room.
The LLM is the Game Master AND the rule keeper: the whole room, the secret codes and the
rules live in one system prompt. Memory = the chat history we resend every turn.
"""
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

SYSTEM_PROMPT = """You are the Game Master of a text escape room called "The Locked Library".
The player woke up locked in a library. Stay in character, answer in 2-4 vivid sentences.

ROOM (only these five objects exist): desk, bookshelf, painting, locked drawer, door.
- Desk: has a small UV torch on it.
- Bookshelf: four books stick out: red=4, blue=1, green=7, gold=2.
- Locked drawer: 4-digit keypad. Code is 4172 (red, blue, green, gold). Inside: a brass key and a
  note saying "The exit code starts with 60".
- Painting: a sunset. Under the UV torch, hidden writing says "...ends with 58".
- Door: needs the brass key AND the 4-digit code 6058.

RULES: Do not reveal codes or solutions unless the player discovered them. Do not let the player
use things they have not collected. Do not invent new objects. Let the player examine, take,
use items and try codes. When the player opens the door with the correct key and code, end your
message with the exact token [ESCAPED]."""


def reset():
    st.session_state.v1_history = []  # list of {"role": "user"|"model", "text": str}
    st.session_state.v1_escaped = False


def ask_llm(history):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    contents = [types.Content(role=m["role"], parts=[types.Part(text=m["text"])]) for m in history]
    resp = client.models.generate_content(
        model=MODEL, contents=contents,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, temperature=0.8))
    return resp.text


def render():
    st.title("🔐 The Locked Library (v1)")
    S = st.session_state
    if "v1_history" not in S:
        reset()

    with st.sidebar:
        st.markdown("**How to play**\n\nYou wake up in a locked library. Type what you want to do "
                    "(e.g. *examine the bookshelf*, *take the torch*, *try 1234 on the drawer*). "
                    "Find the clues and escape through the door.")
        if st.button("🔄 Restart game", key="v1_restart"):
            reset()
            st.rerun()

    st.info("You wake up on a cold floor. A desk, a bookshelf, a painting, a locked drawer and a "
            "heavy door with a keypad surround you. How do you escape?")

    for m in S.v1_history:
        with st.chat_message("user" if m["role"] == "user" else "assistant"):
            st.write(m["text"].replace("[ESCAPED]", ""))

    if S.v1_escaped:
        st.success("🎉 You escaped!")
    elif text := st.chat_input("What do you do?", key="v1_input"):
        S.v1_history.append({"role": "user", "text": text})
        try:
            reply = ask_llm(S.v1_history)
        except Exception as e:
            reply = f"(Game Master error: {e})"
        S.v1_history.append({"role": "model", "text": reply})
        S.v1_escaped = "[ESCAPED]" in reply
        st.rerun()
