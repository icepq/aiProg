import streamlit as st
from groq_client import GroqAPI
from message import Message
from settings import INGREDIENTS

# CSS
def load_css():
    with open("style.css", "r", encoding="utf-8") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css()


def main():
    # 初期化
    if "search_history" not in st.session_state:
        st.session_state.search_history = []

    # サイドバーに食材の選択肢とボタンを横並びに配置
    with st.sidebar:
        st.sidebar.title("食材を選んでください")

        # 食材を複数列で表示
        num_columns = 2
        columns = st.columns(num_columns)
        selected_ingredients = []

        for i, ingredient in enumerate(INGREDIENTS):
            col = columns[i % num_columns]
            # CSS
            if col.checkbox(ingredient, key=ingredient):
                selected_ingredients.append(ingredient)

        # 検索ボタン
        search_button = st.button("レシピを検索")

    message = Message()

    # 検索ボタンが押された場合にレシピを生成
    if search_button and selected_ingredients:
        llm = GroqAPI()
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