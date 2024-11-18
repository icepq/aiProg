import streamlit as st
from settings import MODELS

class ModelSelector:
    def __init__(self):
        self.models = MODELS

    def select(self):
        with st.sidebar:
            return st.selectbox("モデルを選択してください:", self.models)