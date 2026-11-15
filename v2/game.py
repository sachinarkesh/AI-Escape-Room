"""Version 2 - Reliable AI Escape Room (Streamlit UI as a render() function)."""
import json
import os
import sys
import streamlit as st
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))  # so engine / llm / game_data import in any launch mode
load_dotenv()
import engine, llm  # noqa: E402
from game_data import ROOM  # noqa: E402


def reset():
    st.session_state.v2_state = engine.new_state()
    st.session_state.v2_chat = [("assistant", ROOM["intro"])]
    st.session_state.v2_last = None


def render():
    st.title("🔐 The Locked Library (v2 - reliable)")
    if "v2_state" not in st.session_state:
        reset()
    S = st.session_state

    with st.sidebar:
        st.markdown("**How to play**: examine objects, take items, use items on objects, enter 4-digit codes. "
                    "Type *hint* if stuck.")
        inv = ", ".join(i.replace("_", " ") for i in S.v2_state["inventory"]) or "empty"
        st.markdown(f"**Inventory:** {inv}")
        if st.button("🔄 Restart game", key="v2_restart"):
            reset()
            st.rerun()
        if S.v2_last:
            with st.expander("Debug: intent, result, state"):
                st.code(json.dumps(S.v2_last, indent=2))

    for role, msg in S.v2_chat:
        with st.chat_message(role):
            st.write(msg)

    if S.v2_state["escaped"]:
        st.success("🎉 You escaped!")
        st.balloons()
    elif text := st.chat_input("What do you do?", key="v2_input"):
        intent = llm.parse_intent(text)                   # LLM: text -> intent
        result = engine.apply(S.v2_state, intent)         # Python: validate + update state
        reply = llm.narrate(text, result)                 # LLM: facts -> prose
        S.v2_chat += [("user", text), ("assistant", reply)]
        S.v2_last = {"intent": intent, "result": result, "state": S.v2_state}
        st.rerun()
