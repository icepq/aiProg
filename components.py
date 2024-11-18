import streamlit as st
from settings import MODELS

class ModelSelector:
    def __init__(self):
        self.models = MODELS

    def select(self):
        with st.sidebar:
            st.sidebar.title("groq chat")
            return st.selectbox("", self.models)