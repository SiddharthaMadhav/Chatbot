from datetime import datetime
import streamlit as st

class SessionManager:
    def __init__(self, authenticator):
        self.authenticator = authenticator
        self.allowed_domains = ["example.com", "yourdomain.com"]

    def validate_session(self):
        self._check_activity_timeout()

    def _check_activity_timeout(self):
        if 'last_activity' not in st.session_state:
            st.session_state.last_activity = datetime.now()
        elif (datetime.now() - st.session_state.last_activity).seconds > 3600:
            self.authenticator.logout()
            st.error("Session expired. Please log in again.")
            st.rerun()

