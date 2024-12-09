import streamlit as st
from groq_client import GroqAPI
from message import Message
from settings import VEGETABLES, MEATS, OTHERS, FISH, SYSTEM_PROMPT  # SYSTEM_PROMPT をインポート

def load_css():
    with open("style.css", "r", encoding="utf-8") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css()

def main():
    # 初期化
    if "search_history" not in st.session_state:
        st.session_state.search_history = []
    if "favorites" not in st.session_state:
        st.session_state.favorites = []
    if "selected_recipe" not in st.session_state:
        st.session_state.selected_recipe = None


    # サイドバーに食材の選択肢とボタンを横並びに配置
    with st.sidebar:
        st.sidebar.title("食材を選んでください")

        # カテゴリごとに食材を表示
        selected_ingredients = []

        with st.sidebar.expander("野菜"):
            for ingredient in VEGETABLES:
                if st.checkbox(ingredient, key=ingredient):
                    selected_ingredients.append(ingredient)

        with st.sidebar.expander("肉類"):
            for ingredient in MEATS:
                if st.checkbox(ingredient, key=ingredient):
                    selected_ingredients.append(ingredient)

        with st.sidebar.expander("魚類"):
            for ingredient in FISH:
                if st.checkbox(ingredient, key=ingredient):
                    selected_ingredients.append(ingredient)

        with st.sidebar.expander("その他"):
            for ingredient in OTHERS:
                if st.checkbox(ingredient, key=ingredient):
                    selected_ingredients.append(ingredient)

        # 検索ボタン
        search_button = st.button("レシピを検索")

    message = Message()

    # レシピ検索処理
    if search_button and selected_ingredients:
        llm = GroqAPI()
        selected_ingredients_str = ", ".join(selected_ingredients)

        try:
            # SYSTEM_PROMPT を使って日本語でレシピを生成するリクエストを送信
            initial_message = [{
                "role": "system", 
                "content": SYSTEM_PROMPT  # SYSTEM_PROMPT をここで使用
            }, {
                "role": "user", 
                "content": f"食材: {selected_ingredients_str}"  # ユーザーが選んだ食材を送信
            }]
            response = "".join(llm.response_stream(initial_message))

            # 検索履歴に追加
            st.session_state.search_history.insert(0, {
                "ingredients": selected_ingredients_str,
                "recipe": response
            })

        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
            return

    # 最新の結果のみを表示
    if st.session_state.search_history:
        latest_history = st.session_state.search_history[0]
        st.write(f"##### 選択された食材: {latest_history['ingredients']}")
        st.write(f"{latest_history['recipe']}")

        # お気に入りボタンをサイドバーに配置
        with st.sidebar:
            if st.button("お気に入りに追加", key="favorite_button"):
                st.session_state.favorites.append(latest_history)
                st.success("お気に入りに追加しました！")

   # サイドバーにお気に入りを表示
    with st.sidebar:
        st.write("お気に入り:")
        for idx, favorite in enumerate(st.session_state.favorites):
            if st.button(favorite["ingredients"], key=f"favorite_{idx}"):
                st.session_state.selected_recipe = favorite

    # サイドバーに検索履歴を表示（最新以外）
    st.sidebar.write("検索履歴:")
    for idx, history in enumerate(st.session_state.search_history[1:]):  # 最新は除外
        if st.sidebar.button(history["ingredients"], key=f"history_{idx}"):
            st.write(f"##### 選択された食材: {history['ingredients']}")
            st.write(f"{history['recipe']}")


    # メイン画面に選択されたレシピを表示
    if st.session_state.selected_recipe is not None:
        selected_recipe = st.session_state.selected_recipe
        st.write(f"##### 選択された食材: {selected_recipe['ingredients']}")
        st.write(f"{selected_recipe['recipe']}")

if __name__ == "__main__":
    main()