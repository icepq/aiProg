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
        """あなたは愉快なAIです。ユーザの入力に全て日本語で返答を生成してください.ユーザーから食材の入力が来ます、その食材を使った具体的なレシピを提示してください"""
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


class ModelSelector:
    def __init__(self):
        self.models = ["llama3-8b-8192", "llama3-70b-8192"]

    def select(self):
        with st.sidebar:
            # サイドバータイトルを削除
            return st.selectbox("モデルを選択してください:", self.models)


def main():
    # 初期化
    if "search_history" not in st.session_state:
        st.session_state.search_history = []

    # サイドバーに食材の選択肢とボタンを横並びに配置
    with st.sidebar:
        st.sidebar.title("食材を選んでください")
        
        # 横並びにするためのカラムを作成
        col1, col2 = st.columns([2, 1])
        
        with col1:
            ingredients = ["トマト", "チキン", "じゃがいも", "にんじん", "玉ねぎ", "ピーマン", "ほうれん草", "きのこ", "豆腐", "豚肉"]
            selected_ingredients = st.multiselect("食材を選んでください", ingredients)

        with col2:
            # 検索ボタンを横に配置
            search_button = st.button("レシピを検索")

    model = ModelSelector()
    selected_model = model.select()

    message = Message()

    # 検索ボタンが押された場合にレシピを生成
    if search_button and selected_ingredients:
        llm = GroqAPI(selected_model)
        selected_ingredients_str = ", ".join(selected_ingredients)

        # ユーザーの選択をメッセージに追加
        message.add("user", f"選択された食材: {selected_ingredients_str}")
        message.display_chat_history()

        # レシピを生成するためのメッセージを送信
        response = "".join(llm.response_stream(st.session_state.messages))
        message.add("assistant", response)

        # 履歴に保存
        st.session_state.search_history.append({
            "ingredients": selected_ingredients_str,
            "recipe": response
        })

        # レシピを表示
        st.write(f"### 選択された食材: {selected_ingredients_str}")
        st.write(f"#### レシピ:\n{response}")

    # 検索履歴をサイドバーに表示
    st.sidebar.write("検索履歴:")
    for idx, history in enumerate(st.session_state.search_history):
        if st.sidebar.button(history["ingredients"], key=f"history_{idx}"):
            st.write(f"### 選択された食材: {history['ingredients']}")
            st.write(f"#### レシピ:\n{history['recipe']}")

if __name__ == "__main__":
    main()
