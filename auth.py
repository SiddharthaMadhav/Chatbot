from streamlit_google_auth import Authenticate
import streamlit as st
import json
import os
import tempfile

class AuthManager:
    def __init__(self):

        credentials = {"web":{"client_id": st.secrets['client_id'],"project_id": st.secrets['project_id'],"auth_uri": st.secrets['auth_uri'],"token_uri": st.secrets['token_uri'],"auth_provider_x509_cert_url":st.secrets['auth_provider_x509_cert_url'],"client_secret": st.secrets['client_secret'],"redirect_uris": st.secrets['redirect_uris'],"javascript_origins":st.secrets['javascript_origins']}}

        temp_json_path = "./temp_credentials.json"
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as temp_file:
            json.dump(credentials, temp_file)
            temp_json_path = temp_file.name

        self.authenticator = Authenticate(
            secret_credentials_path = temp_json_path,
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
