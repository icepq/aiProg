import streamlit as st
from groq_client import GroqAPI
from message import Message
from components import ModelSelector
from settings import INGREDIENTS

def main():
    # サイドバーに食材の選択肢を配置
    with st.sidebar:
        st.sidebar.title("食材を選んでください")
        selected_ingredients = st.multiselect("食材を選んでください", INGREDIENTS)

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