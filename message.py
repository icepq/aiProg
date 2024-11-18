import streamlit as st
from settings import SYSTEM_PROMPT

class Message:
    def __init__(self):
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                }
            ]

    def add(self, role: str, content: str):
        st.session_state.messages.append({"role": role, "content": content})

    def display_chat_history(self):
        for message in st.session_state.messages:
            if message["role"] == "system":
                continue
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def display_stream(self, generater):
        # 結果を一度に表示するためのリストを作成
        result = ""
        for chunk in generater:
            result += chunk
        st.write(result)
        return result  # 戻り値を追加