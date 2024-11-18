import streamlit as st
from groq_client import GroqAPI
from message import Message
from components import ModelSelector
from settings import INGREDIENTS

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
            selected_ingredients = st.multiselect("食材を選んでください", INGREDIENTS)

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