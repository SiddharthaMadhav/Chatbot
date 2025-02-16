from streamlit_google_auth import Authenticate
import streamlit as st

class AuthManager:
    def __init__(self):
        self.authenticator = Authenticate(
            secret_credentials_path='./Key2.json',
            cookie_name='my_cookie_name',
            cookie_key='this_is_secret',
            redirect_uri='http://localhost:8501',
        )

    def check_auth(self):
        self.authenticator.check_authentification()
        if not st.session_state.get('connected'):
            self.render_login_page()
            st.stop()
        return st.session_state['user_info']

    def render_login_page(self):
        st.header("Welcome to OpenAI Chatbot")
        st.header("Please sign in with your Google account to continue")
        self.authenticator.login()

    def logout(self):
        self.authenticator.logout()
        st.rerun()
