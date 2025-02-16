from openai import OpenAI
import os
import streamlit as st
from dotenv import load_dotenv

class LLMClient:
    def __init__(self):
        load_dotenv()
        self._validate_api_key()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self._test_connection()

    def _validate_api_key(self):
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key or not openai_api_key.startswith('sk-'):
            st.error("Invalid OpenAI API key configuration")
            st.stop()

    def _test_connection(self):
        try:
            self.client.models.list()
        except Exception as e:
            st.error(f"OpenAI connection failed: {str(e)}")
            st.stop()

    def generate_response(self, messages):
        try:
            return self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                stream=True,
            )
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            raise
