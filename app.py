import streamlit as st
from brain import TobbyBrain

st.set_page_config(page_title="Tobby", page_icon="🤖", layout="centered")

st.markdown(
    """
    <style>
    .main { background-color: #0a0a0a; color: #ffffff; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🤖 Tobby")
st.caption("Your personal AI companion")

if "tobby" not in st.session_state:
    st.session_state.tobby = TobbyBrain()

if "messages" not in st.session_state:
    st.session_state.messages = []
    for turn in st.session_state.tobby.history:
        st.session_state.messages.append(
            {"role": "user", "content": turn["user"]})
        st.session_state.messages.append(
            {"role": "assistant", "content": turn["tobby"]})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Talk to Tobby...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Tobby is thinking..."):
            reply = st.session_state.tobby.get_response(user_input)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
