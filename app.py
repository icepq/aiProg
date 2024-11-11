import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv(Path(__file__).parent / ".env")


class GroqAPI:
    def __init__(self, model_name: str):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model_name = model_name

    def _response(self, message):
        return self.client.chat.completions.create(
            model=self.model_name,
            messages=message,
            temperature=0,
            max_tokens=4096,
            stream=True,
            stop=None,
        )

    def response_stream(self, message):
        for chunk in self._response(message):
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class Message:
    system_prompt: str = (
        """あなたは愉快なAIです。ユーザの入力に全て日本語で返答を生成してください.ユーザーから食材の入力が来ます、その食材を使った具体的なレシピを提示してください
"""
    )

    def __init__(self):
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "system",
                    "content": self.system_prompt,
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


class ModelSelector:
    def __init__(self):
        self.models = ["llama3-8b-8192", "llama3-70b-8192"]

    def select(self):
        with st.sidebar:
            st.sidebar.title("groq chat")
            return st.selectbox("", self.models)


def main():
    # サイドバーに食材の選択肢を配置
    with st.sidebar:
        st.sidebar.title("食材を選んでください")
        ingredients = ["トマト", "チキン", "じゃがいも", "にんじん", "玉ねぎ", "ピーマン", "ほうれん草", "きのこ", "豆腐", "豚肉"]
        selected_ingredients = st.multiselect("食材を選んでください", ingredients)

    model = ModelSelector()
    selected_model = model.select()

    message = Message()

    if selected_ingredients:
        llm = GroqAPI(selected_model)

        # ユーザーの選択をメッセージに追加
        selected_ingredients_str = ", ".join(selected_ingredients)
        message.add("user", f"選択された食材: {selected_ingredients_str}")
        message.display_chat_history()

        # レシピを生成するためのメッセージを送信
        response = message.display_stream(
            generater=llm.response_stream(st.session_state.messages)
        )
        message.add("assistant", response)

    # 検索履歴をセッションステートに保存
    if "search_history" not in st.session_state:
        st.session_state.search_history = []

    if selected_ingredients:
        st.session_state.search_history.append(selected_ingredients_str)

    # 検索履歴を表示
    st.sidebar.write("検索履歴:")
    for history in st.session_state.search_history:
        st.sidebar.write(history)

if __name__ == "__main__":
    main()