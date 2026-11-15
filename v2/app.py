"""Version 2 - Reliable AI Escape Room (Streamlit UI)."""
import json
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
import engine, llm  # noqa: E402
from game_data import ROOM  # noqa: E402

st.set_page_config(page_title="AI Escape Room v2", page_icon="🔐")
st.title("🔐 The Locked Library (v2 - reliable)")


def reset():
    st.session_state.state = engine.new_state()
    st.session_state.chat = [("assistant", ROOM["intro"])]
    st.session_state.last = None


if "state" not in st.session_state:
    reset()
S = st.session_state

with st.sidebar:
    st.markdown("**How to play**: examine objects, take items, use items on objects, enter 4-digit codes. "
                "Type *hint* if stuck.")
    inv = ", ".join(i.replace("_", " ") for i in S.state["inventory"]) or "empty"
    st.markdown(f"**Inventory:** {inv}")
    if st.button("🔄 Restart game"):
        reset()
        st.rerun()
    if S.last:
        with st.expander("Debug: intent, result, state"):
            st.code(json.dumps(S.last, indent=2))

for role, msg in S.chat:
    with st.chat_message(role):
        st.write(msg)

if S.state["escaped"]:
    st.success("🎉 You escaped!")
    st.balloons()
elif text := st.chat_input("What do you do?"):
    intent = llm.parse_intent(text)                   # LLM: text -> intent
    result = engine.apply(S.state, intent)            # Python: validate + update state
    reply = llm.narrate(text, result)                 # LLM: facts -> prose
    S.chat += [("user", text), ("assistant", reply)]
    S.last = {"intent": intent, "result": result, "state": S.state}
    st.rerun()
